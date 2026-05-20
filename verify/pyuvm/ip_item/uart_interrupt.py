"""UART interrupt transaction — carries interrupt flags from monitor to VIP."""

from pyuvm import uvm_sequence_item


class uart_interrupt(uvm_sequence_item):
    def __init__(self, name="uart_interrupt"):
        super().__init__(name)
        self.rx_timeout = 0
        self.rx_break_line = 0
        self.rx_wrong_parity = 0
        self.rx_frame_error = 0

    def convert2string(self):
        return (
            f"rx_timeout={self.rx_timeout}, rx_break_line={self.rx_break_line}, "
            f"rx_wrong_parity={self.rx_wrong_parity}, rx_frame_error={self.rx_frame_error}"
        )
