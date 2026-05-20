"""CF_UART behavioral model — golden reference for TX/RX, FIFOs, and flags."""

import asyncio

import cocotb
from cocotb.triggers import Event
from cocotb.queue import Queue
from pyuvm import uvm_component, ConfigDB

from ip_item.uart_item import uart_item


class CF_UART_Model(uvm_component):
    def build_phase(self):
        super().build_phase()
        self.regs = ConfigDB().get(None, "", "bus_regs")
        self.tag = "CF_UART_Model"
        self.fifo_tx = _TxQueue(maxsize=16)
        self.fifo_tx_threshold = False
        self.fifo_rx = Queue(maxsize=16)
        self.fifo_rx_threshold = False
        self.tx_thread = None
        self.event_control = Event()
        self.tx_trig_event = Event()
        self.new_rx_received = Event()
        self.flags = _Flags(self.regs, self.tag)

        from pyuvm import uvm_analysis_port, uvm_tlm_analysis_fifo
        self.ip_export = uvm_analysis_port("model_export", self)
        self.rx_fifo = uvm_tlm_analysis_fifo("model_rx_fifo", self)
        self.rx_analysis_export = self.rx_fifo.analysis_export

    def start_of_simulation_phase(self):
        cocotb.start_soon(self._control_regs())

    def reset(self):
        self.regs.write_reg_value("PR", 0)
        self.fifo_tx = _TxQueue(maxsize=16)
        self.fifo_tx_threshold = False
        self.fifo_rx = Queue(maxsize=16)
        self.fifo_rx_threshold = False
        self.flags = _Flags(self.regs, self.tag)
        self.flags.set_tx_empty()

    def write_register(self, addr, data):
        self.regs.write_reg_value(addr, data)
        reg_map = self.regs.reg_name_to_address
        if addr == reg_map.get("IC", -1):
            self.flags.clear_interrupts(data)
            return
        if addr == reg_map.get("TXDATA", -1):
            word_mask = (1 << (self.regs.read_reg_value("CFG") & 0xF)) - 1
            try:
                self.fifo_tx.put_nowait(data & word_mask)
                self._check_tx_level_threshold()
            except asyncio.QueueFull:
                pass
        if addr == reg_map.get("CTRL", -1):
            self.event_control.set()
        if addr == reg_map.get("IM", -1):
            self.flags.sync_mis()

    def read_register(self, addr):
        reg_map = self.regs.reg_name_to_address
        if addr in (reg_map.get("RIS", -1), reg_map.get("MIS", -1)):
            # Keep dynamic flag semantics synchronized for status reads.
            if self.fifo_tx.qsize() == 0:
                self.flags.set_tx_empty()
            self._check_tx_level_threshold()
            self._check_rx_level_threshold()
            self.flags.sync_mis()
        if addr == reg_map.get("MIS", -1):
            return self.regs.read_reg_value("ris") & self.regs.read_reg_value("im")
        if addr == reg_map.get("RXDATA", -1):
            try:
                data = self.fifo_rx.get_nowait()
                self._check_rx_level_threshold()
                return data
            except asyncio.QueueEmpty:
                return 0
        return self.regs.read_reg_value(addr)

    def write_rx(self, tr):
        ctrl = self.regs.read_reg_value("CTRL") & 7
        if ctrl in (5, 7):
            try:
                self.fifo_rx.put_nowait(tr.char)
                self._check_receiver_match(tr.char)
                self._check_rx_level_threshold()
                self.new_rx_received.set()
                if self.fifo_rx.full():
                    self.flags.set_rx_full()
            except asyncio.QueueFull:
                self.new_rx_received.set()
                self._check_receiver_match(tr.char)
                self.flags.set_overrun_err()

    async def _transmit(self):
        while True:
            data_tx = await self.fifo_tx.get_no_pop()
            self._check_tx_level_threshold()
            tr = uart_item("tx_model_tr")
            tr.char = data_tx
            tr.direction = uart_item.TX
            parity_type = (self.regs.read_reg_value("CFG") >> 5) & 0x7
            tr.calculate_parity(parity_type)
            tr.word_length = self.regs.read_reg_value("CFG") & 0xF
            await self.tx_trig_event.wait()
            self.ip_export.write(tr)
            self.tx_trig_event.clear()
            await self.fifo_tx.get()
            if self.fifo_tx.qsize() == 0:
                self.flags.set_tx_empty()

            # Loopback
            if (self.regs.read_reg_value("CTRL") & 0xF) == 0xF:
                try:
                    self.fifo_rx.put_nowait(data_tx)
                    self._check_receiver_match(data_tx)
                    self._check_rx_level_threshold()
                    if self.fifo_rx.full():
                        self.flags.set_rx_full()
                except asyncio.QueueFull:
                    self._check_receiver_match(data_tx)
                    self.flags.set_overrun_err()

    async def _control_regs(self):
        while True:
            ctrl = self.regs.read_reg_value("CTRL") & 7
            if ctrl in (3, 7):
                if self.tx_thread is None:
                    self.tx_thread = cocotb.start_soon(self._transmit())
            elif self.tx_thread is not None:
                self.tx_thread.kill()
                self.tx_thread = None
            await self.event_control.wait()
            self.event_control.clear()

    def _check_receiver_match(self, new_char):
        match_reg = self.regs.read_reg_value("MATCH")
        if new_char == match_reg:
            self.flags.set_data_match()

    def _check_rx_level_threshold(self):
        threshold = self.regs.read_reg_value("RX_FIFO_THRESHOLD")
        if self.fifo_rx.qsize() > threshold:
            if not self.fifo_rx_threshold:
                self.fifo_rx_threshold = True
                self.flags.set_rx_above_threshold()

    def _check_tx_level_threshold(self):
        threshold = self.regs.read_reg_value("TX_FIFO_THRESHOLD")
        if self.fifo_tx.qsize() < threshold:
            if not self.fifo_tx_threshold:
                self.fifo_tx_threshold = True
                self.flags.set_tx_below_threshold()


class _Flags:
    def __init__(self, regs, tag="Flags"):
        self.regs = regs
        self.tag = tag
        self.mis_changed = Event()

    def sync_mis(self):
        ris = self.regs.read_reg_value("ris") & 0x3FF
        im = self.regs.read_reg_value("im") & 0x3FF
        new_mis = ris & im
        old_mis = self.regs.read_reg_value("mis") & 0x3FF
        self.regs.write_reg_value("mis", new_mis)
        if (old_mis == 0 and new_mis != 0) or (old_mis != 0 and new_mis == 0):
            self.mis_changed.set()

    def _write_interrupt(self, mask, name=""):
        self.regs.write_reg_value("ris", mask, mask=mask)
        self.sync_mis()

    def clear_interrupts(self, ic_mask):
        ic_mask &= 0x3FF
        if ic_mask == 0:
            return
        ris = self.regs.read_reg_value("ris") & 0x3FF
        self.regs.write_reg_value("ris", ris & ~ic_mask)
        self.sync_mis()

    # Bit mapping follows YAML/RTL: TXE,RXF,TXB,RXA,BRK,MATCH,FE,PRE,OR,RTO.
    def set_tx_empty(self): self._write_interrupt(0b0000000001, "TX empty")
    def set_rx_full(self): self._write_interrupt(0b0000000010, "RX full")
    def set_tx_below_threshold(self): self._write_interrupt(0b0000000100, "TX below threshold")
    def set_rx_above_threshold(self): self._write_interrupt(0b0000001000, "RX above threshold")
    def set_line_break(self): self._write_interrupt(0b0000010000, "Line break")
    def set_data_match(self): self._write_interrupt(0b0000100000, "Data match")
    def set_frame_err(self): self._write_interrupt(0b0001000000, "Frame error")
    def set_parity_err(self): self._write_interrupt(0b0010000000, "Parity error")
    def set_overrun_err(self): self._write_interrupt(0b0100000000, "Overrun error")
    def set_timeout_err(self): self._write_interrupt(0b1000000000, "Timeout error")


class _TxQueue(Queue):
    async def get_no_pop(self):
        """Peek at front of queue without removing, blocking if empty."""
        while self.empty():
            event = Event()
            self._getters.append((event, cocotb.task.current_task()))
            await event.wait()
        return self._queue[0]
