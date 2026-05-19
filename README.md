# Dual-UPF Traffic Steering for 5G Stadium Deployments 🏟️📡

![Status](https://img.shields.io/badge/Status-Peer_Reviewed-success)
![OAI Core](https://img.shields.io/badge/OAI-5G_Core-blue)
![Python](https://img.shields.io/badge/Python-3.8+-yellow)

This repository contains the emulation and simulation framework for the research paper: **"Dual-UPF Traffic Steering for 5G Network Slices in Stadium and Mass Event Deployments."** 

It provides a full-scale 5G network environment specifically engineered to handle extreme peak-load scenarios (e.g., stadium halftime shows). The core of the project is an **Evolutionary Game Theory (EGT)** steering controller that dynamically distributes PDU sessions between a capacity-constrained **MEC (Edge)** UPF and a high-capacity **Central Cloud (CC)** UPF, ensuring fairness across eMBB and URLLC network slices.

---

## 🎯 What This Project Does

This project bridges the gap between theoretical game theory and practical 5G Core implementations:

1. **Massive Control-Plane Emulation**: Uses a containerized **OpenAirInterface (OAI) 5G Core** and a heavily optimized, multiplexed `gnbsim` engine to successfully provision **1,000 concurrent PDU sessions** (100% success rate at the AMF/SMF layer, assuming ideal radio conditions).
2. **Dynamic Traffic Steering**: Runs a Python-based **EGT Replicator Dynamics** controller that polls the SMF for session states and calculates optimal anchor routing fractions ($x_{mec}$, $x_{cc}$) to minimize end-to-end delay without overloading the edge.
3. **Data-Plane QoS Simulation**: Utilizes a robust analytical queuing model to simulate extreme data-plane traffic surges (up to $10\times$ baseline load) and measure Packet Delay Budget (PDB) violations across standard and stress-test scenarios.

> **Note on Scope**: The OAI testbed handles the *control-plane scalability* (N1/N2/N4 signalling), while the EGT script computes the *data-plane QoS performance* offline using rigorous mathematical models calibrated to physical hardware metrics.

---

## 🚀 Key Features

*   **Multi-Slice Support**: Differentiates between **eMBB** (high throughput, 300ms PDB) and **URLLC** (low latency AR/VR rendering, 10ms PDB).
*   **Warm-Start Stabilization**: The EGT controller tracks load continuously, preventing discrete-time vanishing-gradient arrests and boundary collapses under extreme demand spikes.
*   **Dual-UPF Architecture**: Simulates a 10:1 cloud-to-edge processing capacity ratio, forcing the controller to intelligently spill eMBB traffic to the cloud while preserving the MEC for latency-critical URLLC sessions.
*   **High-Performance Multiplexing**: Re-engineered the Go-based `gnbsim` simulator with $O(1)$ lookup maps, allowing a single virtual gNB to handle thousands of GTP tunnels simultaneously.

---

## 🏗️ System Architecture

The environment relies on a complete 5G Service-Based Architecture (SBA) deployed via Docker Compose:

*   **Control Plane**: AMF, SMF, NRF, UDR, UDM, AUSF, NSSF.
*   **User Plane Elements**: 
    *   **UPF-MEC**: Local edge processing (Low latency: 0.25ms, limited capacity).
    *   **UPF-CC**: Central cloud processing (High latency: 1.0ms, high capacity).
*   **Access Plane**: `gnbsim` multiplexed emulator connecting 800 eMBB users and 200 URLLC users.
*   **EGT Controller**: Python agent acting as a centralized policy engine interfacing with the SMF.

---

## 💻 Quick Start & Execution Guide

### 1. Prerequisites
Ensure your host machine has at least **16GB RAM** and **4 CPU cores**.
*   Docker & Docker Compose v2
*   Python 3.8+ with dependencies: `pip install numpy matplotlib requests paramiko`

### 2. Deploy the 5G SBA Core
Bring up the OAI network functions and the dual UPFs:
```bash
docker compose up -d
```
Check `docker ps` to ensure all containers report a "healthy" state.

### 3. Provision the Database
The UDM/UDR MySQL database must be populated with the 1,000 UE subscriber identities that match the `gnbsim` configuration:
```bash
docker exec -i mysql mysql -uroot -plinux < provision_1000.sql
```

### 4. Establish 1,000 PDU Sessions
Trigger the multiplexed emulator to attach the UEs to the core:
```bash
docker compose restart gnbsim
```
**Verification:** Check the gnbsim logs. You should see successful camp messages for all UEs:
```bash
docker logs gnbsim | grep "camped" | tail -n 5
# Output: [UE 1000] MSIN=0000001000 SST=2 DNN=oai2 camped
```

### 5. Run the EGT Stadium Simulation
Execute the multi-scenario analytical script to evaluate how the EGT controller steers traffic during the 3-phase stadium event (Ramp-up, Halftime Peak, Dispersal):
```bash
python3 multi_scenario_sim.py
```
This generates the core outputs, delay graphs, and QoS violation reports in the `results/` directory.

---

## ⚙️ Understanding the EGT Controller Parameters

The core logic lives in `egt_controller.py`. Modifying the `SystemParams` allows you to test entirely different network architectures:

*   **$M_1$, $M_2$ (Population Size)**: Dictates the base load. Increasing the URLLC population ($M_2$) rapidly saturates the MEC, potentially triggering unavoidable QoS violations if hardware capacity is exceeded.
*   **$k_{mec}$, $k_{cc}$ (Processing Exponents)**: These dictate UPF capacity. Halving $k_{mec}$ simulates upgrading the Edge server CPU, allowing it to absorb more URLLC traffic before delays spike exponentially.
*   **$\beta$ (Replicator Speed)**: Controls how aggressively traffic shifts between UPFs. High $\beta$ causes rapid adaptation but risks oscillation; low $\beta$ ensures smooth but slow convergence.
*   **$PDB_{embb}$, $PDB_{urllc}$**: Delay thresholds (300ms / 10ms). Used for compliance monitoring. *Note: Future iterations of the algorithm aim to integrate PDB directly into the payoff function.*

---

## 📂 Repository Structure

*   `config/`: NF configuration files (`amf.conf`, `smf.conf`, `gnbsim.json`, etc.).
*   `paper/`: LaTeX source code for the associated peer-reviewed manuscript.
*   `src/python/`: The Python-based EGT algorithm (`egt_controller.py`).
*   `gnbsim/`: High-performance Go source code for multi-UE multiplexing.
*   `verify_claims.py`: Reproducibility script to empirically validate all numerical claims made in the paper.

---

## 📖 References
1. **Alevizaki et al.**, *"Dynamic Selection of User Plane Function in 5G Environments"*, IFIP Networking 2021.
2. **3GPP TS 23.501**, *"System architecture for the 5G System (5GS)"*.
3. **OpenAirInterface (OAI)**, *CN5G Project*.

---
*Maintained by Ajay Chander Ravichandran | IMT Atlantique, France | 2026*
