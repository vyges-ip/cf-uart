"""UART timeout sequence — verifies RX timeout interrupt after idle period."""

import cocotb
from cocotb.triggers import ClockCycles
from pyuvm import uvm_sequence, ConfigDB

from cf_verify.bus_env.bus_seq_lib import write_reg_seq, read_reg_seq, reset_seq
from seq_lib.uart_config import uart_config


class uart_timeout_seq(uvm_sequence):
    async def body(self):
        await reset_seq("rst").start(self.sequencer)
        regs = ConfigDB().get(None, "", "bus_regs")
        addr = regs.reg_name_to_address
        dut = ConfigDB().get(None, "", "DUT")
        rto_b = 9

        async def read_reg(name):
            rd = read_reg_seq(f"rd_{name.lower()}", addr[name])
            await rd.start(self.sequencer)
            return rd.result

        # Configure with short timeout (timeout=3 bit times)
        timeout_val = 3
        wlen = 8
        cfg = wlen | (timeout_val << 8)
        config = uart_config("config", config=cfg, im=0x3FF, prescaler=2)
        await config.start(self.sequencer)

        # Wait for timeout to expire (idle on RX line)
        bit_n_cyc = (2 + 1) * 8
        total_wait = (timeout_val + 1) * bit_n_cyc * 2
        await ClockCycles(dut.CLK, total_wait)

        # Check that timeout flag is set
        ris = await read_reg("RIS")
        mis = await read_reg("MIS")
        assert ((ris >> rto_b) & 1) == 1, f"RTO flag not set in RIS (0x{ris:03x})"
        assert ((mis >> rto_b) & 1) == 1, f"RTO flag not set in MIS (0x{mis:03x})"

        # Clear timeout interrupt
        await write_reg_seq("ic_timeout", addr["IC"], 1 << 9).start(self.sequencer)
        ris_cleared = await read_reg("RIS")
        assert ((ris_cleared >> rto_b) & 1) == 0, (
            f"RTO flag not cleared in RIS after IC write (0x{ris_cleared:03x})"
        )
