// Copyright 2026 Vyges. SPDX-License-Identifier: Apache-2.0
//
// vyges_cf_uart_apb — Vyges integration overlay for ChipFoundry CF_UART_APB.
//
// Presents the SoC-standard peripheral interface so the *generic* Vyges SoC
// generator wires it like any other APB slave — keeping IP-specific handling
// OUT of the generator. Exposes the Vyges APB-slave contract (lowercase _i/_o,
// same as fft/mag_phase/temp/humidistat) and maps to CF_UART_APB's AMBA-style
// PCLK/PRESETn/PSEL/... ports internally. clk_i -> PCLK, rst_ni -> PRESETn.
module vyges_cf_uart_apb (
  input  wire        clk_i,
  input  wire        rst_ni,
  // APB4 slave — Vyges contract (lowercase _i/_o)
  input  wire        psel_i,
  input  wire        penable_i,
  input  wire        pwrite_i,
  input  wire [31:0] paddr_i,
  input  wire [31:0] pwdata_i,
  output wire [31:0] prdata_o,
  output wire        pready_o,
  // UART IO + interrupt
  input  wire        rx,
  output wire        tx,
  output wire        IRQ
);
  CF_UART_APB u_cf_uart_apb (
    .PCLK        (clk_i),
    .PRESETn     (rst_ni),
    .PADDR       (paddr_i),
    .PWRITE      (pwrite_i),
    .PWDATA      (pwdata_i),
    .PSEL        (psel_i),
    .PENABLE     (penable_i),
    .PREADY      (pready_o),
    .PRDATA      (prdata_o),
    .IRQ         (IRQ),
    .rx          (rx),
    .tx          (tx)
  );
endmodule
