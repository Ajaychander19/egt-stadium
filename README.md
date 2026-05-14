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

## 💻 Usage

### 1. Start the OAI 5G Core
Ensure the independent UPF configs and database provisioning are ready:
```bash
docker compose up -d
```

### 2. Run the 1000-UE Scaling
Use the provided provisioning and scaling configurations:
```bash
# Provision 1,000 UE identities in MySQL
docker exec -i mysql mysql -uroot -plinux < provision_1000.sql

# Restart gnbsim with the 1000-UE config
docker compose restart gnbsim
```

### 3. Execute the EGT Controller
Run the 3-phase stadium simulation (Ramp-up, Halftime Peak, Dispersal):
```bash
python3 multi_scenario_sim.py
```

---

## 📈 Results (1000-UE Stadium Scenario)

The simulation demonstrates successful traffic management under heavy load. During the halftime peak (~18 Gbps total demand), the EGT controller stabilizes the network by offloading eMBB traffic to the Cloud UPF to protect the MEC for latency-sensitive URLLC sessions.

- **eMBB QoS**: 100% compliance (0 violations) in standard stadium scenarios.
- **URLLC Performance**: Successfully maintains 10ms PDB during normal load; correctly identifies "Infra-Limited" saturation during the 5.5x spike.
- **Convergence**: The algorithm converges to Nash Equilibrium in <100 iterations.

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
