# Pass 7 Peer Review — Response and Validation
**Paper:** Dual-UPF Traffic Steering for 5G Network Slices in Stadium and Mass Event Deployments
**Date:** May 19, 2026
**Current Score:** 8.5/10 -> targeting 9.5/10

Dear Reviewer,

Thank you for the rigorous Pass 7 review. Your attention to detail has identified three critical structural and numerical ambiguities that impact the integrity of our findings. We have validated your concerns using our simulation scripts and have addressed each of them directly in the manuscript. 

Here are the detailed answers, validations, and the corresponding modifications made to the LaTeX code.

---

## 🔴 R7-Q1 — S1 Transient Iters = 505 is internally inconsistent
**Reviewer Claim:** The paper reports S1 Transient Iters = 505 in Table 2, but the text says S1 Phase II steps converge in exactly 1 iteration (mean 3.3). If S1 operates in warm-start mode, what does 505 measure?

**Validation and Justification:**
We ran our analysis script over the `results/multi_scenario_results.json` simulation data to verify the iteration counts. 
For S1 (Standard $5.5\times$ load), the sum of all iterations during the entire 135-step Phase II warm-start timeline is exactly **442 iterations**.
The 505 figure reported in Table II is NOT the sum of Phase II iterations. Instead, 505 is the **static cold-start convergence count**—the number of iterations required to converge from a neutral 50/50 state to the Nash equilibrium under an instant $5.5\times$ load spike. We originally included this to provide a theoretical benchmark of the algorithm's raw convergence speed. However, you are absolutely correct that presenting this alongside the warm-start narrative without explicit clarification creates a direct contradiction for the reader.

**Action taken in paper:**
1. We have updated the caption of Table II to explicitly distinguish the cold-start benchmark from the warm-start timeline:
   *Original:* "Transient Iters for S1, S3, S4: static cold-start count."
   *Revised:* "Transient Iters for S1, S3, S4: theoretical static cold-start convergence count (from a neutral 50/50 state), providing a baseline benchmark distinct from the dynamic warm-start 1-iteration tracking reported in the text."
2. We added a clarifying sentence in Section V.C (Key Analysis and Findings) under the warm-start tracking paragraph to explicitly state that the 505 iterations represent a cold-start benchmark.

---

## 🔴 R7-Q2 — The S2 eMBB violation rate of 12.5% is mathematically underspecified
**Reviewer Claim:** The abstract/conclusion states violations are "confined to 12.5% of Phase II steps", but 13,491 violations over 108,000 UE-steps = 12.49% of UE-steps. Is 12.5% the fraction of timesteps or UE-steps? 

**Validation and Justification:**
You have correctly identified a factual error in our phrasing. We validated the data for Scenario S2 Phase II:
- Total eMBB violations: 13,491
- Total Phase II eMBB UE-steps: 108,000 ($800 \text{ UEs} \times 135 \text{ steps}$)
- Fraction of UE-steps: $13,491 / 108,000 = 12.49\%$
- Timesteps experiencing $>0$ violations: 114 out of 135 steps ($84.44\%$)

Because violations occur across 84% of the timesteps during the migration phase, describing them as "confined to 12.5% of Phase II steps" is false. The 12.5% figure correctly represents the **volume of eMBB traffic (UE-steps)** affected during the migration phase, not the duration. 

**Action taken in paper:**
We have corrected the mathematical specification in both the Abstract and the Conclusion.
*Abstract Revision:* "In the extreme $10\times$ stress scenario (S2), transient eMBB violations occur during the warm-start migration phase, corresponding to a 12.5\% violation rate across Phase II eMBB UE-steps; these cease once EGT converges."
*Conclusion Revision:* "...in the extreme $10\times$ stress scenario S2, eMBB violations affect 12.5\% of Phase II UE-steps during active migration and cease at convergence."

---

## 🟡 R7-Q3 — The Abbreviations table placement
**Reviewer Claim:** The Abbreviations table appears after the Bibliography in the current LaTeX but before the Introduction in the Pass 6 output. Which placement is intentional?

**Validation and Justification:**
The placement after the Bibliography in the current LaTeX file was an accidental reversion. In standard IEEEtran formatting, a Nomenclature or Abbreviations table should ideally be placed immediately following the Keywords and before the Introduction, as this defines the terminology prior to the reader engaging with the text.

**Action taken in paper:**
We have moved the `\section*{Abbreviations}` block to its correct location immediately following the `\end{IEEEkeywords}` block and before `\section{Introduction}`.

---
### Conclusion
These modifications resolve the internal contradictions regarding the iteration counts and clarify the exact nature of the 12.5% violation metric. We believe the paper is now mathematically robust and structurally sound.
