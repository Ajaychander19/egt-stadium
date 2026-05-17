# Peer Review Response & Modification Log
**Project:** Multi-UPF Traffic Steering for 5G Network Slices in Stadium and Mass Event Deployments
**Date:** May 18, 2026

Dear Reviewer,

Thank you for your exceptionally thorough and insightful critique of our manuscript. Your close reading of our methodology against the Alevizaki reference paper revealed several critical documentation gaps, architectural framing issues, and typographical errors that we had missed. 

We agree with all 14 of your points. Below is a detailed, point-by-point response outlining our validations and the exact modifications we have made to the manuscript to address each issue.

---

### 1. Conclusion — Broken/Inverted Sentence
**Reviewer Point:** The sentence *"the system doesn't converges to a stable equilibrium in under 100 iterations"* contains a grammatical error and factually inverts the results (the system *does* converge, just taking longer than 100 iterations).
**Our Response:** We completely agree. This was a severe typographical error that contradicted both our own data and the core message of the paper.
**Action Taken:** The Conclusion has been rewritten:
> *"Second, the EGT controller converges to a stable equilibrium across all evaluated scenarios. While static cold-starts under extreme load shifts require up to 670 iterations, continuous warm-start tracking resolves in a single iteration per step once the population state reaches the active equilibrium trajectory."*

### 2. "Under 100 Iterations" Claim
**Reviewer Point:** The claim of convergence in "under 100 iterations" is a propagated error from the reference paper and contradicts the 147–670 iterations observed in the stadium simulation.
**Our Response:** You are entirely correct. The "under 100 iterations" figure applies only to the much smaller population ($M_1=130$, $M_2=70$) in the Alevizaki reference. Our stadium scenario with 1,000 UEs takes significantly longer for cold starts.
**Action Taken:** We have removed all instances of the "under 100 iterations" claim from the Abstract and Conclusion. We now explicitly state that convergence takes between 147 and 670 iterations depending on the initialization and load conditions.

### 3. Delay Model — Critical Difference from Reference
**Reviewer Point:** The reference paper uses a shared delay model for both UPFs, but our paper uses a dedicated MEC model (Eq 3a) and a shared CC model (Eq 3b) without disclosing this architectural departure.
**Our Response:** This is an excellent catch. The shift from a shared to a dedicated MEC delay model was a deliberate design choice to reflect 3GPP network slicing (where edge resources are isolated per S-NSSAI to protect URLLC traffic), whereas the reference modeled a generic optical node. We failed to explicitly document this modification.
**Action Taken:** We have added the following justification to Section III.E:
> *"While Alevizaki et al. use a single shared delay formula for both UPFs, we adopt a dedicated-MEC model for the edge UPF, in which only the sessions of group $g$ contribute to that group's MEC processing delay. This reflects the 3GPP TS 23.501 network slicing architecture, where per-S-NSSAI resource isolation at the edge is a core requirement for stadium deployments with strict URLLC guarantees. The central UPF remains shared across all groups, consistent with the reference model."*

### 4. EGT Framing — UE-Driven vs. SMF-Centralized
**Reviewer Point:** The reference paper frames EGT as decentralized UE-driven decisions, whereas our paper implements it as centralized SMF-driven steering. This architectural shift and its impact on signaling are not acknowledged.
**Our Response:** We agree. Allowing 1,000 UEs to independently renegotiate their UPF anchors would generate catastrophic N4/N11 control plane signaling. We purposefully "lifted" the replicator dynamics into the SMF as a centralized population-steering algorithm.
**Action Taken:** We have added a clarifying paragraph to Section III.C (Justification for EGT):
> *"Unlike standard EGT formulations where individual UEs selfishly optimize their choices, we implement the replicator dynamics centrally within the SMF to compute optimal population fractions. This centralized adaptation prevents the massive control-plane signaling overhead that would occur if thousands of UEs independently triggered session renegotiations, while still preserving the mathematically stable load-balancing properties of the Nash equilibrium."*

### 5 & 11. $k$ Calibration & Exponential Model on Software UPF
**Reviewer Point:** The $k$ exponents calibrated for a 100 Mbps optical node were directly applied to a 10/25 Mbps software UPF scenario. Furthermore, the exponential delay model is unphysical for software UPFs at extreme load ($10\times$), where packets would drop rather than queue for $10^6$ ms.
**Our Response:** We agree. We reused the $k$ parameters as generic scaling constants to preserve the 10:1 cloud-to-edge capacity ratio from the reference, allowing us to evaluate the steering logic's response to congestion. However, we agree that the physical meaning does not perfectly transfer to containerized software UPFs.
**Action Taken:** We have added a clear limitation statement in Section III.E:
> *"We note that these $k$ parameters, originally derived from optical switching hardware, are utilized here as generic capacity constraints to preserve the 10:1 cloud-to-edge ratio and test the steering logic's stability. In a physical software UPF deployment, extreme overload would result in packet drops and session rejections rather than unbounded exponential queuing delay."*

### 6. S3/S4 Scenario Names Misleading
**Reviewer Point:** S3 and S4 are called "Overload" but only differ from S1 in their initialization state (90% MEC vs 5% MEC).
**Our Response:** We agree the naming is confusing. The total offered load is identical to S1 ($5.5\times$). 
**Action Taken:** We have renamed S3 to "MEC-Biased Initialization" and S4 to "CC-Biased Initialization" throughout the text and in Table II, and added a sentence defining them clearly in the Methodology.

### 7. Baseline Violations Inconsistent (400/100)
**Reviewer Point:** The 50/50 static baseline reports 400 eMBB and 100 URLLC violations, which is mathematically impossible for cumulative UE-steps over a 135-step window given the massive MEC delay.
**Our Response:** You correctly identified a bug in our reporting script. The 400/100 figures represented an *instantaneous* count at a single timestep, whereas the other scenarios correctly reported *cumulative* counts over the 135 Phase II steps.
**Action Taken:** We have updated Table II with the correct cumulative baseline violations: 54,000 eMBB ($400 \times 135$) and 13,500 URLLC ($100 \times 135$).

### 8. QoS Compliance Percentages (76.5% / 22.1%)
**Reviewer Point:** The 76.5% and 22.1% compliance figures in the Conclusion cannot be derived from the 135,000 total UE-steps in the table.
**Our Response:** We agree. These percentages were artifacts of an older denominator calculation spanning all three event phases. For clarity, compliance should be calculated over the extreme Phase II peak window reported in the table (135,000 total UE-steps).
**Action Taken:** We have corrected the figures in the Conclusion. S1 Phase II compliance is 80.5% ($(135,000 - 26,316) / 135,000$), and S4 compliance is 67.4% ($(135,000 - 44,027) / 135,000$).

### 9. "18 Gbps Throughput" Unexplained
**Reviewer Point:** The abstract mentions an 18 Gbps hard infrastructure ceiling, but the total offered load is 71.5 Gbps. The gap is unexplained.
**Our Response:** The "18 Gbps" figure was meant to describe the *edge MEC node's* saturation boundary, not the aggregate network throughput. 
**Action Taken:** We have revised the Abstract and Section V to clarify that this refers specifically to the MEC node's processing capacity ceiling, avoiding confusion with the 71.5 Gbps total offered load.

### 10. Nsmf SBI Misused as Telemetry Interface
**Reviewer Point:** The Nsmf SBI is for NF-to-NF communication inside the core, not for external controller telemetry. 
**Our Response:** We agree. This was an architectural terminology error in our description of the prototype integration.
**Action Taken:** We have corrected Section IV.B to state:
> *"The controller retrieves session counts via the N4/PFCP interface using Session Report messages and utilizes the O1 interface for management-plane telemetry."*

### 12. Review Rate Subscript Discrepancy
**Reviewer Point:** Eq. 5 uses $u_i^g$ while the reference Alevizaki Eq. 2 uses $u_j^g$.
**Our Response:** We agree this was a typographical error in our LaTeX transcription; the code implementation evaluates payoffs correctly.
**Action Taken:** We have updated Eq. 5 in the manuscript to accurately reflect $u_j^g(\mathbf{x}, \lambda)$.

### 13. Phase II Timestep Mapping Never Defined
**Reviewer Point:** The table refers to a 135-step Phase II window, but the text says Phase II is 45 minutes without defining the step size.
**Our Response:** We omitted the temporal mapping of the simulation steps. 
**Action Taken:** We have added the following clarifying sentence to Section III.G:
> *"Phase II spans 45 minutes, evaluated at 3 simulation steps per minute, yielding the 135-step evaluation window reported in the results."*

### 14. MEC Isolation Assumption
**Reviewer Point:** Assuming MEC isolation requires specific 3GPP QoS configuration, which is not cited.
**Our Response:** We agree. Dedicated edge processing relies on explicit network slicing and QoS flow enforcement.
**Action Taken:** We have added a citation to 3GPP TS 23.501 Section 5.7 (QoS framework) in Section III.E to formally justify the dedicated MEC delay model assumption.

---
*All the above changes have been integrated into the final manuscript.*
