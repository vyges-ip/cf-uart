"""UART coverage groups — auto-generated + UART-specific custom coverage."""

from cocotb_coverage.coverage import CoverPoint, CoverCross

from cf_verify.coverage.auto_coverage import generate_coverage_from_yaml
from cf_verify.bus_env.bus_item import bus_item
from ip_item.uart_item import uart_item

UART_FIELD_BINS = {
    ("CFG", "wlen"): [(v, v) for v in [5, 6, 7, 8, 9]],
    # Include reserved encodings to prevent hidden unverified modes.
    ("CFG", "parity"): [(v, v) for v in [0, 1, 2, 3, 4, 5, 6, 7]],
    ("CFG", "timeout"): [(0, 7), (8, 15), (16, 31), (32, 63)],
    ("PR", None): [(0, 3), (4, 15)],
    ("MATCH", None): [(0, 0x3F), (0x40, 0xFF), (0x100, 0x1FF)],
}

CHAR_BIN_DEFS = {
    5: [(i * 8, i * 8 + 7) for i in range(4)],
    6: [(i * 8, i * 8 + 7) for i in range(8)],
    7: [(i * 16, i * 16 + 15) for i in range(8)],
    8: [(i * 16, i * 16 + 15) for i in range(16)],
    9: [(i * 32, i * 32 + 31) for i in range(16)],
}


class uart_cov_groups:
    def __init__(self, hierarchy, regs):
        self.hierarchy = hierarchy
        self.regs = regs

        self.txdata_addr = regs.reg_name_to_address.get("TXDATA")
        self.rxdata_addr = regs.reg_name_to_address.get("RXDATA")

        self.auto_points = generate_coverage_from_yaml(
            regs, hierarchy, field_bins_override=UART_FIELD_BINS,
        )

        self.char_cov = self._char_coverage()
        self.error_cov = self._error_coverage()
        self.mode_cov = self._mode_coverage()
        self.fifo_full_cov = self._fifo_full_coverage()

        self._init_sample(None)

    def _init_sample(self, tr):
        """Cold-start: register all CoverPoints without actually counting."""
        @self._apply_decorators(
            self.auto_points + self.char_cov + self.error_cov
            + self.mode_cov + self.fifo_full_cov
        )
        def _cold(tr):
            pass

    def sample(self, tr):
        """Sample everything using a uart_item (real or synthetic)."""
        @self._apply_decorators(
            self.auto_points + self.char_cov + self.error_cov
            + self.mode_cov + self.fifo_full_cov
        )
        def _s(tr):
            pass
        _s(tr)

    def sample_bus(self, tr):
        """Sample from bus transactions; synthesise uart_item for TXDATA/RXDATA."""
        # Update software shadow for read-only registers (RIS, MIS, FIFO levels)
        if tr.kind == bus_item.READ:
            rname = self.regs._reg_address_to_name.get(tr.addr)
            if rname:
                self.regs._reg_values[rname.lower()] = tr.data

        @self._apply_decorators(
            self.auto_points + self.error_cov + self.mode_cov + self.fifo_full_cov
        )
        def _bus(tr):
            pass
        _bus(tr)

        if (self.txdata_addr is not None
                and tr.addr == self.txdata_addr
                and tr.kind == bus_item.WRITE):
            self.sample(self._synth(tr.data, uart_item.TX))
        # RX semantic coverage is primarily sampled from real monitor uart_item
        # traffic. If that path is unavailable, allow RXDATA-read synthesis only
        # when there is evidence that RX FIFO is non-empty.
        elif (self.rxdata_addr is not None
              and tr.addr == self.rxdata_addr
              and tr.kind == bus_item.READ):
            rx_lvl = self.regs.read_reg_value("RX_FIFO_LEVEL")
            if rx_lvl > 0 or tr.data != 0:
                self.sample(self._synth(tr.data, uart_item.RX))

    def _synth(self, data, direction):
        """Build a synthetic uart_item from bus data + current CFG state."""
        cfg = self.regs.read_reg_value("CFG")
        wlen = cfg & 0xF
        if wlen < 5 or wlen > 9:
            wlen = 8
        parity_type = (cfg >> 5) & 0x7

        item = uart_item("synth")
        item.direction = direction
        item.word_length = wlen
        item.char = data & ((1 << wlen) - 1)
        item.calculate_parity(parity_type)
        return item

    # ── char / parity coverage ─────────────────────────────────────────

    def _char_coverage(self):
        points = []
        for direction in [uart_item.TX, uart_item.RX]:
            d_str = "TX" if direction == uart_item.TX else "RX"
            for wlen, bins in CHAR_BIN_DEFS.items():
                points.append(CoverPoint(
                    f"{self.hierarchy}.{d_str}.Len{wlen}.Char",
                    xf=lambda tr: (
                        (tr.direction, tr.word_length, tr.char) if tr else (0, 0, 0)
                    ),
                    bins=bins,
                    bins_labels=[f"0x{lo:x}-0x{hi:x}" for lo, hi in bins],
                    rel=lambda val, b, d=direction, w=wlen: (
                        val[0] == d and val[1] == w
                        and b[0] <= val[2] <= b[1]
                    ),
                ))
                parity_bins = [
                    ("None", 0), ("0", 1), ("1", 1),
                    ("0", 2), ("1", 2), ("0", 4), ("1", 5),
                ]
                points.append(CoverPoint(
                    f"{self.hierarchy}.{d_str}.Len{wlen}.Parity",
                    xf=lambda tr: (
                        (tr.direction, tr.word_length, tr.parity,
                         (self.regs.read_reg_value("CFG") >> 5) & 0x7)
                        if tr else (0, 0, "None", 0)
                    ),
                    bins=parity_bins,
                    bins_labels=[
                        "None", "odd_0", "odd_1",
                        "even_0", "even_1", "stick_0", "stick_1",
                    ],
                    rel=lambda val, b, d=direction, w=wlen: (
                        val[0] == d and val[1] == w
                        and b[0] == val[2] and b[1] == val[3]
                    ),
                ))
        return points

    # ── mode coverage (register-state only) ────────────────────────────

    def _mode_coverage(self):
        return [
            CoverPoint(
                f"{self.hierarchy}.Loopback",
                xf=lambda tr: (self.regs.read_reg_value("CTRL") >> 3) & 1,
                bins=[0, 1], bins_labels=["normal", "loopback"], at_least=1,
            ),
            CoverPoint(
                f"{self.hierarchy}.GlitchFilter",
                xf=lambda tr: (self.regs.read_reg_value("CTRL") >> 4) & 1,
                bins=[0, 1], bins_labels=["disabled", "enabled"], at_least=1,
            ),
            CoverPoint(
                f"{self.hierarchy}.StopBits",
                xf=lambda tr: (self.regs.read_reg_value("CFG") >> 4) & 1,
                bins=[0, 1], bins_labels=["one_stop", "two_stop"], at_least=1,
            ),
        ]

    def _fifo_full_coverage(self):
        return [
            CoverPoint(
                f"{self.hierarchy}.fifo.RX_FIFO.full",
                xf=lambda tr: 1 if (
                    ((self.regs.read_reg_value("RIS") >> 1) & 1)
                    or (self.regs.read_reg_value("RX_FIFO_LEVEL") == 15)
                ) else 0,
                bins=[1], bins_labels=["full"], at_least=1,
            ),
            CoverPoint(
                f"{self.hierarchy}.fifo.TX_FIFO.full",
                xf=lambda tr: self.regs.read_reg_value("TX_FIFO_LEVEL"),
                bins=[15], bins_labels=["full"], at_least=1,
            ),
        ]

    # ── error / flag coverage ──────────────────────────────────────────

    def _error_coverage(self):
        return [
            CoverPoint(
                f"{self.hierarchy}.Errors.FrameError",
                xf=lambda tr: (self.regs.read_reg_value("RIS") >> 6) & 1,
                bins=[0, 1], bins_labels=["no_frame_err", "frame_err"],
                at_least=1,
            ),
            CoverPoint(
                f"{self.hierarchy}.Errors.ParityError",
                xf=lambda tr: (self.regs.read_reg_value("RIS") >> 7) & 1,
                bins=[0, 1], bins_labels=["no_parity_err", "parity_err"],
                at_least=1,
            ),
            CoverPoint(
                f"{self.hierarchy}.Errors.Overrun",
                xf=lambda tr: (self.regs.read_reg_value("RIS") >> 8) & 1,
                bins=[0, 1], bins_labels=["no_overrun", "overrun"],
                at_least=1,
            ),
            CoverPoint(
                f"{self.hierarchy}.Errors.Timeout",
                xf=lambda tr: (self.regs.read_reg_value("RIS") >> 9) & 1,
                bins=[0, 1], bins_labels=["no_timeout", "timeout"],
                at_least=1,
            ),
            CoverPoint(
                f"{self.hierarchy}.Errors.Break",
                xf=lambda tr: (self.regs.read_reg_value("RIS") >> 4) & 1,
                bins=[0, 1], bins_labels=["no_break", "break"],
                at_least=1,
            ),
            CoverPoint(
                f"{self.hierarchy}.Match",
                xf=lambda tr: (self.regs.read_reg_value("RIS") >> 5) & 1,
                bins=[0, 1], bins_labels=["no_match", "match"],
                at_least=1,
            ),
        ]

    @staticmethod
    def _apply_decorators(decorators):
        def wrapper(func):
            for dec in decorators:
                func = dec(func)
            return func
        return wrapper
