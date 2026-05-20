"""UART RX sequence — drives random characters into the UART RX line."""

import random

from pyuvm import uvm_sequence

from ip_item.uart_item import uart_item


class uart_rx_seq(uvm_sequence):
    async def body(self):
        for _ in range(6):
            tr = uart_item("rx_item")
            tr.randomize()
            tr.direction = uart_item.RX
            await self.start_item(tr)
            await self.finish_item(tr)
