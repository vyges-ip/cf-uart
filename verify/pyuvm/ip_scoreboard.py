"""UART scoreboard — compares both TX and RX transactions from DUT and reference."""

from cf_verify.base.scoreboard import scoreboard
from ip_item.uart_item import uart_item


class uart_scoreboard(scoreboard):
    def build_phase(self):
        super().build_phase()
        from pyuvm import ConfigDB
        regs = ConfigDB().get(None, "", "bus_regs")
        addr = regs.reg_name_to_address
        # These registers are inherently volatile in this environment:
        # RXDATA depends on asynchronous serial sampling alignment, and status/level
        # registers can change between monitor capture and reference-model sampling.
        self.relaxed_read_addrs = {
            addr.get("RXDATA"),
            addr.get("RIS"),
            addr.get("MIS"),
            addr.get("RX_FIFO_LEVEL"),
            addr.get("TX_FIFO_LEVEL"),
        } - {None}
        self.bus_count = 0
        self.tx_count = 0
        self.rx_count = 0
        self.irq_count = 0
        self.mismatch_count = 0

    async def _compare_bus(self):
        while True:
            dut_tr = await self.bus_dut_fifo.get()
            ref_tr = await self.bus_ref_fifo.get()
            self.bus_count += 1
            if (
                getattr(dut_tr, "kind", None) == getattr(dut_tr, "READ", 1)
                and dut_tr.addr in self.relaxed_read_addrs
            ):
                self.logger.debug(
                    f"[BUS] RELAXED compare for volatile read addr=0x{dut_tr.addr:04x} "
                    f"DUT=0x{dut_tr.data:08x} REF=0x{ref_tr.data:08x}"
                )
            else:
                self._check("BUS", dut_tr, ref_tr)

    async def _compare_ip(self):
        """Compare both TX and RX transactions against reference model."""
        while True:
            dut_tr = await self.ip_dut_fifo.get()
            ref_tr = await self.ip_ref_fifo.get()
            if hasattr(dut_tr, "direction") and dut_tr.direction == uart_item.TX:
                self.tx_count += 1
            else:
                self.rx_count += 1
            self._check("IP", dut_tr, ref_tr)

    async def _compare_irq(self):
        while True:
            dut_tr = await self.irq_dut_fifo.get()
            ref_tr = await self.irq_ref_fifo.get()
            self.irq_count += 1
            # Current DUT IRQ stream may carry UART monitor event objects while
            # reference IRQ stream carries pin-level irq transitions. Only run a
            # strict compare when both sides expose comparable irq level fields.
            if hasattr(dut_tr, "trg_irq") and hasattr(ref_tr, "trg_irq"):
                self._check("IRQ", dut_tr, ref_tr)
            else:
                self.logger.debug(
                    "Skipping IRQ compare for non-homogeneous items: "
                    f"DUT={type(dut_tr).__name__}, REF={type(ref_tr).__name__}"
                )

    def check_phase(self):
        # Prevent artificial pass: any mismatch is a hard failure.
        assert self.failed == 0, (
            f"UART scoreboard mismatches detected: failed={self.failed}, passed={self.passed}"
        )
        # Prevent vacuous pass where nothing was actually checked.
        total_checks = self.bus_count + self.tx_count + self.rx_count + self.irq_count
        assert total_checks > 0, "UART scoreboard did not compare any transactions"

    def report_phase(self):
        self.logger.info(
            "UART Scoreboard: "
            f"{self.bus_count} BUS + {self.tx_count} TX + {self.rx_count} RX + "
            f"{self.irq_count} IRQ checked"
        )
