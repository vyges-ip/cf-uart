# UART Verification Traceability and Gap Report

## Scope
- IP: `CF_UART`
- Verification stack: `verify/pyuvm`
- Buses in regression: `APB`, `AHB`, `WISHBONE`

## Feature -> Coverage -> Test Traceability

| UART functionality | Coverage points | Tests/sequences driving it | Checker strength | Current gaps |
|---|---|---|---|---|
| Enable and mode control (`CTRL.en/txen/rxen/lpen/gfen`) | `top.ip.reg.CTRL.*`, `top.ip.cross.CTRL.*`, `top.ip.Loopback`, `top.ip.GlitchFilter` | `uart_config`, `coverage_closure_seq`, `uart_loopback_seq`, `uart_glitch_filter_seq` | Medium | No direct assertions for every control permutation |
| Frame format (`CFG.wlen/stp2/parity`) | `top.ip.reg.CFG.*`, `top.ip.cross.CFG.*`, `top.ip.TX/RX.Len{5..9}.Char`, `top.ip.TX/RX.Len{5..9}.Parity`, `top.ip.StopBits` | `tx_length_parity_seq`, `rx_length_parity_seq`, `coverage_closure_seq` | Medium | Illegal parity encodings were previously untracked |
| Baud/prescaler (`PR`) | `top.ip.reg.PR` | `uart_prescalar_seq`, `coverage_closure_seq` | Low-Medium | Stress depth was limited; boundary behavior under-asserted |
| TX data path | TX char/parity bins, FIFO level bins, `TXE/TXB` flags | `uart_tx_seq`, `tx_length_parity_seq`, `uart_fifo_seq`, `coverage_closure_seq` | Medium | Most tests previously read status without expected-value checks |
| RX data path | RX char/parity bins, FIFO level bins, `RXF/RXA` flags | `uart_rx_seq`, `rx_length_parity_seq`, `uart_fifo_seq`, `coverage_closure_seq` | Medium | RX char coverage was partially inflated by synthesized bus-read sampling |
| Loopback | `top.ip.Loopback`, RX/TX semantic bins | `uart_loopback_seq`, `uart_match_seq` | High | Good check exists; broadening corner combinations still needed |
| Match detection | `top.ip.reg.MATCH`, `top.ip.flag.MATCH`, `top.ip.Match` | `uart_match_seq`, `coverage_closure_seq` | Medium | Needed explicit RIS-bit assertions |
| Timeout detection | `top.ip.reg.CFG.timeout`, `top.ip.flag.RTO`, `top.ip.Errors.Timeout` | `uart_timeout_seq`, `coverage_closure_seq` | Medium | Needed explicit set/clear assertions |
| Frame/parity error detection | `top.ip.flag.FE/PRE`, `top.ip.Errors.FrameError/ParityError` | `uart_frame_error_seq`, `uart_parity_error_seq`, `coverage_closure_seq` | Medium | Needed direct expected-bit assertions |
| Overrun | `top.ip.flag.OR`, `top.ip.Errors.Overrun` | `uart_fifo_seq`, `coverage_closure_seq` | Low-Medium | Overrun lifecycle and recovery checks were weak |
| Break detection | `top.ip.flag.BRK`, `top.ip.Errors.Break` | `coverage_closure_seq` | Medium | Dedicated directed test is still missing |
| Interrupt architecture (`IM/RIS/MIS/IC`, `IRQ`) | `top.ip.flag.*`, `top.ip.flag.any_masked_irq` | `uart_interrupt_seq`, `coverage_closure_seq` | Medium | Needed strong bit-accurate checks and IRQ compare-path wiring |

## Checker Architecture Review

- **Bus scoreboard** compares monitor transactions vs reference-model bus predictions.
- **IP scoreboard** compares UART monitor transactions vs reference-model IP predictions.
- **IRQ scoreboard** compares DUT IRQ monitor events vs reference-model IRQ predictions.

### Identified high-impact weaknesses (pre-fix baseline)
- UART compare ignored `parity` and `word_length`.
- IRQ DUT monitor stream was not connected to the scoreboard in UART env.
- Reference-model interrupt bit mapping semantics were inconsistent with RTL/YAML definitions.
- Most directed sequences stimulated behavior but did not assert expected outcomes.

## Coverage Model Review

- Strong breadth exists across register fields, mode coverage, FIFO levels, flags, and TX/RX semantic bins.
- Cross-coverage intent was present but one major closure hole existed (`stp2 x timeout` patterning in closure sequence).
- RX semantic coverage sampling needed refinement to avoid counting synthetic values from plain bus reads as real RX behavior.

## Prioritized Gaps

### P0
- Strengthen compare semantics (`char + direction + parity + word_length`).
- Ensure IRQ/IP checker paths are truly active and fed.
- Add explicit assertions to interrupt/error/timeout/match/FIFO/glitch tests.

### P1
- Refine coverage model representativeness (RX sampling path, cross closure patterning, reserved parity encodings).
- Add stronger boundary/negative tests (mask/clear transitions, reset-mid-activity, stop/parity combined faults).

### P2
- Wrapper/documentation consistency cleanup (`IC` readback behavior across wrappers, minor register-description typos).

## Signoff Recommendation

- Functional coverage closure should only be considered valid when paired with:
  - assertion-backed directed checks per feature,
  - active IP/IRQ scoreboard comparisons,
  - and evidence that coverage hits correspond to real protocol behavior (not only synthetic register-derived sampling).
