"""UART interface wrapper — provides clean access to DUT signals."""


class uart_if:
    def __init__(self, dut):
        self.dut = dut
        self.CLK = dut.CLK
        self.RESETn = dut.RESETn
        self.RX = dut.RX
        self.TX = dut.TX
        self.tx_done = dut.tx_done
        self.rx_done = dut.rx_done
