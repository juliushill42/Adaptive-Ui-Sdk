# Adaptive UI SDK

**T21-143** · `adaptive-ui-sdk`

A local deterministic interface-adaptation runtime that resolves a device profile, records runtime observations, and changes presentation density from measured latency.

## Implemented

### Device/context resolution

The current classifier resolves:

- `offline` when connectivity is unavailable.
- `phone-narrow` for phone devices or widths below 600 px.
- `tablet` below 1100 px.
- `desktop` at 1100 px and above.

### Observation

Sessions record latency observations in milliseconds.

### Adaptation

If at least two observations exceed 250 ms, the session resolves to:

```text
density: compact
```

Otherwise:

```text
density: comfortable
```

All state transitions are stored in SQLite and linked into a SHA-256 record chain.

## Proof path

The shipped proof:

1. Resolves a 390 px phone session.
2. Records three latency observations.
3. Detects two observations above 250 ms.
4. Adapts the session to compact density.
5. Verifies record-chain integrity.

```bash
./boot143.sh verify
```

## Run

```bash
./boot143.sh doctor
./boot143.sh verify
./boot143.sh up
```

Default endpoint:

```text
http://127.0.0.1:8765
```

Routes:

```text
GET  /health
GET  /healthz
POST /proof
```

## Repository layout

```text
apps/web/               browser proof surface
services/api/engine.py  classification, observation, adaptation
services/api/common.py  SQLite + SHA-256 record chain
services/api/server.py  local HTTP server
tests/test_proof.py     end-to-end proof
data/                   local state
boot143.sh              doctor / verify / up launcher
```

## Current boundary

This build proves deterministic adaptation rules and persisted evidence. It is not claiming a full production UI framework or learned preference model in this repository.

## Ownership

Owner: Julius Cameron Hill / Titan Universal AI LLC  
Watermark: `":"`
