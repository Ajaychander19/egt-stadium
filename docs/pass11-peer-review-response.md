# Pass 11 Peer Review — Response to Expert Feedback

**Paper:** Dual-UPF Traffic Steering for 5G Network Slices in Stadium and Mass Event Deployments
**Date:** May 19, 2026
**Target Score:** 6.4/10 $\rightarrow$ 9.5/10

Dear Reviewer,

Thank you for your thorough and incisive expert review. Your questions—particularly regarding the methodological scope, the baseline comparisons, and the PFCP mechanism—highlighted critical areas where the manuscript required clarification and factual correction. We have systematically addressed all five of your "make-or-break" questions (Q1–Q5) as well as the notable Q9.

Below is our detailed response and the corresponding modifications made to the manuscript.

---

## Q1: OAI Testbed vs. Analytical Model Clarity
**Reviewer Comment:** Clarify precisely what the OAI testbed actually measured versus what the analytical model computed. The abstract implies empirical QoS results that are actually model outputs.
**Response:** We entirely agree. Presenting analytical data-plane results as physical OAI measurements is a severe methodological misrepresentation. We have explicitly scoped the abstract and Section IV to separate these domains. The OAI testbed was used purely to validate *control-plane scalability* (the AMF/SMF's ability to handle 1,000 active PDU session assignments without crashing). The *data-plane QoS performance* (packet delays and PDB violations) was evaluated offline using a rigorous mathematical queuing model.
**Action taken:** Abstract and Sections IV/V were rewritten to clearly demarcate the physical control-plane emulation from the analytical data-plane simulation.

## Q2: Sensitivity Analysis of $k$-parameters
**Reviewer Comment:** The model is calibrated at ~20 Gbps but applied at 71–130 Gbps; without sensitivity analysis, every delay figure is an extrapolation.
**Response:** This is a sharp observation. The $k$-parameters, derived from Alevizaki's optical switching hardware at 20 Gbps, are indeed an extrapolation when applied to 130 Gbps virtualized 5G UPFs. We have added a dedicated paragraph in Section V.A to clarify this. At 130 Gbps, these parameters serve primarily as *algorithmic constraints* to enforce a 10:1 cloud-to-edge capacity asymmetry to test the EGT controller's mathematical stability under stress, rather than predicting exact physical millisecond delays on specific COTS hardware.
**Action taken:** Added an explicit mathematical justification in Section V.A acknowledging the extrapolation and scoping the $k$-parameters as structural bounds for the steering logic.

## Q3: Factual Correction: NSSF Abbreviation
**Reviewer Comment:** NSSF is labelled "OpenAirInterface" in the abbreviations table, which is wrong.
**Response:** Thank you for catching this embarrassing typographical error.
**Action taken:** Corrected "NSSF - OpenAirInterface" to "NSSF - Network Slice Selection Function" in the Abbreviations table.

## Q4: The O1 Interface Claim
**Reviewer Comment:** Justify or remove the O1 interface claim. O1 is O-RAN, not 3GPP CN5G.
**Response:** You are absolutely correct. The O1 interface connects O-RAN elements (O-RU, O-DU, O-CU) to the Service Management and Orchestration (SMO) framework. It has no place in a 3GPP 5G Core SMF telemetry discussion. The SMF relies on its internal UE context state.
**Action taken:** The sentence referencing the O1 interface in Section IV.B was completely removed and replaced with a reference to the SMF's internal session context store.

## Q5: Non-Trivial Steering Baseline
**Reviewer Comment:** Comparing EGT only against static 50/50 is not sufficient for a research contribution claim.
**Response:** We agree that a static 50/50 split is a "strawman" baseline. We have elevated the "Static 20/80" split—which intelligently respects the 10:1 cloud-to-edge capacity asymmetry—into a formal baseline. We have added it to Table 2 and expanded the discussion in Section V.C to demonstrate that even a capacity-aware static split fails under extreme non-stationary stadium load, validating the need for dynamic EGT.
**Action taken:** Added the Static 20/80 baseline to Table 2 and expanded the comparative analysis in Section V.C.

## Q9: PFCP Session Report Mechanism
**Reviewer Comment:** UPF session counts are maintained by the SMF's own context store, not reported back via PFCP Session Reports.
**Response:** Excellent technical catch. While PFCP Session Reports are used for Usage Reporting Rules (URR) like byte counts, the SMF natively knows how many sessions it has anchored at each UPF because it manages the N4 context establishment directly. Polling the UPF for this would be unnecessary control-plane overhead.
**Action taken:** Corrected lines throughout the methodology and implementation sections to state that the SMF computes population fractions ($x^g$) directly from its internal N4 session context database, rather than via PFCP polling.

---
All changes have been committed to the LaTeX source. Thank you for elevating the technical rigor of this manuscript.
