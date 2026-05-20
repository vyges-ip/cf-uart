"""UART glitch filter sequence — verifies glitch filtering on RX line."""

import random

from pyuvm import uvm_sequence
from ip_item.uart_item import uart_item


class uart_glitch_filter_seq(uvm_sequence):
    """IP-side sequence: sends RX chars with glitches injected by the driver."""

    async def body(self):
        for _ in range(3):
            tr = uart_item("gf_rx")
            tr.char = random.randint(0, 0x1FF)
            tr.direction = uart_item.RX
            await self.start_item(tr)
            await self.finish_item(tr)
