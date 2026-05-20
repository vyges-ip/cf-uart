"""UART VIP — reference model connecting bus transactions to the behavioral model."""

import cocotb
from pyuvm import ConfigDB, uvm_tlm_analysis_fifo

from cf_verify.base.ref_model import ref_model
from cf_verify.bus_env.bus_item import bus_item, bus_irq_item
from ref_model.model import CF_UART_Model
from ip_item.uart_item import uart_item


class UART_VIP(ref_model):
    def build_phase(self):
        super().build_phase()
        self.model = CF_UART_Model("model", self)
        self.tx_ref_fifo = uvm_tlm_analysis_fifo("tx_ref_fifo", self)

    def connect_phase(self):
        super().connect_phase()
        self.model.ip_export.connect(self.tx_ref_fifo.analysis_export)

    def start_of_simulation_phase(self):
        cocotb.start_soon(self._update_irq())
        cocotb.start_soon(self._forward_tx_ref())

    def write_bus(self, tr):
        if tr.kind == bus_item.RESET:
            self.model.reset()
            self.bus_out.write(tr)
            return
        if tr.kind == bus_item.WRITE:
            self.model.write_register(tr.addr, tr.data)
            self.bus_out.write(tr)
        elif tr.kind == bus_item.READ:
            data = self.model.read_register(tr.addr)
            td = tr.do_clone()
            td.data = data
            self.bus_out.write(td)

    def write_ip(self, tr):
        if tr.direction == uart_item.TX:
            self.model.tx_trig_event.set()
        else:
            self.model.write_rx(tr)
            # Build an independent expected RX transaction from model config.
            exp = uart_item("rx_ref_tr")
            exp.direction = uart_item.RX
            exp.char = tr.char
            exp.word_length = self.model.regs.read_reg_value("CFG") & 0xF
            parity_type = (self.model.regs.read_reg_value("CFG") >> 5) & 0x7
            exp.calculate_parity(parity_type)
            self.ip_out.write(exp)

    def write_ip_irq(self, tr):
        if tr.rx_timeout:
            self.model.flags.set_timeout_err()
        if tr.rx_break_line:
            self.model.flags.set_line_break()
        if tr.rx_wrong_parity:
            self.model.flags.set_parity_err()
        if tr.rx_frame_error:
            self.model.flags.set_frame_err()

    async def _update_irq(self):
        irq = 0
        while True:
            await self.model.flags.mis_changed.wait()
            mis_val = self.model.regs.read_reg_value("mis")
            if mis_val != 0 and irq == 0:
                irq = 1
                tr = bus_irq_item("irq_tr")
                tr.trg_irq = 1
                self.irq_out.write(tr)
            elif mis_val == 0 and irq == 1:
                irq = 0
                tr = bus_irq_item("irq_tr")
                tr.trg_irq = 0
                self.irq_out.write(tr)
            self.model.flags.mis_changed.clear()

    async def _forward_tx_ref(self):
        while True:
            tr = await self.tx_ref_fifo.get()
            self.ip_out.write(tr)
