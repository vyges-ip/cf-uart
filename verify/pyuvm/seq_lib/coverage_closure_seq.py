"""Coverage closure sequence — systematically exercises all coverage bins."""

import cocotb
from cocotb.triggers import ClockCycles
from pyuvm import uvm_sequence, ConfigDB

from cf_verify.bus_env.bus_seq_lib import write_reg_seq, read_reg_seq, reset_seq

CHAR_REPS = {
    5: [4, 12, 20, 28],
    6: [4, 12, 20, 28, 36, 44, 52, 60],
    7: [8, 24, 40, 56, 72, 88, 104, 120],
    8: [8, 24, 40, 56, 72, 88, 104, 120, 136, 152, 168, 184, 200, 216, 232, 248],
    9: [16, 48, 80, 112, 144, 176, 208, 240, 272, 304, 336, 368, 400, 432, 464, 496],
}
CTRL_CROSS_VALS = [0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x07, 0x0F, 0x17, 0x1F]
TIMEOUT_VALS = [3, 10, 20, 40]


class coverage_closure_seq(uvm_sequence):
    async def body(self):
        await reset_seq("rst").start(self.sequencer)
        regs = ConfigDB().get(None, "", "bus_regs")
        self.addr = regs.reg_name_to_address
        self.dut = ConfigDB().get(None, "", "DUT")

        if "GCLK" in self.addr:
            await self._w("gclk", "GCLK", 1)

        self.dut.RX.value = 1

        await self._ctrl_cross()
        await self._cfg_cross_and_tx()
        await self._rx_chars_direct()
        await self._fifo_levels()
        await self._flag_triggers()
        await self._pr_and_match()

    # ── helpers ─────────────────────────────────────────────────────────

    async def _w(self, name, reg, val):
        await write_reg_seq(name, self.addr[reg], val).start(self.sequencer)

    async def _r(self, name, reg):
        seq = read_reg_seq(name, self.addr[reg])
        await seq.start(self.sequencer)
        return seq.result

    async def _setup(self, pr, cfg, ctrl):
        await self._w("ctrl_off", "CTRL", 0)
        await self._w("pr", "PR", pr)
        await self._w("cfg", "CFG", cfg)
        if "TX_FIFO_FLUSH" in self.addr:
            await self._w("flush_tx", "TX_FIFO_FLUSH", 1)
        if "RX_FIFO_FLUSH" in self.addr:
            await self._w("flush_rx", "RX_FIFO_FLUSH", 1)
        await self._w("ctrl_on", "CTRL", ctrl)

    def _bit_cyc(self, pr):
        return (pr + 1) * 8

    async def _drive_rx_frame(self, char, wlen, parity_type, bit_cyc):
        """Bit-bang a UART frame onto the RX pin."""
        self.dut.RX.value = 0  # start
        await ClockCycles(self.dut.CLK, bit_cyc)
        for i in range(wlen):
            self.dut.RX.value = (char >> i) & 1
            await ClockCycles(self.dut.CLK, bit_cyc)
        if parity_type in (1, 2, 4, 5):
            self.dut.RX.value = self._parity_bit(char, wlen, parity_type)
            await ClockCycles(self.dut.CLK, bit_cyc)
        self.dut.RX.value = 1  # stop
        await ClockCycles(self.dut.CLK, bit_cyc * 2)

    @staticmethod
    def _parity_bit(char, wlen, parity_type):
        ones = bin(char & ((1 << wlen) - 1)).count("1")
        if parity_type == 1:     # odd
            return 0 if ones % 2 else 1
        elif parity_type == 2:   # even
            return 1 if ones % 2 else 0
        elif parity_type == 4:   # sticky 0
            return 0
        elif parity_type == 5:   # sticky 1
            return 1
        return 0

    # ── Phase 1: CTRL field-pair crosses ───────────────────────────────

    async def _ctrl_cross(self):
        for ctrl in CTRL_CROSS_VALS:
            await self._w("ctrl", "CTRL", ctrl)

    # ── Phase 2: CFG crosses + TX char + TX parity ─────────────────────

    async def _cfg_cross_and_tx(self):
        parity_cfg_vals = [0, 1, 2, 3, 4, 5, 6, 7]
        parity_semantic_vals = [0, 1, 2, 4, 5]
        for wlen in [5, 6, 7, 8, 9]:
            chars = CHAR_REPS[wlen]
            mask = (1 << wlen) - 1

            # Close CFG field and cross bins, including reserved parity encodings.
            for parity in parity_cfg_vals:
                for stp2 in [0, 1]:
                    for timeout in TIMEOUT_VALS:
                        cfg = wlen | (stp2 << 4) | (parity << 5) | (timeout << 8)
                        await self._setup(1, cfg, 0x07)

                        if parity in parity_semantic_vals:
                            odd_char = 1 & mask
                            even_char = 3 & mask
                            await self._w("tx0", "TXDATA", odd_char)
                            await self._w("tx1", "TXDATA", even_char)

            # Per-wlen: fill every TX Char bin
            cfg_base = wlen | (0x3F << 8)
            await self._setup(1, cfg_base, 0x07)
            for ch in chars:
                await self._w("tx_ch", "TXDATA", ch)

    # ── Phase 3: RX char + RX parity via direct RX drive ──────────────

    async def _rx_chars_direct(self):
        pr = 2
        bc = self._bit_cyc(pr)

        for wlen in [5, 6, 7, 8, 9]:
            chars = CHAR_REPS[wlen]

            cfg = wlen | (0x3F << 8)
            await self._setup(pr, cfg, 0x07)
            self.dut.RX.value = 1
            await ClockCycles(self.dut.CLK, bc * 4)

            for ch in chars:
                await self._drive_rx_frame(ch, wlen, 0, bc)

            for _ in range(len(chars)):
                await self._r("rx_ch", "RXDATA")

            # RX Parity bins: drive chars with each parity type
            for parity in [0, 1, 2, 4, 5]:
                cfg_p = wlen | (parity << 5) | (0x3F << 8)
                await self._setup(pr, cfg_p, 0x07)
                self.dut.RX.value = 1
                await ClockCycles(self.dut.CLK, bc * 4)

                odd_char = 1 & ((1 << wlen) - 1)
                even_char = 3 & ((1 << wlen) - 1)
                await self._drive_rx_frame(odd_char, wlen, parity, bc)
                await self._drive_rx_frame(even_char, wlen, parity, bc)

                await self._r("rx_p0", "RXDATA")
                await self._r("rx_p1", "RXDATA")

    # ── Phase 4: FIFO level bins ───────────────────────────────────────

    async def _fifo_levels(self):
        pr = 2
        bc = self._bit_cyc(pr)
        cfg = 8 | (0x3F << 8)
        await self._setup(pr, cfg, 0x07)

        # TX FIFO levels
        for fill_to in [1, 5, 12, 15, 16]:
            if "TX_FIFO_FLUSH" in self.addr:
                await self._w("flush", "TX_FIFO_FLUSH", 1)
            for i in range(fill_to):
                await self._w("tx_f", "TXDATA", i)
            if "TX_FIFO_LEVEL" in self.addr:
                await self._r("tx_lvl", "TX_FIFO_LEVEL")

        if "TX_FIFO_FLUSH" in self.addr:
            await self._w("flush_tx_f", "TX_FIFO_FLUSH", 1)

        # RX FIFO levels via direct drive
        self.dut.RX.value = 1
        await ClockCycles(self.dut.CLK, bc * 4)
        for fill_to in [1, 5, 12, 15, 16]:
            if "RX_FIFO_FLUSH" in self.addr:
                await self._w("flush_rx", "RX_FIFO_FLUSH", 1)
            for i in range(fill_to):
                await self._drive_rx_frame(i, 8, 0, bc)
            if "RX_FIFO_LEVEL" in self.addr:
                await self._r("rx_lvl", "RX_FIFO_LEVEL")

        if "RX_FIFO_FLUSH" in self.addr:
            await self._w("flush_rx_f", "RX_FIFO_FLUSH", 1)

    # ── Phase 5: flag triggers ─────────────────────────────────────────

    async def _flag_triggers(self):
        pr = 2
        bc = self._bit_cyc(pr)
        cfg = 8 | (1 << 5) | (3 << 8)  # wlen=8, odd parity, timeout=3
        await self._setup(pr, cfg, 0x07)
        if "IM" in self.addr:
            await self._w("im", "IM", 0x3FF)

        # TXE — TX empty after flush
        await self._r("ris_txe", "RIS")

        # TXB — set high threshold so level is below
        if "TX_FIFO_THRESHOLD" in self.addr:
            await self._w("tx_thr", "TX_FIFO_THRESHOLD", 14)
        await self._r("ris_txb", "RIS")

        # Overrun — fill RX via direct drive, then send more
        if "RX_FIFO_FLUSH" in self.addr:
            await self._w("flush_rx_or", "RX_FIFO_FLUSH", 1)
        self.dut.RX.value = 1
        await ClockCycles(self.dut.CLK, bc * 4)
        for i in range(18):
            await self._drive_rx_frame(i, 8, 1, bc)
        await self._r("ris_or", "RIS")
        if "IC" in self.addr:
            await self._w("ic_or", "IC", 0x3FF)

        # RXA — RX above threshold
        if "RX_FIFO_FLUSH" in self.addr:
            await self._w("flush_rx_rxa", "RX_FIFO_FLUSH", 1)
        if "RX_FIFO_THRESHOLD" in self.addr:
            await self._w("rx_thr", "RX_FIFO_THRESHOLD", 2)
        for i in range(4):
            await self._drive_rx_frame(i, 8, 1, bc)
        await self._r("ris_rxa", "RIS")
        if "IC" in self.addr:
            await self._w("ic_rxa", "IC", 0x3FF)

        # RXF — fill RX completely
        if "RX_FIFO_FLUSH" in self.addr:
            await self._w("flush_rx_rxf", "RX_FIFO_FLUSH", 1)
        for i in range(16):
            await self._drive_rx_frame(i, 8, 1, bc)
        await self._r("ris_rxf", "RIS")
        if "IC" in self.addr:
            await self._w("ic_rxf", "IC", 0x3FF)

        # Timeout — idle RX
        if "RX_FIFO_FLUSH" in self.addr:
            await self._w("flush_rx_rto", "RX_FIFO_FLUSH", 1)
        self.dut.RX.value = 1
        await ClockCycles(self.dut.CLK, bc * 8)
        await self._r("ris_rto", "RIS")
        if "IC" in self.addr:
            await self._w("ic_rto", "IC", 0x3FF)

        # Break — RX held low >13 bit times (from idle=1)
        self.dut.RX.value = 1
        await ClockCycles(self.dut.CLK, bc * 4)
        self.dut.RX.value = 0
        await ClockCycles(self.dut.CLK, bc * 16)
        self.dut.RX.value = 1
        await ClockCycles(self.dut.CLK, bc * 4)
        await self._r("ris_brk", "RIS")
        if "IC" in self.addr:
            await self._w("ic_brk", "IC", 0x3FF)

        # Frame error — bad stop bit
        self.dut.RX.value = 1
        await ClockCycles(self.dut.CLK, bc * 2)
        self.dut.RX.value = 0  # start
        await ClockCycles(self.dut.CLK, bc)
        for i in range(8):
            self.dut.RX.value = (0x55 >> i) & 1
            await ClockCycles(self.dut.CLK, bc)
        self.dut.RX.value = 0  # parity (wrong, doesn't matter for FE)
        await ClockCycles(self.dut.CLK, bc)
        self.dut.RX.value = 0  # bad stop
        await ClockCycles(self.dut.CLK, bc)
        self.dut.RX.value = 1
        await ClockCycles(self.dut.CLK, bc * 3)
        await self._r("ris_fe", "RIS")
        if "IC" in self.addr:
            await self._w("ic_fe", "IC", 0x3FF)

        # Parity error — wrong parity bit (0x55 has 4 ones; odd expects bit=1, send 0)
        self.dut.RX.value = 1
        await ClockCycles(self.dut.CLK, bc * 2)
        self.dut.RX.value = 0  # start
        await ClockCycles(self.dut.CLK, bc)
        test_char = 0x55
        for i in range(8):
            self.dut.RX.value = (test_char >> i) & 1
            await ClockCycles(self.dut.CLK, bc)
        self.dut.RX.value = 0  # WRONG parity (odd parity of 0x55 should be 1)
        await ClockCycles(self.dut.CLK, bc)
        self.dut.RX.value = 1  # stop
        await ClockCycles(self.dut.CLK, bc)
        await ClockCycles(self.dut.CLK, bc * 3)
        await self._r("ris_pe", "RIS")
        if "IC" in self.addr:
            await self._w("ic_pe", "IC", 0x3FF)

        # Match — send matching char directly
        match_val = 0x42
        if "MATCH" in self.addr:
            await self._w("match", "MATCH", match_val)
        cfg_m = 8 | (0x3F << 8)
        await self._w("cfg_m", "CFG", cfg_m)
        if "RX_FIFO_FLUSH" in self.addr:
            await self._w("flush_rx_m", "RX_FIFO_FLUSH", 1)
        self.dut.RX.value = 1
        await ClockCycles(self.dut.CLK, bc * 4)
        await self._drive_rx_frame(match_val, 8, 0, bc)
        await self._r("ris_match", "RIS")

        # Read MIS for masked-irq coverage
        if "MIS" in self.addr:
            await self._r("mis", "MIS")

    # ── Phase 6: remaining PR / MATCH bins ─────────────────────────────

    async def _pr_and_match(self):
        for pr in [1, 8]:
            await self._w("pr_cov", "PR", pr)
        for mv in [0x10, 0x80, 0x150]:
            if "MATCH" in self.addr:
                await self._w("match_cov", "MATCH", mv)
