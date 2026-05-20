"""Read RXDATA register sequence."""

from pyuvm import uvm_sequence, ConfigDB

from cf_verify.bus_env.bus_seq_lib import read_reg_seq


class uart_rx_read(uvm_sequence):
    async def body(self):
        regs = ConfigDB().get(None, "", "bus_regs")
        addr = regs.reg_name_to_address
        rd = read_reg_seq("rx_rd", addr["RXDATA"])
        await rd.start(self.sequencer)
