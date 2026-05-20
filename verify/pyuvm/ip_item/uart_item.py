"""UART transaction item — carries char, direction, parity, word_length."""

import random

from pyuvm import uvm_sequence_item


class uart_item(uvm_sequence_item):
    RX = 0
    TX = 1

    def __init__(self, name="uart_item"):
        super().__init__(name)
        self.char = 0
        self.direction = uart_item.RX
        self.word_length = 8
        self.parity = "None"

    def randomize(self, max_val=0x1FF):
        self.char = random.randint(0, max_val)

    def convert2string(self):
        d = "RX" if self.direction == uart_item.RX else "TX"
        return (
            f"uart char={chr(self.char) if 32 <= self.char < 127 else '?'}"
            f"(0x{self.char:x}) direction={d}, "
            f"word_length={self.word_length}, parity={self.parity}"
        )

    def do_compare(self, rhs):
        return (
            self.char == rhs.char
            and self.direction == rhs.direction
            and self.word_length == rhs.word_length
            and self.parity == rhs.parity
        )

    def do_copy(self, rhs):
        super().do_copy(rhs)
        self.char = rhs.char
        self.direction = rhs.direction
        self.word_length = rhs.word_length
        self.parity = rhs.parity

    def do_clone(self):
        new = uart_item(self.get_name())
        new.do_copy(self)
        return new

    def calculate_parity(self, parity_type):
        if parity_type == 0:
            self.parity = "None"
        elif parity_type == 1:  # odd
            self.parity = "0" if self._count_ones(self.char) % 2 else "1"
        elif parity_type == 2:  # even
            self.parity = "0" if self._count_ones(self.char) % 2 == 0 else "1"
        elif parity_type == 4:  # sticky 0
            self.parity = "0"
        elif parity_type == 5:  # sticky 1
            self.parity = "1"
        else:
            self.parity = "None"

    @staticmethod
    def _count_ones(n):
        count = 0
        while n:
            count += n & 1
            n >>= 1
        return count
