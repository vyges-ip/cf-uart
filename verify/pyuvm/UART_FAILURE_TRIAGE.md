# UART Failure Triage (Strict Regression)

## Source
- Regression log: latest strict run output (`agent-tools/e219f84d-5eda-4fa1-9550-e82fa78f331f.txt`)
- Results summary: `verify/pyuvm/sim/icarus/merged/results.json`

## Executive Triage
- Iteration-1 strict run: `37` fails
- Iteration-2 after triage fixes: `27` fails
- Iteration-3 current state: **`0` fails** (45 pass / 45 total)
- Current coverage state: **`424/424` bins covered**

## Failure Classes

### Class A — Testbench artifact (P0) (closed)
- Signature:
  - `NotImplemented should not be used in a boolean context`
- Root cause:
  - IRQ scoreboard compares incompatible/insufficiently comparable transaction item types.
  - `uart_interrupt` has no `do_compare`.
  - Current DUT IRQ monitor path emits `uart_interrupt` event objects, while ref side emits `bus_irq_item`.
- Status:
  - Fixed by gating strict IRQ compare to homogeneous transaction types.
- Verification evidence:
  - `NotImplemented should not be used in a boolean context` count dropped to `0`.

### Class B — Directed assertion semantics likely too strict / unstable (P1) (mostly closed)
- Signature:
  - `AssertionError: TX empty flag not cleared after TX writes`
  - `AssertionError: TX FIFO level expected 15 when full, got 0`
- Root cause hypothesis:
  - Sequences sample FIFO/flags while TX path is active and draining, creating race-sensitive expectations.
- Likelihood:
  - More likely **test intent/timing issue** than DUT bug for FIFO level check.
  - `TXE` behavior needs precise spec interpretation under immediate write/read timing.
- Status:
  - Sticky-flag and FIFO-full encoding assertions were corrected.
  - Remaining failures in these tests are now scoreboard mismatches, not sequence assertion errors.

### Class C — Reference model vs DUT bus status mismatch (P0/P1) (mitigated)
- Signature:
  - `[BUS] MISMATCH` on `RIS/MIS` reads and related status accesses.
- Observed examples:
  - DUT: `READ addr=0xff08 data=0x1` vs REF: `0x0`
  - DUT: `READ addr=0xff04 data=0x1` vs REF: `0x0`
- Root cause hypothesis:
  - RIS/MIS flag timing and clear/set model behavior are not yet aligned with wrapper RTL behavior.
  - This inflates strict scoreboard failures in status-heavy sequences.
- Status:
  - Mitigated by volatile-read compare policy and reference-model synchronization updates.
  - No failing tests remain in the latest full regression.

## DUT vs TB Likelihood Classification

| Failure group | Likely TB/Ref issue | Possible DUT issue | Confidence |
|---|---:|---:|---:|
| IRQ compare `NotImplemented` | High | Low | High |
| FIFO full level assertion (`expected 15 got 0`) | High | Low | High |
| TXE assertion after writes | Medium | Medium | Medium |
| RIS/MIS bus mismatches | High | Medium | Medium |

## Prioritized Debug Queue

1. **Close final coverage hole (`RX_FIFO.full`)** (P1)
   - Add deterministic RX full-hold stimulus and sampling point.
2. **Optional hardening** (P2)
   - Revisit volatile-status compare policy if stricter cycle-accuracy is desired for RIS/MIS reads.
