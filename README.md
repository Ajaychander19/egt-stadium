# EGT Stadium 5G — Project Documentation

## Project Goal

Implement and validate a multi-UPF traffic steering system for 5G stadium/mass-event deployments using Evolutionary Game Theory (EGT), running on a real OAI CN5G emulation testbed with two UPF instances (MEC edge + Central Cloud), and demonstrate that the EGT controller achieves fair load distribution and QoS compliance across eMBB and URLLC network slices.

---

## System Architecture

```
Stadium UEs (eMBB SST=1, URLLC SST=2)
         ↓ radio (rfsim)
    OAI gNB (RF simulator)
         ↓ N2/NGAP
    OAI AMF ←→ NRF ←→ NSSF
         ↓
    OAI SMF ←→ UDM/UDR/AUSF
       ↙  ↘  N4/PFCP
UPF-MEC    UPF-CC
(edge,     (central,
low lat)   high cap)
       ↕
EGT Controller (Python)
polls SMF → computes x(t) → steers new PDU sessions
```

---

## What Is Done ✓

### 1. EGT Algorithm — Validated

- Implemented replicator dynamics from Alevizaki et al. (2021)
- **Delay model:** local UPF dedicated per group, central UPF shared
- **Validated k values:** k_mec = 4.833e-04, k_cc = 4.833e-05 (ratio = 10)
- **Equilibrium result:** G1@MEC = 17.8%, G2@MEC = 32.0% — matches Alevizaki Fig. 2
- Convergence in ~230 iterations (paper: < 300)
- File: `egt_controller.py`

### 2. Stadium Simulation — Complete

- Three load phases modelled from real-world measurements (Super Bowl LVII)
- Phase I (ramp-up, ×1.0): zero violations, EGT steers toward MEC
- Phase II (peak, ×5.5 halftime spike): EGT redistributes to CC, URLLC infra-limited
- Phase III (dispersal, ×0.3): traffic reverts to MEC
- eMBB violations: zero across all phases
- URLLC Phase II: infrastructure-limited (both UPFs exceed 10ms PDB at ×5.5)
- QoS compliance: 53.3% of time steps violation-free
- File: `stadium_simulation.py`

### 3. Paper Figures — Generated

| Figure | Content | File |
| --- | --- | --- |
| Fig 2 reproduction | Alevizaki validation | `results/fig2_reproduction.png` |
| Fig (a) | Population fractions x(t) | `results/stadium_results.png` |
| Fig (b) | E2E delay per slice/UPF | same |
| Fig (c) | QoS violations + infra-limited | same |
| Fig (d) | Load profile vs convergence speed | same |

### 4. OAI CN5G Core — Running

All 9 network functions healthy on Docker:

| Container | Function | IP |
| --- | --- | --- |
| mysql | Subscriber DB | 192.168.70.131 |
| oai-nrf | NF Registry | 192.168.70.130 |
| oai-udr | User Data Repo | 192.168.70.136 |
| oai-udm | User Data Mgmt | 192.168.70.137 |
| oai-ausf | Authentication | 192.168.70.138 |
| oai-nssf | Slice Selection | 192.168.70.139 |
| oai-amf | Access & Mobility | 192.168.70.132 |
| oai-smf | Session Mgmt | 192.168.70.133 |
| oai-upf-mec | UPF edge node | 192.168.70.140 |
| oai-upf-cc | UPF central | 192.168.70.141 |

### 5. Two-UPF Architecture — Confirmed

- Both UPFs registered with NRF
- Both UPFs have PFCP associations with SMF (heartbeat confirmed)
- SMF configured with two DNN entries: `oai` (eMBB) and `oai2` (URLLC)
- Slice mapping: SST=1→UPF-MEC/CC, SST=2→UPF-MEC/CC (EGT decides)
- Config: `config/stadium_config.yaml`

### 6. gNB — Running and Registered

- OAI gNB v2.1.0 with RF simulator
- NG Setup Response received from AMF
- Cell 12345678 in service, PLMN 001.01
- rfsim server listening on port 4043
- Config: `config/gnb.conf`

---

## What Is In Progress ⟳

### UE Attachment — gnbsim approach

The OAI nrUE binary has a PHY band resolution issue in v2.1.0. Switching to **gnbsim** — OAI's own gNB+UE simulator that directly implements N2/NGAP without radio simulation. gnbsim proves the complete call flow: Registration → Authentication → PDU Session Establishment → Data plane, which is what the paper needs for testbed validation.

---

## What Remains ✗

| Item | Effort |
| --- | --- |
| gnbsim UE attach (eMBB SST=1) | In progress now |
| gnbsim UE attach (URLLC SST=2) | 30 min |
| Confirm PDU session lands on correct UPF | 15 min |
| Run stadium simulation with `--smf` flag (live data) | 10 min |
| Data plane ping through UPF tunnel | 15 min |
| Write Results section of paper | Your work |

---

## End Goal

A complete working system where:

1. **gnbsim** establishes PDU sessions for both eMBB (SST=1) and URLLC (SST=2) UEs through the OAI 5G core
2. **SMF** selects UPF-MEC or UPF-CC for each session based on slice type
3. **EGT controller** polls the SMF, reads live session counts, updates population state x(t), and steers new sessions toward equilibrium
4. **Stadium simulation** runs with `-smf http://localhost:8080` using real session data
5. All four paper figures show real OAI data + EGT steering decisions

---

## Tests for the Paper

### Test 1 — EGT Algorithm Validation (done)

Reproduce Alevizaki et al. Fig. 2 with M1=130, M2=70. Confirms mathematical correctness of implementation.

### Test 2 — Stadium 3-Phase Simulation (done)

Run full 95-minute stadium scenario (ramp-up / peak+halftime / dispersal). Show EGT redistributes sessions between UPFs in response to load, maintaining eMBB PDB=300ms and URLLC PDB=10ms where possible.

### Test 3 — OAI Testbed PDU Session Establishment (in progress)

Use gnbsim to establish real PDU sessions through OAI CN5G. Confirm: AMF registration, SMF session selection, UPF anchor assignment, N4/PFCP rule installation.

### Test 4 — EGT Live Integration (pending Test 3)

Run `python3 stadium_simulation.py --smf http://localhost:8080`. EGT controller polls real SMF session counts and incorporates them into x(t). Demonstrate that real UPF load data influences the equilibrium steering decisions.

### Test 5 — Two-UPF Fairness Verification (pending Test 3)

At normal load: confirm sessions split between UPF-MEC and UPF-CC at the EGT equilibrium ratio. At peak load (×5.5): confirm EGT correctly offloads to UPF-CC, verify both UPFs receive traffic, verify eMBB remains QoS-compliant.

---

## Key Parameters (Table I of your paper)

| Parameter | Value | Source |
| --- | --- | --- |
| M1 (eMBB UEs) | 800 | Stadium scenario |
| M2 (URLLC UEs) | 200 | Stadium scenario |
| ρ_eMBB | 10 Mbps/UE | Super Bowl ref |
| ρ_URLLC | 25 Mbps/UE | AR/VR offload |
| t_prop_MEC | 0.25 ms | 50km fibre |
| t_prop_CC | 1.0 ms | 200km fibre |
| k_mec | 4.833e-04 | Grid search calibrated |
| k_cc | 4.833e-05 | k_mec/k_cc = 10 |
| PDB_eMBB | 300 ms | 3GPP 5QI 6 |
| PDB_URLLC | 10 ms | 3GPP 5QI 82 |
| Halftime spike | ×5.5 | Super Bowl LVII |

---

## File Structure

```
~/egt-stadium/
├── egt_controller.py          ← EGT algorithm (validated)
├── validate_fig2.py           ← Alevizaki reproduction
├── stadium_simulation.py      ← 3-phase paper results
├── verify_status.py           ← Project health check
├── docker-compose.yaml        ← Full OAI stack
├── oai_db.sql                 ← Subscribers (2 UEs)
├── config/
│   ├── stadium_config.yaml    ← Shared NF config
│   ├── nssf_slice_config.yaml ← Slice definitions
│   ├── gnb.conf               ← gNB rfsim config
│   ├── gnbsim.yaml            ← gnbsim UE profiles
│   ├── ue_embb.conf           ← UE-1 (SST=1)
│   └── ue_urllc.conf          ← UE-2 (SST=2)
└── results/
    ├── fig2_reproduction.png
    ├── stadium_results.png
    └── stadium_results.json
```
