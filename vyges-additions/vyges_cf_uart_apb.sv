// Copyright 2026 Vyges. SPDX-License-Identifier: Apache-2.0
//
// vyges_cf_uart_apb — Vyges integration overlay for ChipFoundry CF_UART_APB.
//
// Presents the SoC-standard peripheral interface (clk_i / rst_ni + a clean APB4
// slave + rx/tx/IRQ) so the *generic* Vyges SoC generator wires it like any other
// peripheral — keeping IP-specific handling OUT of the generator. Maps
// clk_i -> PCLK, rst_ni (active-low) -> PRESETn, and ties off the DFT pin.
// Works around upstream CF_UART metadata exposing 3 slash-joined bus variants
// (WB/APB/AHBL) and PCLK/PRESETn (not clk_i/rst_ni).
module vyges_cf_uart_apb (
  input  wire        clk_i,
  input  wire        rst_ni,
  // APB4 slave
  input  wire [31:0] PADDR,
  input  wire        PWRITE,
  input  wire [31:0] PWDATA,
  input  wire        PSEL,
  input  wire        PENABLE,
  output wire        PREADY,
  output wire [31:0] PRDATA,
  // UART IO + interrupt
  input  wire        rx,
  output wire        tx,
  output wire        IRQ
);
  CF_UART_APB u_cf_uart_apb (
    .sc_testmode (1'b0),       // DFT scan disabled in functional integration
    .PCLK        (clk_i),
    .PRESETn     (rst_ni),
    .PADDR       (PADDR),
    .PWRITE      (PWRITE),
    .PWDATA      (PWDATA),
    .PSEL        (PSEL),
    .PENABLE     (PENABLE),
    .PREADY      (PREADY),
    .PRDATA      (PRDATA),
    .IRQ         (IRQ),
    .rx          (rx),
    .tx          (tx)
  );
endmodule
