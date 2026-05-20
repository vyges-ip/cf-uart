"""UART configuration sequence — sets up prescaler, CFG, IM, CTRL registers."""

import random

from pyuvm import uvm_sequence, ConfigDB

from cf_verify.bus_env.bus_item import bus_item
from cf_verify.bus_env.bus_seq_lib import write_reg_seq, reset_seq


class uart_config(uvm_sequence):
    def __init__(self, name="uart_config", prescaler=None, config=None,
                 im=None, match=None, control=None):
        super().__init__(name)
        self.prescaler = prescaler
        self.config = config
        self.im = im
        self.match = match
        self.control = control
        self.is_glitch_filter_en = False

    async def body(self):
        await reset_seq("rst").start(self.sequencer)
        regs = ConfigDB().get(None, "", "bus_regs")
        addr = regs.reg_name_to_address

        # Enable clock gate
        if "GCLK" in addr:
            await write_reg_seq("wr_gclk", addr["GCLK"], 1).start(self.sequencer)

        # Disable UART first
        await write_reg_seq("wr_ctrl_off", addr["CTRL"], 0).start(self.sequencer)

        # Prescaler
        pr = self.prescaler if self.prescaler is not None else random.randint(1, 3)
        await write_reg_seq("wr_pr", addr["PR"], pr).start(self.sequencer)

        # Configuration
        if self.config is not None:
            cfg = self.config
        else:
            wlen = random.choice([5, 6, 7, 8, 9])
            parity = random.choice([0, 1, 2, 4, 5])
            stp2 = random.randint(0, 1)
            timeout = random.choice([0x3, 0xF, 0x1F, 0x3F])
            cfg = wlen | (stp2 << 4) | (parity << 5) | (timeout << 8)
        await write_reg_seq("wr_cfg", addr["CFG"], cfg).start(self.sequencer)

        # Interrupt mask
        im_val = self.im if self.im is not None else random.randint(0, 0x3FF)
        if "IM" in addr:
            await write_reg_seq("wr_im", addr["IM"], im_val).start(self.sequencer)

        # Match register
        match_val = self.match if self.match is not None else random.choice(
            [random.randint(0, 0x1F), random.randint(0x20, 0x7F),
             random.randint(0x80, 0xFF), random.randint(0x100, 0x1FF)]
        )
        if "MATCH" in addr:
            await write_reg_seq("wr_match", addr["MATCH"], match_val).start(self.sequencer)

        # Enable UART
        if self.control is not None:
            ctrl = self.control
        else:
            self.is_glitch_filter_en = random.randint(0, 1)
            if self.is_glitch_filter_en:
                # Enable glitch filter first, then enable TX+RX
                await write_reg_seq("wr_ctrl_gf", addr["CTRL"], 0x10).start(self.sequencer)
                # Wait a few cycles for glitch filter to stabilize
                nop = write_reg_seq("nop", addr["CTRL"], 0x10)
                for _ in range(16):
                    await nop.start(self.sequencer)
                ctrl = 0x17  # en + txen + rxen + gfen
            else:
                ctrl = 0x07  # en + txen + rxen
        await write_reg_seq("wr_ctrl", addr["CTRL"], ctrl).start(self.sequencer)
