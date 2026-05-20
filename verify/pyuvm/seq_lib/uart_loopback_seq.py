"""UART loopback sequence — enables loopback, sends TX data, reads RX data."""

import os
import random

from pyuvm import uvm_sequence, ConfigDB

from cf_verify.bus_env.bus_seq_lib import write_reg_seq, read_reg_seq, reset_seq
from seq_lib.uart_config import uart_config


class uart_loopback_seq(uvm_sequence):
    def __init__(self, name="uart_loopback_seq"):
        super().__init__(name)
        self.monitor = None

    async def body(self):
        await reset_seq("rst").start(self.sequencer)
        regs = ConfigDB().get(None, "", "bus_regs")
        addr = regs.reg_name_to_address

        config = uart_config("config", config=8 | (0 << 4) | (0 << 5) | (0x1F << 8))
        await config.start(self.sequencer)

        # Enable loopback (en + txen + rxen + lpen [+ gfen])
        ctrl = 0x1F if config.is_glitch_filter_en else 0x0F
        await write_reg_seq("lpbk", addr["CTRL"], ctrl).start(self.sequencer)

        dut = ConfigDB().get(None, "", "DUT")
        dut.RX.value = 1  # ensure RX idle in case a prior test left it driven

        pr = regs.read_reg_value("PR") or 1
        bit_cyc = (pr + 1) * 16

        from cocotb.triggers import ClockCycles

        # Drain any stale data in the RX FIFO from prior test state
        await ClockCycles(dut.CLK, bit_cyc * 2)
        for _ in range(16):
            rd = read_reg_seq("flush", addr["RXDATA"])
            await rd.start(self.sequencer)

        for _ in range(3):
            n_send = random.randint(1, 3)
            sent_data = []
            for _ in range(n_send):
                data = random.randint(0, 0xFF)
                sent_data.append(data)
                await write_reg_seq("tx_wr", addr["TXDATA"], data).start(self.sequencer)

            vlt = os.environ.get("SIM", "").lower() == "verilator"
            if vlt:
                await ClockCycles(
                    dut.CLK, bit_cyc * 12 * n_send * 48 + 20_000
                )
            elif "RX_FIFO_LEVEL" in addr:
                for _ in range(500_000):
                    await ClockCycles(dut.CLK, 2)
                    rdl = read_reg_seq("rxlvl", addr["RX_FIFO_LEVEL"])
                    await rdl.start(self.sequencer)
                    if int(rdl.result) & 0xF >= n_send:
                        break
            else:
                await ClockCycles(dut.CLK, bit_cyc * 12 * n_send + 2000)

            for expected in sent_data:
                rd = read_reg_seq("rx_rd", addr["RXDATA"])
                await rd.start(self.sequencer)
                rx_val = rd.result & 0xFF
                assert rx_val == expected, (
                    f"UART loopback MISMATCH: sent 0x{expected:02x}, "
                    f"received 0x{rx_val:02x}"
                )
