"""RX length/parity stress — sweeps word lengths and parity types for RX."""

import random

import cocotb
from cocotb.triggers import Event
from pyuvm import uvm_sequence, ConfigDB

from cf_verify.bus_env.bus_seq_lib import write_reg_seq, read_reg_seq, reset_seq
from seq_lib.uart_config import uart_config
from ip_item.uart_item import uart_item


class rx_length_parity_seq(uvm_sequence):
    """IP-side: sends RX chars after handshake."""

    def __init__(self, handshake_event, name="rx_length_parity_seq"):
        super().__init__(name)
        self.handshake = handshake_event

    async def body(self):
        for wlen in range(5, 10):
            for parity in [0, 1, 2, 4, 5]:
                await self.handshake.wait()
                self.handshake.clear()
                mask = (1 << wlen) - 1
                for _ in range(2):
                    tr = uart_item("rx_item")
                    tr.char = random.randint(0, mask)
                    tr.direction = uart_item.RX
                    await self.start_item(tr)
                    await self.finish_item(tr)
                self.handshake.set()


class rx_length_parity_seq_wrapper(uvm_sequence):
    """Bus-side: configures UART then signals IP-side, reads back RX data."""

    def __init__(self, handshake_event, name="rx_length_parity_wrapper"):
        super().__init__(name)
        self.handshake = handshake_event

    async def body(self):
        await reset_seq("rst").start(self.sequencer)
        regs = ConfigDB().get(None, "", "bus_regs")
        addr = regs.reg_name_to_address

        for wlen in range(5, 10):
            for parity in [0, 1, 2, 4, 5]:
                timeout = 0x3F
                cfg = wlen | (parity << 5) | (timeout << 8)
                config = uart_config("config", config=cfg)
                await config.start(self.sequencer)

                self.handshake.set()
                await self.handshake.wait()
                self.handshake.clear()

                for _ in range(2):
                    await read_reg_seq("rd", addr["RXDATA"]).start(self.sequencer)
