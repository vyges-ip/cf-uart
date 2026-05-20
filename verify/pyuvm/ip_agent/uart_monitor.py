"""UART IP monitor — observes TX and RX lines, decodes frames."""

import math

import cocotb
from cocotb.triggers import (
    Timer, ClockCycles, FallingEdge, RisingEdge, First, Combine,
)
from cocotb.utils import get_sim_time
from pyuvm import uvm_monitor, uvm_analysis_port, ConfigDB

from ip_item.uart_item import uart_item
from ip_item.uart_interrupt import uart_interrupt


class uart_monitor(uvm_monitor):
    def build_phase(self):
        super().build_phase()
        self.ap = uvm_analysis_port("ap", self)
        self.irq_ap = uvm_analysis_port("irq_ap", self)
        self.dut = ConfigDB().get(self, "", "DUT")
        self.regs = ConfigDB().get(None, "", "bus_regs")
        self.tx_received = cocotb.triggers.Event()
        self.rx_received = cocotb.triggers.Event()
        self.clk_period = 20  # default, updated in run_phase

    async def run_phase(self):
        cocotb.start_soon(self._sample_tx())
        cocotb.start_soon(self._sample_rx())
        cocotb.start_soon(self._watch_rx_timeout())
        cocotb.start_soon(self._watch_line_break())
        await self._get_clk_period()

    async def _get_clk_period(self):
        await RisingEdge(self.dut.CLK)
        await RisingEdge(self.dut.CLK)
        t0 = get_sim_time(unit="ns")
        await RisingEdge(self.dut.CLK)
        t1 = get_sim_time(unit="ns")
        self.clk_period = t1 - t0

    async def _sample_tx(self):
        while True:
            char, parity, wlen = await self._get_char(uart_item.TX)
            if char == "None":
                continue
            tr = uart_item("tx_tr")
            tr.char = char
            tr.parity = parity
            tr.word_length = wlen
            tr.direction = uart_item.TX
            self.ap.write(tr)
            self.tx_received.set()

    async def _sample_rx(self):
        while True:
            char, parity, wlen = await self._get_char(uart_item.RX)
            if char == "None":
                continue
            tr = uart_item("rx_tr")
            tr.char = char
            tr.parity = parity
            tr.word_length = wlen
            tr.direction = uart_item.RX
            self.ap.write(tr)
            self.rx_received.set()
            self._check_parity(char, parity)

    async def _get_char(self, direction):
        if direction == uart_item.TX:
            ncyc, wlen = await self._start_of_frame(self.dut.TX)
            signal = self.dut.TX
            done_signal = self.dut.tx_done
        else:
            ncyc, wlen = await self._start_of_frame(self.dut.RX)
            signal = self.dut.RX
            done_signal = self.dut.rx_done

        char_str = ""
        parity = "None"

        # Data bits
        for i in range(wlen):
            bit = await self._glitch_free_sample(signal, ncyc, 8)
            char_str = bit + char_str

        # Parity
        if self._is_parity_exists():
            parity = await self._glitch_free_sample(signal, ncyc, 8)

        # Stop bit(s)
        stop = await self._glitch_free_sample(
            signal, ncyc, 8, last_bit=not self._is_two_stop_bits()
        )
        if stop != "1":
            if direction == uart_item.RX:
                self._frame_error()
                return "None", "None", "None"

        if self._is_two_stop_bits():
            stop2 = await self._glitch_free_sample(signal, ncyc, 8, last_bit=True)
            if stop2 != "1":
                if direction == uart_item.RX:
                    self._frame_error()
                    return "None", "None", "None"

        # For TX, wait for tx_done
        if direction == uart_item.TX:
            while True:
                await RisingEdge(done_signal)
                await Timer(1, "ns")
                if done_signal.value == 1:
                    await FallingEdge(done_signal)
                    await Timer(1, "ns")
                    break

        if "X" in char_str:
            return "None", "None", "None"
        return int(char_str, 2), parity, wlen

    async def _start_of_frame(self, signal):
        while True:
            await FallingEdge(signal)
            ncyc = self._get_bit_n_cyc()
            wlen = self._get_n_bits()
            await Timer(1, unit="ns")
            try:
                if signal.value == 1:
                    continue
            except Exception:
                continue
            await ClockCycles(self.dut.CLK, ncyc)
            break
        return ncyc, wlen

    def _get_bit_n_cyc(self):
        prescale = self.regs.read_reg_value("PR")
        return (prescale + 1) * 8

    def _get_n_bits(self):
        return self.regs.read_reg_value("CFG") & 0xF

    def _is_parity_exists(self):
        return ((self.regs.read_reg_value("CFG") >> 5) & 0x7) != 0

    def _is_two_stop_bits(self):
        return bool((self.regs.read_reg_value("CFG") >> 4) & 0x1)

    async def _watch_rx_timeout(self):
        while True:
            if not (self.regs.read_reg_value("CTRL") & 1):
                await ClockCycles(self.dut.CLK, 1)
                continue
            timeout_bits = 1 + ((self.regs.read_reg_value("CFG") >> 8) & 0x3F)
            bit_rate = self._get_bit_n_cyc() * self.clk_period
            total_ns = int(timeout_bits * bit_rate)
            timeout_trigger = Timer(total_ns, "ns")
            rx_trigger = self.rx_received.wait()
            await First(timeout_trigger, rx_trigger)
            if self.rx_received.is_set():
                self.rx_received.clear()
            else:
                irq = uart_interrupt("timeout_irq")
                irq.rx_timeout = 1
                self.irq_ap.write(irq)

    async def _watch_line_break(self):
        while True:
            await FallingEdge(self.dut.RX)
            ncyc = self._get_bit_n_cyc()
            await ClockCycles(self.dut.CLK, math.floor(ncyc / 2))
            is_break = True
            for _ in range(11):
                await ClockCycles(self.dut.CLK, ncyc)
                try:
                    if self.dut.RX.value == 1:
                        is_break = False
                        break
                except Exception:
                    is_break = False
                    break
            if is_break:
                irq = uart_interrupt("break_irq")
                irq.rx_break_line = 1
                self.irq_ap.write(irq)

    def _check_parity(self, char, parity):
        tr = uart_item("parity_check")
        tr.char = char
        parity_type = (self.regs.read_reg_value("CFG") >> 5) & 0x7
        tr.calculate_parity(parity_type)
        if tr.parity != parity:
            irq = uart_interrupt("parity_irq")
            irq.rx_wrong_parity = 1
            self.irq_ap.write(irq)

    def _frame_error(self):
        irq = uart_interrupt("frame_irq")
        irq.rx_frame_error = 1
        self.irq_ap.write(irq)

    async def _glitch_free_sample(self, signal, num_cyc, sample_num, last_bit=False):
        base = num_cyc // sample_num
        samples = [base] * sample_num
        remainder = num_cyc % sample_num
        for i in range(remainder):
            samples[i] += 1
        if last_bit:
            samples.pop()
        ones = zeros = 0
        for cyc in samples:
            try:
                val = signal.value.binstr
                if val == "1":
                    ones += 1
                elif val == "0":
                    zeros += 1
            except Exception:
                pass
            await ClockCycles(self.dut.CLK, cyc)
        if ones > zeros:
            return "1"
        elif ones < zeros:
            return "0"
        return "X"
