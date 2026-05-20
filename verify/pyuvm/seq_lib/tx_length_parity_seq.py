"""TX length/parity stress — sweeps word lengths and parity types for TX."""

import random

from pyuvm import uvm_sequence, ConfigDB

from cf_verify.bus_env.bus_seq_lib import write_reg_seq, reset_seq
from seq_lib.uart_config import uart_config


class tx_length_parity_seq(uvm_sequence):
    def __init__(self, name="tx_length_parity_seq"):
        super().__init__(name)
        self.monitor = None

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

                mask = (1 << wlen) - 1
                for _ in range(2):
                    data = random.randint(0, mask)
                    await write_reg_seq("tx", addr["TXDATA"], data).start(self.sequencer)
