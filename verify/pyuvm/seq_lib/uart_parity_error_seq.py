"""UART parity error sequence — sends frames with wrong parity to trigger errors."""

import cocotb
from cocotb.triggers import ClockCycles
from pyuvm import uvm_sequence, ConfigDB

from cf_verify.bus_env.bus_seq_lib import reset_seq
from seq_lib.uart_config import uart_config


class uart_parity_error_seq(uvm_sequence):
    """Drives the RX line directly to inject parity errors."""

    async def body(self):
        await reset_seq("rst").start(self.sequencer)
        regs = ConfigDB().get(None, "", "bus_regs")
        addr = regs.reg_name_to_address
        dut = ConfigDB().get(None, "", "DUT")

        # Configure UART with odd parity
        from cf_verify.bus_env.bus_seq_lib import write_reg_seq
        if "GCLK" in addr:
            await write_reg_seq("gclk", addr["GCLK"], 1).start(self.sequencer)
        await write_reg_seq("ctrl_off", addr["CTRL"], 0).start(self.sequencer)
        await write_reg_seq("pr", addr["PR"], 2).start(self.sequencer)
        cfg = 8 | (1 << 5) | (0x3F << 8)  # 8 bit, odd parity
        await write_reg_seq("cfg", addr["CFG"], cfg).start(self.sequencer)
        await write_reg_seq("im", addr["IM"], 0x3FF).start(self.sequencer)
        await write_reg_seq("ctrl_on", addr["CTRL"], 0x07).start(self.sequencer)

        bit_n_cyc = (2 + 1) * 8
        test_char = 0x55  # 4 ones -> odd parity should be 0

        for _ in range(3):
            # Start bit
            dut.RX.value = 0
            await ClockCycles(dut.CLK, bit_n_cyc)

            # 8 data bits
            for i in range(8):
                dut.RX.value = (test_char >> i) & 1
                await ClockCycles(dut.CLK, bit_n_cyc)

            # Wrong parity bit: 0x55 has 4 ones; odd parity bit should be 1, send 0
            dut.RX.value = 0
            await ClockCycles(dut.CLK, bit_n_cyc)

            # Stop bit
            dut.RX.value = 1
            await ClockCycles(dut.CLK, bit_n_cyc)
            await ClockCycles(dut.CLK, bit_n_cyc * 2)

        # Check parity error flag
        from cf_verify.bus_env.bus_seq_lib import read_reg_seq
        rd = read_reg_seq("ris_pe", addr["RIS"])
        await rd.start(self.sequencer)
        ris = rd.result
        assert ((ris >> 7) & 1) == 1, f"Parity error flag not set in RIS (0x{ris:03x})"
