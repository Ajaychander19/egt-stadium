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

## ⚙️ Advanced Parameter Tuning & System Behavior
The EGT controller operates based on a delicate balance of mathematical parameters. Modifying the values in `egt_controller.py` allows you to test entirely different network architectures and stress conditions. Here is a deep analysis of how changing each parameter alters the system's behavior:

### 1. Population and Traffic Volume ($M_g$, $\rho_g$)
*   **Parameters**: `M1` (eMBB count), `M2` (URLLC count), `rho_embb`, `rho_urllc`
*   **System Impact**: These dictate the total offered load. The delay model is exponential: `Delay ∝ exp(load)`. 
*   **Consequence of Change**:
    *   **Increasing $M_2$ (URLLC)**: Since URLLC is highly latency-sensitive and primarily targets the MEC, significantly increasing $M_2$ will rapidly saturate the Edge infrastructure. If total URLLC load forces the MEC processing delay beyond 10ms, the system enters an "Infra-Limited" state where QoS violations are mathematically unavoidable on current hardware.
    *   **Increasing $M_1$ (eMBB)**: Increases background congestion. Because eMBB has a relaxed 300ms PDB, the EGT controller will gracefully "spill" this excess traffic to the Cloud (`UPF-CC`). However, extreme eMBB scaling could eventually saturate the Cloud as well.

### 2. Capacity Constraints ($k_{mec}$, $k_{cc}$)
*   **Parameters**: `k_mec`, `k_cc`
*   **System Impact**: In our model, $k$ represents the *inverse* of processing capacity. It acts as the multiplier in the exponent of the delay function. A higher $k$ means the UPF's delay degrades much faster under load.
*   **Consequence of Change**:
    *   Currently, `k_mec` is $10\times$ larger than `k_cc` ($4.833 \times 10^{-4}$ vs $4.833 \times 10^{-5}$), enforcing the 1:10 Edge-to-Cloud capacity ratio.
    *   **Simulating Edge Upgrades**: If you halve `k_mec` (e.g., to $2.41 \times 10^{-4}$), you simulate doubling the CPU capacity of the MEC node. The EGT controller will automatically anchor more traffic at the MEC before the delay forces a spillover to the Cloud.

### 3. Propagation Delays ($t_{prop\_mec}$, $t_{prop\_cc}$)
*   **Parameters**: `t_prop_mec` (0.25 ms), `t_prop_cc` (1.0 ms)
*   **System Impact**: This is the fixed baseline latency (fiber distance) added to the dynamic processing delay. It heavily biases the initial EGT payoff.
*   **Consequence of Change**:
    *   If you move the Cloud further away (e.g., $t_{prop\_cc} = 15.0$ ms), the Cloud becomes completely non-viable for URLLC traffic (which requires <10ms end-to-end). The EGT controller will refuse to steer URLLC traffic to the Cloud, forcing it to remain on an overloaded MEC and accepting the resulting QoS violations.

### 4. Replicator Dynamics Speed ($\beta$)
*   **Parameters**: `beta` (default: 1.0)
*   **System Impact**: Controls the "step size" of the population shift during each iteration.
*   **Consequence of Change**:
    *   **$\beta > 1$**: Makes the steering logic highly aggressive. UEs will quickly jump to the better-performing UPF. However, if $\beta$ is set too high (e.g., 5.0), the system will suffer from **oscillations**—traffic will bounce back and forth between MEC and CC without ever settling on a stable Nash Equilibrium.
    *   **$\beta < 1$**: Makes the system sluggish. It will smoothly approach the equilibrium without overshooting, but it may take hundreds of iterations to get there, potentially failing to react fast enough to a sudden halftime traffic spike.

### 5. Quality of Service Thresholds ($PDB_{embb}$, $PDB_{urllc}$)
*   **Parameters**: `PDB_embb` (300 ms), `PDB_urllc` (10 ms)
*   **System Impact**: In the current implementation, these thresholds are used purely for **monitoring and compliance reporting**, not for the steering logic itself (the EGT optimizes absolute delay, not threshold margins).
*   **Consequence of Change**: Changing these will alter the reported "Violations" in the multi-scenario simulation output, but the actual fraction of traffic steered to the MEC vs CC will remain exactly the same. Making the steering logic explicitly PDB-aware (e.g., heavily penalizing a UPF only when it approaches the PDB) is a subject for future research.

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
