"""Test library for CF_UART verification — 14 tests covering full UART functionality."""

import os
from pathlib import Path

import cocotb
import pyuvm
from pyuvm import uvm_root, ConfigDB

from cocotb.triggers import Event
from cocotb_coverage.coverage import coverage_db

from cf_verify.base.base_test import base_test
from cf_verify.base.top_env import top_env
from cf_verify.bus_env.bus_regs import BusRegs
from cf_verify.bus_env.bus_seq_lib import write_read_regs_seq, reset_seq
from cf_verify.bus_env.bus_seq_lib import write_reg_seq, read_reg_seq
from cf_verify.ip_env.ip_agent import ip_agent
from cf_verify.ip_env.ip_driver import ip_driver
from cf_verify.ip_env.ip_monitor import ip_monitor
from cf_verify.ip_env.ip_coverage import ip_coverage
from cf_verify.base.ref_model import ref_model

from ip_agent.uart_driver import uart_driver
from ip_agent.uart_monitor import uart_monitor
from ref_model.ref_model import UART_VIP
from ip_coverage.uart_coverage import uart_coverage
from ip_scoreboard import uart_scoreboard


class uart_env(top_env):
    """UART-specific top environment with proper component wiring."""

    def build_phase(self):
        from cf_verify.bus_env.bus_agent import bus_agent
        from cf_verify.ip_env.ip_logger import ip_logger

        self.bus_agent = bus_agent("bus_agent", self)
        self.ip_agent = uart_ip_agent("ip_agent", self)
        self.ref_model = UART_VIP("ref_model", self)
        self.scoreboard = uart_scoreboard("scoreboard", self)
        self.ip_coverage = uart_coverage("ip_coverage", self)
        self.ip_logger = ip_logger("ip_logger", self)

    def connect_phase(self):
        super().connect_phase()
        self.ip_agent.monitor.irq_ap.connect(self.ref_model.irq_analysis_export)
        self.ip_agent.monitor.irq_ap.connect(self.scoreboard.irq_dut_export)
        self.bus_agent.monitor.ap.connect(self.ip_coverage.analysis_export)


class uart_ip_agent(ip_agent):
    driver_cls = uart_driver
    monitor_cls = uart_monitor


class uart_base_test(base_test):
    """Base test for CF_UART — wires up the UART environment."""

    def build_phase(self):
        import os
        import cocotb

        dut = cocotb.top
        bus_type = os.environ.get("BUS_TYPE", "APB")
        yaml_file = os.environ.get(
            "YAML_FILE",
            str(Path(__file__).resolve().parent.parent.parent / "CF_UART.yaml"),
        )
        test_path = os.environ.get("TEST_PATH", "./sim")

        regs = BusRegs(yaml_file)

        ConfigDB().set(None, "*", "DUT", dut)
        ConfigDB().set(None, "*", "BUS_TYPE", bus_type)
        ConfigDB().set(None, "*", "bus_regs", regs)
        ConfigDB().set(None, "*", "irq_exist", regs.get_irq_exist())
        ConfigDB().set(None, "*", "collect_coverage", True)
        ConfigDB().set(None, "*", "disable_logger", False)
        ConfigDB().set(None, "*", "TEST_PATH", test_path)

        self.env = uart_env("env", self)
        super().build_phase()


# ──────────────────────────────────────────
#  7 EXISTING TESTS (ported from uvm-python)
# ──────────────────────────────────────────

@pyuvm.test()
class WriteReadRegsTest(uart_base_test):
    """Write/read all accessible registers."""

    async def run_phase(self):
        self.raise_objection()
        # Keep existing auto sequence for broad access stimulation.
        seq = write_read_regs_seq("write_read_regs")
        await seq.start(self.env.bus_agent.sequencer)

        # Add strict local assertions so this test can never pass on log-only mismatches.
        regs = ConfigDB().get(None, "", "bus_regs")
        addr = regs.reg_name_to_address
        for reg in regs.get_writable_regs():
            if reg.name in ("IC", "GCLK") or reg.name.endswith("_FLUSH"):
                continue
            wr_val = (
                0xA5 if reg.size <= 8
                else 0xA5A5 if reg.size <= 16
                else 0xDEAD_BEEF
            ) & ((1 << reg.size) - 1)
            await write_reg_seq("wr_chk", addr[reg.name], wr_val).start(self.env.bus_agent.sequencer)
            rd = read_reg_seq("rd_chk", addr[reg.name])
            await rd.start(self.env.bus_agent.sequencer)
            rd_val = rd.result & ((1 << reg.size) - 1)
            assert rd_val == wr_val, (
                f"WriteReadRegsTest mismatch on {reg.name}: "
                f"wrote 0x{wr_val:x}, read 0x{rd_val:x}"
            )
        self.drop_objection()


@pyuvm.test()
class TX_StressTest(uart_base_test):
    """TX stress — sends many characters through the TX path."""

    async def run_phase(self):
        self.raise_objection()
        from seq_lib.uart_tx_seq import uart_tx_seq
        from cocotb.triggers import ClockCycles
        seq = uart_tx_seq("tx_stress")
        seq.monitor = self.env.ip_agent.monitor
        await seq.start(self.env.bus_agent.sequencer)
        regs = ConfigDB().get(None, "", "bus_regs")
        dut = ConfigDB().get(self, "", "DUT")
        pr = regs.read_reg_value("PR")
        bit_cyc = (pr + 1) * 8
        await ClockCycles(dut.CLK, bit_cyc * 14 * 6)
        self.drop_objection()


@pyuvm.test()
class RX_StressTest(uart_base_test):
    """RX stress — sends many characters through the RX path, reads back RXDATA."""

    async def run_phase(self):
        self.raise_objection()
        from seq_lib.uart_config import uart_config
        from cocotb.triggers import ClockCycles
        from cf_verify.bus_env.bus_seq_lib import read_reg_seq
        config = uart_config("config")
        await config.start(self.env.bus_agent.sequencer)

        from seq_lib.uart_rx_seq import uart_rx_seq
        seq = uart_rx_seq("rx_stress")
        await seq.start(self.env.ip_agent.sequencer)
        dut = ConfigDB().get(self, "", "DUT")
        regs = ConfigDB().get(None, "", "bus_regs")
        pr = regs.read_reg_value("PR")
        bit_cyc = (pr + 1) * 8
        await ClockCycles(dut.CLK, bit_cyc * 14 * 8)

        addr = regs.reg_name_to_address
        rx_count = 0
        for _ in range(6):
            rd = read_reg_seq("rx_rd", addr["RXDATA"])
            await rd.start(self.env.bus_agent.sequencer)
            if rd.result is not None:
                rx_count += 1
        self.logger.info(f"RX stress: read back {rx_count} chars from RXDATA")
        self.drop_objection()


@pyuvm.test()
class LoopbackTest(uart_base_test):
    """Loopback — sends data through TX, reads back through RX."""

    async def run_phase(self):
        self.raise_objection()
        from seq_lib.uart_loopback_seq import uart_loopback_seq
        from cocotb.triggers import ClockCycles
        seq = uart_loopback_seq("loopback")
        seq.monitor = self.env.ip_agent.monitor
        await seq.start(self.env.bus_agent.sequencer)
        dut = ConfigDB().get(self, "", "DUT")
        regs = ConfigDB().get(None, "", "bus_regs")
        pr = regs.read_reg_value("PR")
        bit_cyc = (pr + 1) * 8
        await ClockCycles(dut.CLK, bit_cyc * 14 * 3)
        self.drop_objection()


@pyuvm.test()
class PrescalarStressTest(uart_base_test):
    """Prescaler sweep — tests UART at different baud rates."""

    async def run_phase(self):
        self.raise_objection()
        from seq_lib.uart_prescalar_seq import (
            uart_prescalar_seq,
            uart_prescalar_seq_wrapper,
        )
        handshake = Event()

        bus_seq = uart_prescalar_seq_wrapper(handshake, "pr_bus")
        bus_seq.monitor = self.env.ip_agent.monitor
        ip_seq = uart_prescalar_seq(handshake, "pr_ip")

        cocotb.start_soon(ip_seq.start(self.env.ip_agent.sequencer))
        await bus_seq.start(self.env.bus_agent.sequencer)
        self.drop_objection()


@pyuvm.test()
class LengthParityTXStressTest(uart_base_test):
    """TX length/parity sweep — tests all word lengths x parity types for TX."""

    async def run_phase(self):
        self.raise_objection()
        from seq_lib.tx_length_parity_seq import tx_length_parity_seq
        from cocotb.triggers import ClockCycles
        seq = tx_length_parity_seq("lp_tx")
        seq.monitor = self.env.ip_agent.monitor
        await seq.start(self.env.bus_agent.sequencer)
        dut = ConfigDB().get(self, "", "DUT")
        regs = ConfigDB().get(None, "", "bus_regs")
        pr = regs.read_reg_value("PR")
        bit_cyc = (pr + 1) * 8
        await ClockCycles(dut.CLK, bit_cyc * 14 * 3)
        self.drop_objection()


@pyuvm.test()
class LengthParityRXStressTest(uart_base_test):
    """RX length/parity sweep — tests all word lengths x parity types for RX."""

    async def run_phase(self):
        self.raise_objection()
        from seq_lib.rx_length_parity_seq import (
            rx_length_parity_seq,
            rx_length_parity_seq_wrapper,
        )
        handshake = Event()

        bus_seq = rx_length_parity_seq_wrapper(handshake, "rx_lp_bus")
        ip_seq = rx_length_parity_seq(handshake, "rx_lp_ip")

        cocotb.start_soon(ip_seq.start(self.env.ip_agent.sequencer))
        await bus_seq.start(self.env.bus_agent.sequencer)
        self.drop_objection()


# ──────────────────────────────────
#  7 NEW TESTS (coverage closure)
# ──────────────────────────────────

@pyuvm.test()
class InterruptTest(uart_base_test):
    """Interrupt — verifies all interrupt sources fire and clear correctly."""

    async def run_phase(self):
        self.raise_objection()
        from seq_lib.uart_interrupt_seq import uart_interrupt_seq
        seq = uart_interrupt_seq("irq_test")
        await seq.start(self.env.bus_agent.sequencer)
        self.drop_objection()


@pyuvm.test()
class FIFOEdgeTest(uart_base_test):
    """FIFO edge — verifies FIFO full, empty, threshold, and overrun."""

    async def run_phase(self):
        self.raise_objection()
        from seq_lib.uart_fifo_seq import uart_fifo_seq
        seq = uart_fifo_seq("fifo_test")
        await seq.start(self.env.bus_agent.sequencer)
        self.drop_objection()


@pyuvm.test()
class TimeoutTest(uart_base_test):
    """Timeout — verifies RX timeout interrupt triggers after idle period."""

    async def run_phase(self):
        self.raise_objection()
        from seq_lib.uart_timeout_seq import uart_timeout_seq
        seq = uart_timeout_seq("timeout_test")
        await seq.start(self.env.bus_agent.sequencer)
        self.drop_objection()


@pyuvm.test()
class MatchDataTest(uart_base_test):
    """Match — verifies the data match interrupt fires on match."""

    async def run_phase(self):
        self.raise_objection()
        from seq_lib.uart_match_seq import uart_match_seq
        seq = uart_match_seq("match_test")
        await seq.start(self.env.bus_agent.sequencer)
        self.drop_objection()


@pyuvm.test()
class GlitchFilterTest(uart_base_test):
    """Glitch filter — verifies glitch filtering on the RX line."""

    async def run_phase(self):
        self.raise_objection()
        from seq_lib.uart_glitch_filter_seq import uart_glitch_filter_seq
        from seq_lib.uart_config import uart_config
        from cf_verify.bus_env.bus_seq_lib import read_reg_seq
        ConfigDB().set(None, "*", "insert_glitches", True)
        config = uart_config("config", control=0x17, prescaler=1)
        await config.start(self.env.bus_agent.sequencer)
        seq = uart_glitch_filter_seq("glitch_test")
        await seq.start(self.env.ip_agent.sequencer)

        regs = ConfigDB().get(None, "", "bus_regs")
        addr = regs.reg_name_to_address
        if "RX_FIFO_LEVEL" in addr:
            rd = read_reg_seq("rx_lvl", addr["RX_FIFO_LEVEL"])
            await rd.start(self.env.bus_agent.sequencer)
            assert rd.result > 0, (
                "GlitchFilterTest observed no RX captures after glitch-injected traffic"
            )
        self.drop_objection()


@pyuvm.test()
class FrameErrorTest(uart_base_test):
    """Frame error — verifies frame error detection on corrupted stop bits."""

    async def run_phase(self):
        self.raise_objection()
        from seq_lib.uart_frame_error_seq import uart_frame_error_seq
        seq = uart_frame_error_seq("frame_err_test")
        await seq.start(self.env.bus_agent.sequencer)
        self.drop_objection()


@pyuvm.test()
class ParityErrorTest(uart_base_test):
    """Parity error — verifies parity error detection on corrupted parity bits."""

    async def run_phase(self):
        self.raise_objection()
        from seq_lib.uart_parity_error_seq import uart_parity_error_seq
        seq = uart_parity_error_seq("parity_err_test")
        await seq.start(self.env.bus_agent.sequencer)
        self.drop_objection()


@pyuvm.test()
class CoverageClosureTest(uart_base_test):
    """Coverage closure — systematically hits all remaining coverage bins."""

    async def run_phase(self):
        self.raise_objection()
        from seq_lib.coverage_closure_seq import coverage_closure_seq
        seq = coverage_closure_seq("cov_closure")
        await seq.start(self.env.bus_agent.sequencer)
        self.drop_objection()


