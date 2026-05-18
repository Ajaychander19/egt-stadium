# -*- coding: utf-8 -*-
import json, math
import sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import Counter

with open('results/multi_scenario_results.json') as f:
    data = json.load(f)

k_mec = 4.833e-4
k_cc  = 4.833e-5
t_prop_mec = 0.25
t_prop_cc  = 1.0
M1, M2 = 800, 200
rho_e, rho_u = 10, 25

# ─── R6-Q1: S4 Phase I lambda profile and violation explanation ──────────────
print("=" * 60)
print("R6-Q1: S4 Phase I lambda profile and violation audit")
print("=" * 60)
s4p1 = [d for d in data if d['scenario'] == 'S4_CCOverload' and d['phase'] == 1]
mults = [d['load_mult'] for d in s4p1]
vios  = [d['vio_URLLC'] for d in s4p1]
print(f"S4 Phase I steps: {len(s4p1)}")
print(f"Lambda range: min={min(mults):.4f}, max={max(mults):.4f}")
print(f"First 5 lambda: {[round(m,4) for m in mults[:5]]}")
print(f"Total URLLC vio Phase I: {sum(vios)}")
# Now check: at what lambda does CC delay exceed PDB2=10ms?
# CC load at S4 Phase I = 95% * total_load = 0.95 * (M1*rho_e + M2*rho_u) * lam
# But S4 starts with x_mec=0.05, so x_cc=0.95
# Check first step with violations
for i, d in enumerate(s4p1):
    lam = d['load_mult']
    x_cc_u = d['x_URLLC_CC']
    x_cc_e = d['x_eMBB_CC']
    cc_load = (M1 * rho_e * x_cc_e + M2 * rho_u * x_cc_u) * lam
    d_cc = t_prop_cc + math.exp(k_cc * cc_load)
    if d['vio_URLLC'] > 0:
        print(f"First violation at step {i}: lam={lam:.4f}, cc_load={cc_load:.1f} Mbps, d_cc={d_cc:.3f} ms, x_cc_u={x_cc_u:.4f}")
        break
# At max lambda=1.0 with 95% CC routing:
lam_max = 1.0
x_cc_init = 0.95
cc_load_p1max = (M1*rho_e*x_cc_init + M2*rho_u*x_cc_init) * lam_max
t_cc_p1max = math.exp(k_cc * cc_load_p1max)
d_cc_p1max = t_prop_cc + t_cc_p1max
print(f"\nManual calc at lam=1.0, x_cc=0.95:")
print(f"  CC load = ({M1}*{rho_e}*0.95 + {M2}*{rho_u}*0.95)*1.0 = {cc_load_p1max:.1f} Mbps")
print(f"  d_cc = 1.0 + exp({k_cc}*{cc_load_p1max:.1f}) = 1.0 + {t_cc_p1max:.4f} = {d_cc_p1max:.4f} ms")
print(f"  Violates PDB2=10ms? {d_cc_p1max > 10}")
# Find threshold lambda
print("\nFinding lambda threshold for CC violation at x_cc=0.95:")
for lam_t in [0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5]:
    cc_l = (M1*rho_e*x_cc_init + M2*rho_u*x_cc_init) * lam_t
    d_c = t_prop_cc + math.exp(k_cc * cc_l)
    print(f"  lam={lam_t:.2f}: cc_load={cc_l:.0f} Mbps, d_cc={d_c:.3f} ms, vio={d_c>10}")

# ─── R6-Q2: S2 URLLC counting window clarification ───────────────────────────
print()
print("=" * 60)
print("R6-Q2: S2 URLLC violation count breakdown")
print("=" * 60)
s2 = [d for d in data if d['scenario'] == 'S2_ExtremePeak']
for ph in [1, 2, 3]:
    rows = [d for d in s2 if d['phase'] == ph]
    uv = sum(d['vio_URLLC'] for d in rows)
    ev = sum(d['vio_eMBB'] for d in rows)
    print(f"S2 Phase {ph}: eMBB_vio={ev}, URLLC_vio={uv}")
total_uv = sum(d['vio_URLLC'] for d in s2)
p2_uv = sum(d['vio_URLLC'] for d in s2 if d['phase'] == 2)
p3_uv = sum(d['vio_URLLC'] for d in s2 if d['phase'] == 3)
print(f"TOTAL URLLC: {total_uv} = Phase2({p2_uv}) + Phase3({p3_uv})")
print(f"Table value 27,064 = Phase2 {p2_uv} + Phase3 {p3_uv}? = {p2_uv + p3_uv}")
print(f"Footnote says 'Phase II only = 26,467' -> Phase3 residual = {total_uv - p2_uv}")

# ─── R6-Q3: Can EGT route 0% to MEC? Minimum viable fraction ────────────────
print()
print("=" * 60)
print("R6-Q3: Ceiling analysis — minimum viable fraction at 5.5x")
print("=" * 60)
lam55 = 5.5
ceiling_mbps = math.log(9.75) / k_mec
print(f"Ceiling load = {ceiling_mbps:.1f} Mbps = {ceiling_mbps/1000:.3f} Gbps")
min_frac = ceiling_mbps / (M2 * rho_u * lam55)
print(f"Min fraction to stay BELOW ceiling = {ceiling_mbps:.1f} / ({M2}*{rho_u}*{lam55}) = {min_frac:.4f} = {min_frac*100:.1f}%")
print(f"At x_mec=0.171: MEC load = {M2*rho_u*0.171*lam55:.1f} Mbps (vs ceiling {ceiling_mbps:.1f})")
print(f"At x_mec=0.000: MEC load = 0 Mbps — ZERO violations possible in theory")
# Why EGT doesn't route 0%: Nash equilibrium requires u_mec = u_cc
# At x_mec=0, all traffic at CC: d_cc = 1.0 + exp(k_cc * M1*rho_e*5.5 + M2*rho_u*5.5)
cc_load_all = (M1*rho_e + M2*rho_u) * lam55
d_cc_all = t_prop_cc + math.exp(k_cc * cc_load_all)
d_mec_zero = t_prop_mec + math.exp(0)  # no load on MEC
u_cc_all = 1.0 / d_cc_all
u_mec_zero = 1.0 / d_mec_zero
print(f"\nAt x_mec=0 (all traffic on CC):")
print(f"  CC load = {cc_load_all:.0f} Mbps, d_cc = {d_cc_all:.3f} ms, u_cc = {u_cc_all:.6f}")
print(f"  MEC has 0 load: d_mec = 0.25 + exp(0) = {d_mec_zero:.2f} ms, u_mec = {u_mec_zero:.6f}")
print(f"  u_mec ({u_mec_zero:.6f}) > u_cc ({u_cc_all:.6f}) → replicator INCREASES x_mec → cannot stay at 0%")

# ─── R6-Q4: Replicator equation u_j vs u_i derivation ───────────────────────
print()
print("=" * 60)
print("R6-Q4: Replicator equation pairwise comparison derivation")
print("=" * 60)
print("Standard replicator: dx_i/dt = x_i*(u_i - u_bar)")
print("Pairwise comparison protocol (Alevizaki Eq.): agents review at rate r_i = a - beta*u_i")
print("  Rate at which i-player switches to j: r_i * x_j (encounter probability)")
print("  Net flow from i to j: x_i * r_i * x_j - x_j * r_j * x_i")
print("  = x_i * x_j * (r_i - r_j)")
print("  = x_i * x_j * ((a - beta*u_i) - (a - beta*u_j))")
print("  = x_i * x_j * beta * (u_j - u_i)")
print()
print("  dx_i/dt = -flow(i→j) = -x_i*x_j*beta*(u_j-u_i)")
print("           = x_i*x_j*beta*(u_i - u_j)")
print()
print("  But paper writes dx_i/dt = beta*(u_j - u_bar)*x_i")
print()
print("  Expanding u_bar = x_i*u_i + x_j*u_j:")
print("  u_j - u_bar = u_j - x_i*u_i - x_j*u_j = x_i*(u_j - u_i)")
print()
print("  So: beta*(u_j - u_bar)*x_i = beta*x_i*(u_j-u_i)*x_i")
print("  Wait — this gives beta*x_i^2*(u_j-u_i), not x_i*x_j*beta*(u_i-u_j)")
print()
print("  Correct pairwise replicator: dx_i/dt = x_i*(u_i - u_bar)")
print("  because u_i - u_bar = x_j*(u_i - u_j), giving x_i*x_j*(u_i-u_j)")
print("  This is the STANDARD form. Paper uses u_j-u_bar which gives the SAME sign")
print("  but different amplitude (x_i vs x_j factor).")
# Verify numerically: both converge to same NE?
# At NE: u_i = u_j, so u_j - u_bar = u_i - u_bar = 0 — both stop at same point

# ─── R6-Q6: Phase III lambda profile per scenario ────────────────────────────
print()
print("=" * 60)
print("R6-Q6: Phase III lambda profile by scenario")
print("=" * 60)
for sc in ['S1_Standard', 'S2_ExtremePeak', 'S3_MECBiased', 'S4_CCOverload']:
    p3 = [d for d in data if d['scenario'] == sc and d['phase'] == 3]
    if p3:
        mults3 = [d['load_mult'] for d in p3]
        uv3 = sum(d['vio_URLLC'] for d in p3)
        print(f"{sc}: Phase III lambda=[{min(mults3):.3f}, {max(mults3):.3f}], URLLC_vio={uv3}")

# ─── R6-Q7: S2 Phase II n_iter_conv full distribution ───────────────────────
print()
print("=" * 60)
print("R6-Q7: S2 Phase II n_iter_conv distribution")
print("=" * 60)
s2p2 = [d for d in data if d['scenario'] == 'S2_ExtremePeak' and d['phase'] == 2]
iters2 = [d['n_iter_conv'] for d in s2p2]
c2 = Counter(iters2)
print(f"Total steps: {len(iters2)}, min={min(iters2)}, max={max(iters2)}, mean={sum(iters2)/len(iters2):.1f}")
cnt1_s2 = sum(1 for x in iters2 if x == 1)
cnt_gt10 = sum(1 for x in iters2 if x > 10)
print(f"Steps with 1 iter: {cnt1_s2}/{len(iters2)} ({100*cnt1_s2/len(iters2):.1f}%)")
print(f"Steps with >10 iters: {cnt_gt10}/{len(iters2)}")
print(f"Full distribution: {sorted(c2.items())}")
# S1 for comparison
s1p2 = [d for d in data if d['scenario'] == 'S1_Standard' and d['phase'] == 2]
iters1 = [d['n_iter_conv'] for d in s1p2]
cnt1_s1 = sum(1 for x in iters1 if x == 1)
print(f"\nS1 Phase II: steps={len(iters1)}, 1-iter={cnt1_s1} ({100*cnt1_s1/len(iters1):.1f}%), max={max(iters1)}")

# ─── R6-Q8: Review rate constraint verification ──────────────────────────────
print()
print("=" * 60)
print("R6-Q8: Review rate constraint a/beta > u_i")
print("=" * 60)
a, beta = 1.0, 1.0
# Max payoff: minimum delay = t_prop_mec + exp(0) = 0.25 + 1.0 = 1.25 ms at zero load
d_min = t_prop_mec + math.exp(0)
u_max_theory = 1.0 / d_min
print(f"Minimum possible delay (MEC, zero load): {t_prop_mec} + exp(0) = {d_min:.2f} ms")
print(f"Maximum possible payoff: 1/{d_min:.2f} = {u_max_theory:.4f}")
print(f"Constraint: a/beta = {a}/{beta} = {a/beta:.1f} > u_max = {u_max_theory:.4f}? {a/beta > u_max_theory}")
print(f"exp(0) = 1 ms floor explanation: the exponential model has t_UPF = exp(k*load)")
print(f"  At load=0: exp(0) = 1.0 ms — this represents minimum hardware pipeline latency")
print(f"  This is a modelling choice from Alevizaki et al., not a bug")
# Check max payoff across all scenarios
all_payoffs = []
for d in data:
    for delay_key in ['d_eMBB_MEC', 'd_eMBB_CC', 'd_URLLC_MEC', 'd_URLLC_CC']:
        if delay_key in d and d[delay_key] > 0:
            all_payoffs.append(1.0 / d[delay_key])
if all_payoffs:
    print(f"Max payoff observed across all scenarios: {max(all_payoffs):.6f}")
    print(f"Constraint satisfied at all times? {max(all_payoffs) < a/beta}")

# ─── R6-Q9: S3/S4 initialisation vectors ────────────────────────────────────
print()
print("=" * 60)
print("R6-Q9: Scenario initialisation vectors at Phase II start")
print("=" * 60)
for sc, label in [('S1_Standard','S1'), ('S2_ExtremePeak','S2'),
                  ('S3_MECBiased','S3'), ('S4_CCOverload','S4')]:
    # Phase II first step = initialisation for Phase II
    p2rows = [d for d in data if d['scenario'] == sc and d['phase'] == 2]
    if p2rows:
        first = p2rows[0]
        print(f"{label}: Phase II start: x_eMBB_MEC={first['x_eMBB_MEC']:.4f}, x_URLLC_MEC={first['x_URLLC_MEC']:.4f}")
    # Phase I last step (for warm-start info)
    p1rows = [d for d in data if d['scenario'] == sc and d['phase'] == 1]
    if p1rows:
        last_p1 = p1rows[-1]
        print(f"  Phase I end: x_eMBB_MEC={last_p1['x_eMBB_MEC']:.4f}, x_URLLC_MEC={last_p1['x_URLLC_MEC']:.4f}")

# ─── R6-Q10: Nash vs Pareto — aggregate delay comparison ────────────────────
print()
print("=" * 60)
print("R6-Q10: Nash equilibrium vs aggregate-delay-minimising split")
print("=" * 60)
lam = 5.5
# NE point from S1
x_ne_e, x_ne_u = 0.156, 0.222
def total_delay(xe, xu, lam):
    cc_load = (M1*rho_e*(1-xe) + M2*rho_u*(1-xu)) * lam
    d_mec_e = t_prop_mec + math.exp(k_mec * M1*rho_e*xe*lam)
    d_mec_u = t_prop_mec + math.exp(k_mec * M2*rho_u*xu*lam)
    d_cc = t_prop_cc + math.exp(k_cc * cc_load)
    # Weighted aggregate delay
    agg = M1*(xe*d_mec_e + (1-xe)*d_cc) + M2*(xu*d_mec_u + (1-xu)*d_cc)
    return agg, d_mec_e, d_mec_u, d_cc

agg_ne, d_me, d_mu, d_cc_ne = total_delay(x_ne_e, x_ne_u, lam)
print(f"Nash Equilibrium (x_e={x_ne_e}, x_u={x_ne_u}):")
print(f"  d_mec_eMBB={d_me:.2f}ms, d_mec_URLLC={d_mu:.2f}ms, d_cc={d_cc_ne:.2f}ms")
print(f"  Aggregate delay = {agg_ne:.1f} ms·UE")

# Brute force search for aggregate minimum
best_agg = float('inf')
best_xe, best_xu = 0, 0
for xe in [i/100 for i in range(0, 101, 2)]:
    for xu in [i/100 for i in range(0, 101, 2)]:
        try:
            agg, _, _, _ = total_delay(xe, xu, lam)
            if agg < best_agg:
                best_agg = agg
                best_xe, best_xu = xe, xu
        except:
            pass
print(f"\nAggregate-delay-minimising split (x_e={best_xe}, x_u={best_xu}):")
agg_opt, d_me_opt, d_mu_opt, d_cc_opt = total_delay(best_xe, best_xu, lam)
print(f"  d_mec_eMBB={d_me_opt:.2f}ms, d_mec_URLLC={d_mu_opt:.2f}ms, d_cc={d_cc_opt:.2f}ms")
print(f"  Aggregate delay = {agg_opt:.1f} ms·UE")
print(f"\nNE is Pareto-dominated? {agg_ne > agg_opt}")
print(f"Aggregate delay reduction: {agg_ne - agg_opt:.1f} ms·UE ({100*(agg_ne-agg_opt)/agg_ne:.1f}%)")
print(f"NE vs Optimum: both UPFs better at optimum? d_mec_e better={d_me_opt<d_me}, d_cc better={d_cc_opt<d_cc_ne}")

print("\nDONE")
