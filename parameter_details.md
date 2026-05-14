# EGT Stadium — Parameter Details
**Source**: ResearchPaperv1(5).pdf — TABLE I: System, Slice, and Algorithm Parameters

---

## Network Topology Parameters

| Symbol | Paper Value | Old Value | New Value | Status | Notes |
|:-------|:------------|:----------|:----------|:-------|:------|
| C_mec | 40 CPU cores | Not defined | 100 units (NRF) | Updated | Ratio 1:10 preserved |
| C_cc | 120 CPU cores | Not defined | 1000 units (NRF) | Updated | 10x MEC |
| Link bandwidth | 10 Gbps | Not modeled | Not modeled | Inherited | Docker bridge |
| t_prop_mec | 0.25 ms | 0.25 ms | 0.25 ms | Match | |
| t_prop_cc | 1.0 ms | 1.0 ms | 1.0 ms | Match | |

---

## Slice Parameters (3GPP TS 22.261, TS 23.501)

| Symbol | Paper Value | Old Value | New Value | Status | Notes |
|:-------|:------------|:----------|:----------|:-------|:------|
| M1 (eMBB UEs) | 800 | 800 | 800 | Match | SST=1 |
| M2 (URLLC UEs) | 200 | 200 | 200 | Match | SST=2 |
| rho_eMBB | 10 Mbps | 10.0 | 10.0 | Match | |
| rho_URLLC | 25 Mbps | 25.0 | 25.0 | Match | AR/VR offload |
| PDB_eMBB | 300 ms | 300.0 ms | 300.0 ms | Match | 5QI=6 |
| PDB_URLLC | 10 ms | 10.0 ms | 10.0 ms | CORRECT | 5QI=82, Delay-Critical GBR |
| DNN (eMBB) | oai | oai only on UPF-CC | oai + oai2 on BOTH UPFs | Updated | |
| DNN (URLLC) | oai2 | oai2 only on UPF-MEC | oai + oai2 on BOTH UPFs | Updated | Spillover enabled |

---

## UPF Delay Model (Alevizaki [3])

| Symbol | Paper Value | Old Value | New Value | Status |
|:-------|:------------|:----------|:----------|:-------|
| k_mec | Grid-searched | 4.833e-04 | 4.833e-04 | Match |
| k_cc | Grid-searched | 4.833e-05 | 4.833e-05 | Match |
| k_mec/k_cc ratio | 10x | 10x | 10x | Match |

---

## EGT Algorithm Parameters

| Symbol | Paper Value | Old Value | New Value | Status |
|:-------|:------------|:----------|:----------|:-------|
| beta (replicator speed) | beta > 0 | 1.0 | 1.0 | Match |
| epsilon (convergence) | — | 0.01 | 0.01 | Match |
| Phase II halftime spike | 5.5x | 5.5 | 5.5 | Match |
| Phase I duration | 30 min | 30 min | 30 min | Match |
| Phase II duration | 45 min | 45 min | 45 min | Match |
| Phase III duration | 20 min | 20 min | 20 min | Match |

---

## UPF Configuration Changes (New)

| Parameter | Old Config | New Config |
|:----------|:----------|:----------|
| UPF-MEC DNNs | oai2 only | oai + oai2 (both slices) |
| UPF-CC DNNs | oai only | oai + oai2 (both slices) |
| Config file | Shared stadium_config.yaml | Independent upf_mec.yaml / upf_cc.yaml |
| NRF Capacity MEC | Not set | 100 units |
| NRF Capacity CC | Not set | 1000 units |
| NRF Priority MEC | Not set | 50 |
| NRF Priority CC | Not set | 100 |

---

## URLLC PDB Clarification

**Correct PDB_URLLC = 10 ms** (5QI=82, Delay-Critical GBR, 3GPP TS 22.261)
The paper table had a formatting artifact showing '1020' — confirmed correct value is 10 ms.
The egt_controller.py already uses PDB_urllc = 10.0 — no code change required.

---
Generated: 2026-05-14 | Reference: ResearchPaperv1(5).pdf Table I
