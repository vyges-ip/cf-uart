"""UART match sequence — verifies data match interrupt fires on match."""

import os

from pyuvm import uvm_sequence, ConfigDB

from cf_verify.bus_env.bus_seq_lib import write_reg_seq, read_reg_seq, reset_seq
from seq_lib.uart_config import uart_config
from ip_item.uart_item import uart_item


class uart_match_seq(uvm_sequence):
    async def body(self):
        await reset_seq("rst").start(self.sequencer)
        regs = ConfigDB().get(None, "", "bus_regs")
        addr = regs.reg_name_to_address
        match_b = 5

        match_char = 0x55

        async def read_reg(name):
            rd = read_reg_seq(f"rd_{name.lower()}", addr[name])
            await rd.start(self.sequencer)
            return rd.result

        config = uart_config(
            "config",
            im=0x3FF,
            match=match_char,
            prescaler=2,
            config=9 | (0x3F << 8),
        )
        await config.start(self.sequencer)

        # Send the matching character via loopback
        ctrl_loopback = 0x0F
        await write_reg_seq("ctrl_lb", addr["CTRL"], ctrl_loopback).start(self.sequencer)

        # Send non-matching first
        await write_reg_seq("tx_no_match", addr["TXDATA"], 0xAA).start(self.sequencer)
        # Then send matching
        await write_reg_seq("tx_match", addr["TXDATA"], match_char).start(self.sequencer)

        # Wait and check RIS for match flag
        from cocotb.triggers import ClockCycles
        dut = ConfigDB().get(None, "", "DUT")
        bit_n_cyc = (2 + 1) * 8
        frame_cyc = bit_n_cyc * (1 + 9 + 1 + 1) * 3
        for _ in range(5000):
            await ClockCycles(dut.CLK, max(1, frame_cyc // 100))
            ris = await read_reg("RIS")
            if (ris >> match_b) & 1:
                break
        else:
            await ClockCycles(dut.CLK, frame_cyc * 2)
        ris = await read_reg("RIS")
        assert int(ris) & (1 << match_b), f"MATCH flag not set in RIS (0x{int(ris):03x})"

        if os.environ.get("SIM", "").lower() == "verilator":
            await ClockCycles(dut.CLK, frame_cyc * 2)

        # Read back RX data
        rx0 = await read_reg("RXDATA")
        rx1 = await read_reg("RXDATA")
        assert (rx0 & 0x1FF) == 0x0AA, f"First loopback RX data mismatch: 0x{rx0:03x}"
        assert (rx1 & 0x1FF) == match_char, (
            f"Match RX data mismatch: expected 0x{match_char:03x}, got 0x{rx1:03x}"
        )
