"""UART interrupt sequence — exercises all interrupt sources and verifies IM/IC."""

import random

from pyuvm import uvm_sequence, ConfigDB

from cf_verify.bus_env.bus_seq_lib import write_reg_seq, read_reg_seq, reset_seq
from seq_lib.uart_config import uart_config


class uart_interrupt_seq(uvm_sequence):
    async def body(self):
        await reset_seq("rst").start(self.sequencer)
        regs = ConfigDB().get(None, "", "bus_regs")
        addr = regs.reg_name_to_address
        txe_b, rxf_b, txb_b, rxa_b, brk_b, match_b, fe_b, pre_b, or_b, rto_b = range(10)

        async def read_reg(name):
            rd = read_reg_seq(name, addr[name])
            await rd.start(self.sequencer)
            return rd.result

        async def expect_bit(reg_name, bit_idx, expected, msg):
            value = await read_reg(reg_name)
            bit = (value >> bit_idx) & 1
            assert bit == expected, (
                f"{msg}: {reg_name}[{bit_idx}] expected {expected}, got {bit} "
                f"(0x{value:03x})"
            )

        # Configure UART with TX disabled to avoid FIFO drain races while
        # validating sticky RIS/MIS semantics.
        config = uart_config("config", im=0x3FF, control=0x05)
        await config.start(self.sequencer)

        # TX empty should assert immediately after reset/config with empty TX FIFO.
        await expect_bit("RIS", txe_b, 1, "TX empty flag not asserted at idle")
        await expect_bit("MIS", txe_b, 1, "TX empty masked status incorrect")

        # Fill TX FIFO to exercise TX writes while preserving sticky TXE semantics.
        for i in range(16):
            await write_reg_seq("tx_fill", addr["TXDATA"], i).start(self.sequencer)

        # RIS bits are sticky and remain asserted until cleared via IC.
        await expect_bit("RIS", txe_b, 1, "TX empty sticky RIS flag unexpectedly deasserted")
        await expect_bit("RIS", txb_b, 0, "TX below-threshold unexpectedly asserted")

        # Force TXB with an empty FIFO and threshold=1.
        if "TX_FIFO_FLUSH" in addr:
            await write_reg_seq("tx_flush", addr["TX_FIFO_FLUSH"], 1).start(self.sequencer)
        if "TX_FIFO_THRESHOLD" in addr:
            await write_reg_seq("tx_thr", addr["TX_FIFO_THRESHOLD"], 1).start(self.sequencer)
            await expect_bit("RIS", txb_b, 1, "TX below-threshold not asserted")
            await expect_bit("MIS", txb_b, 1, "TX below-threshold masked status incorrect")

        # Verify mask semantics: only selected enabled bit appears in MIS.
        for bit in range(10):
            await write_reg_seq("im_set", addr["IM"], 1 << bit).start(self.sequencer)
            im_val = await read_reg("IM")
            assert im_val == (1 << bit), (
                f"IM write/read mismatch: expected 0x{1 << bit:03x}, got 0x{im_val:03x}"
            )
            mis = await read_reg("MIS")
            assert (mis & ~(1 << bit)) == 0, (
                f"MIS contains unexpected masked flags for IM=0x{1 << bit:03x}, MIS=0x{mis:03x}"
            )

        # Clear all interrupts and verify RIS/MIS clear behavior.
        await write_reg_seq("ic_clear", addr["IC"], 0x3FF).start(self.sequencer)
        ris = await read_reg("RIS")
        mis = await read_reg("MIS")
        sticky_level_mask = (1 << txe_b) | (1 << txb_b)
        assert mis == 0, f"Interrupt clear failed: MIS=0x{mis:03x}"
        assert (ris & ~sticky_level_mask) == 0, (
            f"Unexpected non-level RIS bits remained set after clear: RIS=0x{ris:03x}"
        )

        # Restore all interrupts
        await write_reg_seq("im_all", addr["IM"], 0x3FF).start(self.sequencer)
