"""UART prescaler stress sequence — sweeps prescaler values."""

import random

import cocotb
from cocotb.triggers import Event
from pyuvm import uvm_sequence, ConfigDB

from cf_verify.bus_env.bus_seq_lib import write_reg_seq, reset_seq
from seq_lib.uart_config import uart_config
from ip_item.uart_item import uart_item


class uart_prescalar_seq(uvm_sequence):
    """IP-side sequence: sends RX chars at different prescaler rates."""

    def __init__(self, handshake_event, name="uart_prescalar_seq"):
        super().__init__(name)
        self.handshake = handshake_event

    async def body(self):
        for _ in range(3):
            await self.handshake.wait()
            self.handshake.clear()
            for _ in range(3):
                tr = uart_item("pr_rx")
                tr.randomize()
                tr.direction = uart_item.RX
                await self.start_item(tr)
                await self.finish_item(tr)
            self.handshake.set()


class uart_prescalar_seq_wrapper(uvm_sequence):
    """Bus-side sequence: configures UART with different prescalers then sends TX."""

    def __init__(self, handshake_event, name="uart_prescalar_seq_wrapper"):
        super().__init__(name)
        self.handshake = handshake_event
        self.monitor = None

    async def body(self):
        await reset_seq("rst").start(self.sequencer)
        regs = ConfigDB().get(None, "", "bus_regs")
        addr = regs.reg_name_to_address

        for pr in [1, 2, 4]:
            config = uart_config("config", prescaler=pr)
            await config.start(self.sequencer)

            for _ in range(2):
                data = random.randint(0, 0x1FF)
                await write_reg_seq("tx", addr["TXDATA"], data).start(self.sequencer)

            # Signal IP-side to send RX
            self.handshake.set()
            await self.handshake.wait()
            self.handshake.clear()
