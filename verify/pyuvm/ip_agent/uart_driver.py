"""UART IP driver — drives RX serial line to send data into the DUT."""

import random

import cocotb
from cocotb.triggers import Timer, ClockCycles, FallingEdge, RisingEdge, First
from pyuvm import uvm_driver, ConfigDB

from ip_item.uart_item import uart_item


class uart_driver(uvm_driver):
    def build_phase(self):
        super().build_phase()
        self.dut = ConfigDB().get(self, "", "DUT")
        self.regs = ConfigDB().get(None, "", "bus_regs")
        try:
            self.insert_glitches = ConfigDB().get(self, "", "insert_glitches")
        except Exception:
            self.insert_glitches = False

    async def run_phase(self):
        self.dut.RX.value = 1
        while True:
            item = await self.seq_item_port.get_next_item()
            if item.direction == uart_item.RX:
                self.logger.info(f"Driving RX: {item.convert2string()}")
                send_thread = cocotb.start_soon(self._send_item_rx(item))
                reset_thread = cocotb.start_soon(self._wait_reset())
                await First(send_thread, reset_thread)
                self.dut.RX.value = 1
                reset_thread.kill()
                send_thread.kill()
            self.seq_item_port.item_done()

    async def _wait_reset(self):
        await FallingEdge(self.dut.RESETn)

    async def _send_item_rx(self, tr):
        self._num_cyc_bit = self._get_bit_n_cyc()
        self._word_length = self._get_n_bits()

        # Start bit
        self.dut.RX.value = 0
        await ClockCycles(self.dut.CLK, self._num_cyc_bit)

        if self.insert_glitches:
            cocotb.start_soon(self._add_glitches())

        # Data bits (LSB first)
        for i in range(self._word_length):
            self.dut.RX.value = (tr.char >> i) & 1
            await ClockCycles(self.dut.CLK, self._num_cyc_bit)

        # Parity bit
        parity_type = (self.regs.read_reg_value("CFG") >> 5) & 0x7
        tr.calculate_parity(parity_type)
        if tr.parity != "None":
            self.dut.RX.value = int(tr.parity)
            await ClockCycles(self.dut.CLK, self._num_cyc_bit)

        # Extra stop bit (if 2 stop bits configured)
        if (self.regs.read_reg_value("CFG") >> 4) & 0x1:
            self.dut.RX.value = 1
            await ClockCycles(self.dut.CLK, self._num_cyc_bit)

        # Stop bit
        self.dut.RX.value = 1
        await ClockCycles(self.dut.CLK, self._num_cyc_bit)
        await ClockCycles(self.dut.CLK, self._num_cyc_bit)

    def _get_bit_n_cyc(self):
        prescale = self.regs.read_reg_value("PR")
        return (prescale + 1) * 8

    def _get_n_bits(self):
        return self.regs.read_reg_value("CFG") & 0xF

    async def _add_glitches(self):
        await ClockCycles(
            self.dut.CLK,
            random.randint(self._num_cyc_bit, self._num_cyc_bit * 7),
        )
        await Timer(random.randint(1, 100), unit="ns")
        try:
            old_val = int(self.dut.RX.value)
        except Exception:
            old_val = 1
        self.dut.RX.value = 1 - old_val
        await Timer(random.randint(1, 10), unit="ns")
        self.dut.RX.value = old_val
