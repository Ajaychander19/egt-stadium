# Pass 9 Peer Review — Empirical Validation & Corrections

**Paper:** Dual-UPF Traffic Steering for 5G Network Slices in Stadium and Mass Event Deployments
**Date:** May 19, 2026
**Target:** Final Verification (Pass 9)

Dear Reviewer,

Thank you for your rigorous review. We have performed an exhaustive empirical validation (Pass 9) of every quantitative claim presented in the manuscript. To do this, we re-ran the full simulation suite (`multi_scenario_sim.py` and `egt_controller.py`) and traced the step-by-step replicator dynamics to cross-examine our claims.

Our findings validated the majority of the data, but identified two specific calculation errors in the manuscript that must be corrected to maintain absolute scientific integrity. 

Below are the detailed findings and the precise corrections to be applied to the LaTeX source.

---

### Q1: Baseline Replication
*   **Claim:** The model reproduces the Alevizaki reference equilibrium ($17.82\%$ and $31.97\%$) in exactly 231 iterations using the calibrated parameters $k_{mec} = 4.833 \times 10^{-4}$ and $k_{cc} = 4.833 \times 10^{-5}$.
*   **Empirical Result:** **VALIDATED.** The `EGTController` execution exactly reproduces $x_{mec}^{eMBB} = 17.82\%$ and $x_{mec}^{URLLC} = 31.97\%$ in precisely 231 iterations. No modification needed.

### Q2: Infrastructure Ceiling & S1 Violations
*   **Claim:** S1 produces zero eMBB violations and 26,316 URLLC violations. The MEC URLLC load ceiling is 4.7 Gbps (the exact threshold for a 9.75 ms MEC processing delay).
*   **Empirical Result:** **VALIDATED.** The S1 simulation output yields exactly 0 eMBB violations and 26,316 URLLC violations. The 4.7 Gbps ceiling calculation ($\ln(9.75) / k_{mec} = 4,711$ Mbps) holds true. No modification needed. *(Minor note: The S1 eMBB delay is 27.8 ms empirically, off by 0.1 ms from the 27.9 ms in text due to rounding; we will apply this minor precision fix).*

### Q3: S4 CC-Biased Initialisation
*   **Claim:** S4 produces 44,027 total violations and an 18.5 ms Phase II onset delay for CC.
*   **Empirical Result:** **CORRECTION REQUIRED.** The total violations (44,027) is exact. However, the calculation for the CC delay at Phase II onset under the 95% CC-bias is slightly off.
    *   CC Load is indeed 58,855 Mbps.
    *   $t_{cc} = \exp(4.833\times 10^{-5} \times 58,855) = \exp(2.844) \approx 17.2$ ms.
    *   Total delay $d_{cc} = 17.2 + 1.0 = 18.2$ ms (not 18.5 ms).
*   **Modification:** Update the delay math in the S4 section.

### Q4: S2 Cold Start to Boundary Collapse
*   **Claim:** When EGT is initialized from a neutral state ($x=0.5$) at $10\times$ load with $\varepsilon=0.01$, it "converges in 213 iterations to the all-MEC boundary equilibrium ($x_{mec}=1.0$)".
*   **Empirical Result:** **CORRECTION REQUIRED.** This claim is empirically false. Our script tracing shows the replicator does *not* hit the boundary. Instead, it halts prematurely at an intermediate state ($x_{mec}^{eMBB} \approx 0.380$) in 347 iterations.
    *   **The true phenomenon:** At extreme load ($10\times$), the MEC delay is catastrophic ($2.46 \times 10^6$ ms). Consequently, the inverse-delay payoff drops to near zero ($4.06 \times 10^{-7}$). 
    *   Because the payoffs are incredibly small, the difference between them becomes smaller than $\varepsilon = 0.01$. The discrete stopping criterion is trivially met, and the algorithm stops updating.
    *   This is a "gradient vanishing" phenomenon due to extreme overload, not a topological "boundary collapse".
*   **Modification:** Rewrite the paragraph discussing S2 cold start to correctly characterize the vanishing gradient phenomenon.

---

## Required LaTeX Modifications

We will apply the following targeted replacements to `paper/UpfSelectionAjay.tex`.

### Modification 1: S1 Peak Delay Precision Fix
*   **Target:** "eMBB end-to-end delays are 27.9~ms (MEC)" and "URLLC delays are 19.5~ms"
*   **Replacement:** Fix to empirical `27.8~ms` and `19.4~ms`.

### Modification 2: S4 CC Delay Calculation Fix
*   **Target:** 
    ```latex
    producing $t_\text{CC} = \exp(k_\text{cc} \times 58{,}855)
    = \exp(2.845) \approx 17.5$~ms processing delay plus
    $t_{\text{prop}_\text{cc}} = 1.0$~ms, totalling \textbf{18.5}~ms
    ```
*   **Replacement:**
    ```latex
    producing $t_\text{CC} = \exp(k_\text{cc} \times 58{,}855)
    = \exp(2.844) \approx 17.2$~ms processing delay plus
    $t_{\text{prop}_\text{cc}} = 1.0$~ms, totalling \textbf{18.2}~ms
    ```

### Modification 3: S2 Cold Start Vanishing Gradient Correction
*   **Target:** 
    ```latex
    When EGT is initialised from a neutral state ($x = 0.5$) and
    converged in a single cold-start call at $10\times$ load with
    $\varepsilon = 0.01$, the optimiser converges in 213 iterations
    to the all-MEC boundary equilibrium ($x_\text{mec} = 1.0$),
    where the payoff equality condition is trivially satisfied at
    zero CC occupancy. An intermediate snapshot at approximately
    iteration 150 shows $x_\text{mec}^\text{eMBB} \approx 0.380$,
    producing catastrophic MEC processing delay
    ($d_\text{eMBB}^\text{MEC} \approx 2.4\times10^6$~ms), but the
    algorithm proceeds to the boundary rather than halting there.
    While physical UPFs would drop packets rather than queue them
    indefinitely, this boundary-convergence behaviour is a structural
    consequence of the Jacobian sign structure of the discrete-time
    replicator under the pairwise comparison protocol (see footnote
    to Eq.~\eqref{eq:replicator}): the interior Nash equilibrium is
    not a stable attractor under cold-start conditions, and the
    all-MEC boundary is the only reachable stable fixed point from
    $x = 0.5$ at this load level.
    ```
*   **Replacement:** 
    ```latex
    When EGT is initialised from a neutral state ($x = 0.5$) and
    converged in a single cold-start call at $10\times$ load with
    $\varepsilon = 0.01$, the optimiser halts prematurely in 347
    iterations at an intermediate state ($x_\text{mec}^\text{eMBB}
    \approx 0.380$). At this fraction, the MEC processing delay is
    catastrophic ($d_\text{eMBB}^\text{MEC} \approx 2.46\times10^6$~ms).
    Because the payoff function is defined as inverse delay, this
    massive delay crushes the MEC payoff to near-zero
    ($u_\text{mec} \approx 4.06\times10^{-7}$). Consequently, the
    difference between the payoffs falls entirely within the
    convergence tolerance $\varepsilon = 0.01$. The algorithm halts
    not because it has reached a true Nash Equilibrium, but because
    the extreme overload causes the payoff gradient to vanish
    relative to the discrete stopping criterion.
    ```

### Modification 4: Footnote adjustment corresponding to Mod 3
*   **Target:** Footnote attached to Eq 7 about Jacobian boundary states.
*   **Replacement:** Since we've proven the boundary collapse was a hallucination caused by the $\varepsilon$ threshold, we must adjust the footnote to reflect that warm-start prevents vanishing gradient arrest, not boundary collapse.
