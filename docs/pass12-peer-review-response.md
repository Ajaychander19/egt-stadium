# Pass 12 Peer Review — Response to Expert Feedback

**Paper:** Dual-UPF Traffic Steering for 5G Network Slices in Stadium and Mass Event Deployments
**Date:** May 19, 2026
**Target Score:** 6.4/10 $\rightarrow$ Final Polish

Dear Reviewer,

Thank you for your incredibly rigorous Pass 12 review. Your attention to detail has fundamentally strengthened the manuscript's theoretical framing (particularly regarding the "Price of Anarchy"), resolved lingering terminology inconsistencies, and ensured our delay modelling and citations are explicitly anchored in 3GPP standards.

Below is our detailed point-by-point response and the corresponding modifications made directly to the LaTeX source.

---

## Responses to Questions

**Q12-1: 20/80 baseline eMBB weighted delay**
*Response:* We have added the requested calculation confirming that the eMBB weighted average delay under the 20/80 baseline is 27.6 ms. We added an explanatory note demonstrating that this achieves zero eMBB violations (matching EGT performance) but does so at the catastrophic cost of 100% URLLC violations.

**Q12-2: "Price of Anarchy" Terminology**
*Response:* You are absolutely correct; the Price of Anarchy compares the worst-case Nash equilibrium to the true social optimum, not to a static heuristic like the 20/80 split. We have replaced this phrasing with "coordination-efficiency gap between the decentralised Nash equilibrium and a centrally optimised static assignment" and removed the Pareto-dominance claim, correctly noting that it "achieves lower URLLC delay at the cost of dynamic adaptability." The orphan sentence fragment at the end of the section was also deleted.

**Q12-3: Emulation Prototype PFCP Inconsistency**
*Response:* The residual PFCP wording in Section III.F has been updated. The sentence now reads: "It reads per-UPF session counts from the SMF's internal N4 session context database to compute $\mathbf{x}^g(t)$, consistent with the population state definition in Section III.C." This fully aligns the manuscript with the internal state mechanism.

**Q12-4: Conclusion Convergence Sentence Rewrite**
*Response:* The grammatical fragment in the conclusion has been rewritten into two distinct, complete sentences as requested, clarifying the iteration counts for S1 and S2 relative to the convergence guarantees.

**Q12-5: S3 vs S1 Transient Explanation**
*Response:* We added the sentence explaining the 198-violation difference between S3 and S1. We verified numerically that a 670-iteration cold-start transient under $\Delta t = 0.05$ consistently accounts for these additional boundary crossings for the initial URLLC cohort.

**Q12-6: Delay Model Omissions & 3GPP TR 38.913**
*Response:* We added the requested paragraph to Section III.B acknowledging the omission of Uu (radio), GTP-U overhead, and N6 egress delays, noting that they do not affect the relative payoff ordering. We cited 3GPP TR 38.913 as requested.

**Q12-7: 5QI 83 Justification (3GPP TR 26.918)**
*Response:* We replaced the non-normative survey citation with a direct citation to 3GPP TR 26.918 §5.2. We clarified that the 10 ms PDB represents the network-layer budget within the total 20 ms motion-to-photon target.

**Q12-8: "Critical Stabilisation" Overclaim**
*Response:* To prevent overclaiming from an empirical trace, we softened the language describing the warm-start tracking from "critical stabilisation mechanism" to "empirically demonstrated stabilisation mechanism — formally characterised via Jacobian eigenspectrum analysis in Section V.C (future work)." 

**Q12-9: mMTC Exclusion Citation**
*Response:* Added `\cite{3gpp_ts22261}` to support the $\ll 1$ Mbps characteristic of mMTC devices.

**Q12-10: S2 Cold-Start Iteration Discrepancy**
*Response:* We re-ran `verify_claims.py` against the final codebase. The definitive results are: 347 iterations, $x_{mec}=0.380$, and a payoff gap of $0.020$. The manuscript has been updated with these precise values, including a note that they were verified on the current implementation.

## Formatting Fixes (Fix-1 to Fix-4)
*   **Fix-1:** Deleted the orphan sentence fragment.
*   **Fix-2:** Purged all `% P8-Q...` inline revision tags from the source code.
*   **Fix-3:** Added the `.png` extension to the `multi_scenario_1000ue` image inclusion.
*   **Fix-4:** Moved the Abbreviations section to the end of the manuscript, immediately following the References, to comply with standard IEEE conference formatting.

---
All modifications have been committed to the LaTeX source and checked for compilation integrity. Thank you for your rigorous guidance in finalizing this paper.
