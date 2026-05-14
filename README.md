# Capacity-Aware 5G Stadium Emulation with EGT-Based UPF Selection

This repository contains a full-scale 5G network emulation environment designed for high-density stadium scenarios. It leverages an **Evolutionary Game Theory (EGT)** model to dynamically select between **MEC (Edge)** and **Central Cloud (CC)** User Plane Functions based on capacity constraints and service requirements (eMBB vs. URLLC).

The project is built on the **OpenAirInterface (OAI) 5G Core** and features a high-performance, multiplexed GNB/UE simulator capable of handling **1,000 concurrent physical UEs**.

## 🚀 Key Accomplishments
- **1,000 UE Scale**: Successfully emulated 1,000 physical UEs (800 eMBB / 200 URLLC) with 100% PDU session establishment success.
- **EGT-Based Steering**: Implemented the replicator dynamics model from **Alevizaki et al.** to ensure Nash Equilibrium and fairness in UPF selection.
- **Dual-UPF Architecture**: Deployed independent MEC and Cloud UPFs with a 1:10 capacity ratio and multi-slice support (spillover enabled).
- **High-Performance Multiplexing**: Re-engineered the `gnbsim` Go engine with $O(1)$ lookup maps to handle thousands of GTP tunnels on a single virtual gNB.

---

## 🏗 System Architecture

The environment consists of a complete 5G Service-Based Architecture (SBA) deployed via Docker:

- **Control Plane**: AMF, SMF, NRF, UDR, UDM, AUSF, NSSF.
- **User Plane**: 
  - **UPF-MEC**: Local edge processing (Low latency, limited capacity).
  - **UPF-CC**: Central cloud processing (High latency, high capacity).
- **Access Plane**: `gnbsim` multiplexed emulator (800 eMBB users, 200 URLLC users).

---

## 📊 Theoretical Model & Parameters

The system follows the delay model and EGT dynamics specified in **"Dynamic Selection of User Plane Function in 5G Environments" (Alevizaki et al.)**.

### System Parameters
| Parameter | Value | Description |
| :--- | :--- | :--- |
| **$M_1$ (eMBB)** | 800 | Population group 1 (10 Mbps/UE) |
| **$M_2$ (URLLC)**| 200 | Population group 2 (25 Mbps/UE) |
| **$k_{mec} / k_{cc}$**| 10 | Capacity ratio (Cloud is 10x Edge) |
| **$t_{prop}$ Ratio** | 4:1 | Cloud is 4x further than Edge |
| **$PDB_{urllc}$** | 10 ms | Strict 3GPP Delay-Critical GBR target |
| **$PDB_{embb}$** | 300 ms | Standard eMBB target |

---

## 💻 Detailed Execution Guide

### 1. Prerequisites
Before running the platform, ensure your environment meets the following requirements:
*   **Docker & Docker Compose**: Installed and running.
*   **Python 3.8+**: With the following packages:
    ```bash
    pip install numpy matplotlib requests paramiko
    ```
*   **System Resources**: Minimum 16GB RAM and 4 CPU cores recommended for 1,000-UE emulation.

### 2. Platform Deployment
Follow these steps to initialize the 5G Core and Simulator:

#### Step A: Initialize the OAI Core
Deploy the 5G Stack (AMF, SMF, UPFs, etc.):
```bash
docker compose up -d
```
Verify that all 9 containers are "healthy" using `docker ps`.

#### Step B: Provision the Subscriber Database
The MySQL database must be populated with the 1,000 UE identities matching the `gnbsim` configuration:
```bash
# This script inserts 1,000 UEs into the 'oai_db'
docker exec -i mysql mysql -uroot -plinux < provision_1000.sql
```

#### Step C: Start the Stadium Emulator
The `gnbsim` container handles the physical attachment of the UEs:
```bash
# Restart to ensure it picks up the latest config/gnbsim.json
docker compose restart gnbsim
```

### 3. Running the EGT Simulations
You can run different simulation scenarios to test the steering logic.

*   **Standard Stadium Simulation**: Runs the 3-phase (Ramp-up, Peak, Dispersal) scenario.
    ```bash
    python3 multi_scenario_sim.py
    ```
*   **Individual Testing**: You can manually trigger the EGT controller to verify convergence for a specific load:
    ```python
    from egt_controller import EGTController, SystemParams
    ctrl = EGTController(SystemParams(M1=800, M2=200))
    results = ctrl.run_to_equilibrium(load_mult=5.5) # Simulate Halftime Peak
    print(results['equilibrium'])
    ```

---

## ✅ Testing & Verification

### 1. Verify UE Attachment
Check the `gnbsim` logs to ensure all UEs have successfully established PDU sessions:
```bash
docker logs gnbsim | grep "camped" | tail -n 20
```
You should see: `[UE 1000] MSIN=0000001000 SST=2 DNN=oai2 camped`.

### 2. Monitor Traffic Steering
To verify that traffic is actually being steered between the MEC and Cloud UPFs, monitor the SMF logs:
```bash
docker logs oai-smf | grep "Selection"
```
Or use the EGT controller's built-in polling tool to see live session counts:
```python
ctrl.poll_smf()
print(ctrl.status()) # Shows x_fraction and delays per UPF
```

---

## ⚙️ Scaling & Customization
To customize the simulation for your own research, you can modify the following files:

*   **Population**: Edit `M1` (eMBB) and `M2` (URLLC) in `egt_controller.py`.
*   **Capacity Constraints**: Adjust `k_mec` and `k_cc` in `egt_controller.py` to change the Edge/Cloud performance ratio.
*   **QoS Requirements**: Modify `PDB_embb` (default 300ms) or `PDB_urllc` (default 10ms) to test different service standards.
*   **Network Scale**: To go beyond 1,000 UEs, generate a new `gnbsim.json` and matching `provision_XXXX.sql` script.

---

## 📂 Repository Structure
- `config/`: Configuration files for AMF, SMF, UPFs, and GNBSIM.
- `results/`: Output charts and JSON metrics from the latest simulations.
- `egt_controller.py`: The core Evolutionary Game Theory logic.
- `multi_scenario_sim.py`: Automated tester for stadium scenarios.
- `gnbsim/`: Optimized Go source code for multi-UE multiplexing.

---

## 📖 References
1. **Alevizaki et al.**, *"Dynamic Selection of User Plane Function in 5G Environments"*, IFIP 2021.
2. **3GPP TS 23.501**, *"System architecture for the 5G System (5GS)"*.
3. **OpenAirInterface (OAI)**, *CN5G Project*.

---
*Developed for 5G Stadium Research Project | May 2026*
