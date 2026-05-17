# Peer Review Response & Modification Log (Pass 2)
**Project:** Dual-UPF Traffic Steering for 5G Network Slices in Stadium and Mass Event Deployments
**Date:** May 18, 2026

Dear Reviewer,

Thank you for your exceptionally rigorous second-pass review. Your scrutiny of the convergence thresholds, the violation denominators, and the physical capacity constraints has fundamentally elevated the scientific honesty and rigor of this paper. We agree with your critique entirely.

Below is our detailed response to the 23 points raised, outlining the exact textual and mathematical corrections made to the manuscript.

---

### 🔴 CRITICAL ISSUES

**C1 — Abstract is a Placeholder**
*   **Response:** We agree. The placeholder was an artifact of the draft compilation process. We have restored the full abstract, which properly introduces the dual-UPF framework, the SMF-centralised EGT methodology, the 100% eMBB compliance finding, and the 10 ms URLLC infrastructure ceiling.

**C2 — Eq. 5 (Replicator) Subscript Fix**
*   **Response:** You are completely correct; changing $u_i^g$ to $u_j^g$ broke the equation by failing to define $j$. We have rewritten the text following Eq. 5 to explicitly state: *"where $u_j^g(\mathbf{x},\lambda)$ denotes the payoff of an alternative UPF strategy $j \in \mathcal{S}_g$ chosen at random by the reviewing agent."*

**C3 — S4 URLLC Violation Count and S4 vs S1 NE Contradiction**
*   **Response:** This was a brilliant observation. The discrepancy in the equilibrium fractions (0.156 vs 0.128) despite identical load is due to the discrete stopping condition $\varepsilon = 0.01$. S1 approaches this tolerance boundary from $x=0.5$, while S4 approaches it from $x=0.05$, causing them to halt on opposite edges of the $\varepsilon$-ball. 
    Furthermore, S4 accumulates massively more violations (44,027 vs 26,316) despite converging faster because it starts with 95% of traffic on the Central Cloud. At 95% load, initial CC processing delay spikes to >27 ms, meaning *every single URLLC session* violates the 10 ms PDB instantly during the transient migration phase. 
*   **Action Taken:** We have rewritten Section V.D ("Transient recovery and numerical $\varepsilon$-boundaries") to explicitly document this boundary-stopping behavior and the transient violation penalty of the cloud-first initialization.

**C4 — Compliance Metric Denominator**
*   **Response:** We agree entirely. Using 135,000 total UE-steps as the denominator mathematically masked the URLLC failures by padding the compliance rate with eMBB successes.
*   **Action Taken:** We have recalculated URLLC compliance using the correct 27,000 URLLC UE-steps. The 26,316 violations represent a **97.5% violation rate** for URLLC under $5.5\times$ load. We have updated the Conclusion to state this explicitly, which massively strengthens our "infrastructure ceiling" finding.

**C5 — 18 Gbps MEC Ceiling Figure Underived**
*   **Response:** You are correct. The 18 Gbps figure was an artifact of an earlier parameter iteration and was mathematically disjoint from the current model.
*   **Action Taken:** We have added the explicit derivation to Section V.D: $k_\text{mec} \cdot (\text{Load}) > \ln(10 - 0.25) \implies \text{Load} \approx 4.7$ Gbps. Because total URLLC load is 27.5 Gbps, this hard 4.7 Gbps edge capacity ceiling mathematically prevents compliance. The text has been updated to reflect this derived value.

---

### 🟠 MAJOR ISSUES

**M1 — Slice-Agnostic Payoff**
*   **Response:** We agree. The $u = 1/\text{delay}$ payoff function minimizes delay but is blind to discrete PDB thresholds, preventing the algorithm from aggressively prioritizing URLLC traffic when capacity runs out.
*   **Action Taken:** We explicitly acknowledge this limitation in Section III.E and the Conclusion, suggesting a PDB-margin payoff (e.g., $u = \text{PDB}_g / d_i^g$) as a critical avenue for future work.

**M2 — mMTC Absent from Model**
*   **Response:** We agree. We modeled only two slices but incorrectly included mMTC in the preamble.
*   **Action Taken:** We removed mMTC from the Keywords, Introduction, and Related Work. We added a note in Section III.A stating that mMTC is excluded from the evaluation due to its low throughput exerting negligible selection pressure.

**M3 — "Multi-MEC" Claim**
*   **Response:** Agreed. The architecture has one MEC node.
*   **Action Taken:** Changed to "dual-UPF, single-MEC architecture" in Related Work.

**M4 — SSB Periodicity Argument**
*   **Response:** We agree. Conflating RAN SSB with Core N4 signaling was flawed.
*   **Action Taken:** The paragraph has been removed.

**M5 — Eq. 6 (UPF Bound) Unused**
*   **Response:** Agreed.
*   **Action Taken:** Eq. 6 has been deleted.

**M6 — Phase II Timestep Orphan**
*   **Response:** Agreed.
*   **Action Taken:** Moved the sentence into the Phase II bullet point in Section III.B.

**M7 — EGT Centralization Orphan**
*   **Response:** Agreed.
*   **Action Taken:** This has been formatted as a bolded property ("**Centralised SMF Steering**") at the start of Section III.C.

**M8 — CC Load > 10 Gbps Link Bandwidth**
*   **Response:** This was a typo in Table I. Core backhaul links are provisioned at much higher capacities.
*   **Action Taken:** Changed $B_{u,v}$ to 100 Gbps in Table I.

**M9 — Convergence Claim in Conclusion**
*   **Response:** We agree the claim was overly broad.
*   **Action Taken:** Qualified the text in the Conclusion: *"resolves in 1 iteration under standard load transitions, and up to 147 iterations per step during extreme $10\times$ load surges."*

---

### 🟡 MODERATE & 🔵 MINOR ISSUES

**m1 (Abbreviations):** Added all 18 missing terms (CUPS, SBA, BLSTM, PFCP, PDU, NR, NF, ILP, OPEX, GTP, NSSF, AMF, NRF, UDM, AUSF, UDR) to the table.
**m2 (Redundant Citations):** Merged the duplicate TS 23.501 citations in Section III.E.
**m3 (Emulation Label):** Added `\label{sec:implementation}` to Section IV.
**m4 (5QI for AR/VR):** Changed 5QI 82 (V2X) to **5QI 83**, which appropriately specifies a 10 ms PDB.
**m5 (450% Mapping):** Clarified the math in the text: *"where a 450% increase above the pre-match baseline corresponds to a load multiplier of $\lambda = 1 + 4.5 = 5.5$."*
**m6 (Physical Scaling):** Compressed the attachment narrative into a single sentence in the Section V preamble.
**m7 (Theoretical Contribution):** Hedged the phrasing to *"a practically important empirical observation of this work."*
**p1 & p2 (Table I Units):** Changed link bandwidth to $B_{u,v}$ and capacities from "CPU" to "cores (2.4 GHz)".
**p3 (Hyphenation):** Standardized on "warm-start".
**p4 (Title):** Changed paper title to **"Dual-UPF Traffic Steering..."** to accurately reflect the two-UPF topology.
**p6 (Reconfiguration Events):** Removed the contradictory mention of reconfiguration events in Section III.C, clarifying that established sessions are not re-anchored.

---
*All the above changes have been integrated into the revised manuscript.*
