# High-Scale EGT Stadium Emulation: Architectural Limitations & Gaps

While the scaled 1,000-UE Evolutionary Game Theory (EGT) stadium emulation successfully demonstrates capacity-aware user-plane steering and reproduces theoretical Nash Equilibria, it operates under several simplifications. When transitioning from this containerized Software-in-the-Loop (SITL) environment to a commercial, production-grade 5G network, operators must consider the following engineering constraints and architectural limitations:

---

## 1. RAN Layer Bypass (Radio Propagation Realism)
*   **Emulation Reality:** In our dockerized environment, the Radio Access Network (RAN) physical and MAC layers are completely bypassed. User-plane packets flow directly over virtual Linux bridge interfaces (`stadium_net`) and virtual network interfaces (`gtp-gnb`). Latency in the transport layer is dominated by CPU packet processing queues and is virtually zero.
*   **Real-World Gap:** In actual 5G deployments, user packets traverse the Uu radio interface, experiencing path loss, multi-path fading, shadowing, Doppler shifts, and scheduling delays (e.g., Slot Allocation, HARQ retransmissions). These physical radio impairments introduce stochastic, bursty latency variations that are not present in our clean, software-in-the-loop transport channel.

---

## 2. Control-Plane Transaction Bottlenecks (Attach Storms)
*   **Emulation Reality:** The UEs in our simulation establish sessions progressively. During the EGT recalculation loops, the control plane behaves predictably with no connection failures.
*   **Real-World Gap:** In real stadium environments, events such as halftime or a kickoff trigger simultaneous device wake-ups. This leads to an **"Authentication Attach Storm"**, where hundreds of UEs attempt to attach to the AMF at the exact same millisecond. This creates high CPU utilization and database lock contention in the Unified Data Management (UDM) and Unified Data Repository (UDR) modules, causing session establishment failures that EGT does not model.

---

## 3. Radio Resource Control (RRC) State Transitions
*   **Emulation Reality:** Once registered, all 1,000 emulated UEs are assumed to be in a permanent, high-power active state with active PDU sessions.
*   **Real-World Gap:** Real-world 5G UEs actively transition between three states to conserve battery: **RRC-CONNECTED**, **RRC-INACTIVE**, and **RRC-IDLE**.
    *   Whenever a device wakes up from IDLE/INACTIVE state to transmit user-plane data, it must execute a multi-step **Service Request** signaling procedure with the AMF to reconstruct the radio bearers.
    *   For 1,000 active devices, this continuous cycle of wake-ups and sleep states generates a massive signaling overhead on the control plane, which significantly impacts SMF response time and EGT re-steering latency.

---

## 4. Device Mobility & Handover Overhead (Xn/N2 Signalling)
*   **Emulation Reality:** The simulation assumes that all UEs are statically positioned and anchored to a single gNodeB (gNB) instance.
*   **Real-World Gap:** stadium users are constantly moving, causing frequent **handovers** between neighboring gNB small cells.
    *   Handovers require continuous Xn (gNB-to-gNB) or N2 (gNB-to-AMF) signaling to transfer the UE's context.
    *   During these transitions, the SMF must continuously modify and update the GTP-U downlink and uplink tunnel paths (using standard Packet Forwarding Control Protocol - PFCP - signaling).
    *   The packet buffering, forwarding, and synchronization overhead during handovers introduce transient packet delays and packet loss that our static emulation ignores.

---

## 5. TCP Congestion Collapse (TCP Incast)
*   **Emulation Reality:** The delay calculations in our EGT payoff functions assume ideal, isolated mathematical queueing delay curves that scale smoothly with the traffic volume.
*   **Real-World Gap:** In a real network, when the local MEC UPF becomes heavily congested, packet drop rates increase.
    *   This triggers simultaneous packet retransmission timeouts across thousands of concurrent TCP streams.
    *   This leads to a phenomenon known as **TCP Incast**, where retransmitted packets flood the network buffer queues, causing a complete collapse in throughput and a severe spike in latency (bufferbloat).
    *   The smooth, predictable delay curves of EGT are broken during such network events.

---

## 6. Physical vs. Simulated Offered Traffic
*   **Emulation Reality:** To prevent host CPU exhaustion, the virtual gNB pushes lightweight synthetic control packets rather than pushing a physical line-rate of $130$ Gbps. The offered load ($71.5$ Gbps and $130$ Gbps) is modeled mathematically inside the EGT payoff calculations to guide steering choices.
*   **Real-World Gap:** Handling a true physical throughput of $130$ Gbps requires specialized enterprise-grade telecommunications hardware. Operators must utilize dedicated smartNICs, Single Root I/O Virtualization (SR-IOV), or Data Plane Development Kit (DPDK) software libraries to process packet encapsulation at line-rate. Standard Linux bridges and CPU-bound packet routing would fail under real load.
