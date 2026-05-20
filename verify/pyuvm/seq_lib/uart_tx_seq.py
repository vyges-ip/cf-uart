"""UART TX stress sequence — writes random data to TXDATA, waits for TX completion."""

import os
import random

from pyuvm import uvm_sequence, ConfigDB

from cf_verify.bus_env.bus_seq_lib import write_reg_seq, reset_seq
from seq_lib.uart_config import uart_config


class uart_tx_seq(uvm_sequence):
    def __init__(self, name="uart_tx_seq"):
        super().__init__(name)
        self.monitor = None

    async def body(self):
        await reset_seq("rst").start(self.sequencer)
        regs = ConfigDB().get(None, "", "bus_regs")
        addr = regs.reg_name_to_address

        config = uart_config("config")
        await config.start(self.sequencer)

        n_iters = int(os.environ.get("TX_STRESS_ITERS", "3"))
        for _ in range(n_iters):
            n_send = random.randint(1, 4)
            for _ in range(n_send):
                data = random.randint(0, 0x1FF)
                await write_reg_seq("tx_wr", addr["TXDATA"], data).start(self.sequencer)

        pass
