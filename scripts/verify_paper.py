"""
Paper Verification Script — UpfSelectionAjay-2.pdf
Verifies every numerical claim in the paper against the simulation code.
"""
from egt_controller import EGTController, SystemParams
import numpy as np
import pandas as pd
import os
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


p = SystemParams(epsilon=0.01)
results = {}

print("=" * 70)
print("PAPER CLAIM VERIFICATION REPORT")
print("=" * 70)

# ──────────────────────────────────────────────────────────────────
# CLAIM 1: Parameters (Table I)
# ──────────────────────────────────────────────────────────────────
print("\n[PARAMS] Table I parameters from egt_controller.py:")
print(f"  M1={p.M1}  M2={p.M2}  rho_eMBB={p.rho_embb}  rho_URLLC={p.rho_urllc}")
print(f"  t_prop_mec={p.t_prop_mec}  t_prop_cc={p.t_prop_cc}")
print(f"  k_mec={p.k_mec:.4e}  k_cc={p.k_cc:.4e}  ratio={p.k_mec/p.k_cc:.1f}")
print(f"  beta={p.beta}  epsilon={p.epsilon}  dt=0.05")
print(f"  PDB_eMBB={p.PDB_embb}ms  PDB_URLLC={p.PDB_urllc}ms")
paper_load_base = (p.M1 * p.rho_embb + p.M2 * p.rho_urllc)
print(f"\n[CLAIM] Base offered load: {paper_load_base/1000:.0f} Gbps (paper claims 13 Gbps)")
print(f"  VERIFIED: {paper_load_base/1000:.1f} Gbps {'✓' if paper_load_base/1000 == 13.0 else '✗'}")
print(f"[CLAIM] At 5.5x: {paper_load_base*5.5/1000:.1f} Gbps (paper claims 71.5 Gbps)")
print(f"  VERIFIED: {'✓' if paper_load_base*5.5/1000 == 71.5 else '✗'}")

# ──────────────────────────────────────────────────────────────────
# CLAIM 2: Alevizaki Fig 2 reproduction
# ──────────────────────────────────────────────────────────────────
print("\n[CLAIM] Alevizaki Fig.2: G1=17.82%, G2=31.97%, 231 iterations")
p_val = SystemParams(M1=130, M2=70, rho_embb=100.0, rho_urllc=100.0, epsilon=0.01)
c_val = EGTController(params=p_val)
c_val.x = np.array([[0.5, 0.5], [0.5, 0.5]])
r_val = c_val.run_to_equilibrium(load_mult=1.0, max_iter=2000, dt=0.05)
eq_val = r_val["equilibrium"]
print(f"  G1@MEC={eq_val[0,0]*100:.2f}%  G2@MEC={eq_val[1,0]*100:.2f}%  iters={r_val['n_iter']}")
print(f"  G1 {'✓' if abs(eq_val[0,0]*100 - 17.82) < 0.05 else '✗'}  "
      f"G2 {'✓' if abs(eq_val[1,0]*100 - 31.97) < 0.05 else '✗'}  "
      f"Iters {'✓' if r_val['n_iter'] == 231 else '✗'}")

# ──────────────────────────────────────────────────────────────────
# CLAIM 3: S1 Standard peak (static cold-start from 0.5)
# ──────────────────────────────────────────────────────────────────
print("\n[CLAIM] S1 Standard 5.5x: x_eMBB=0.156, x_URLLC=0.222, 505 iters")
c1 = EGTController(params=p)
c1.x = np.array([[0.5, 0.5], [0.5, 0.5]])
r1 = c1.run_to_equilibrium(load_mult=5.5, max_iter=2000, dt=0.05)
eq1 = r1["equilibrium"]
d_embb_mec_s1  = c1.e2e_delay(0, 0, eq1, 5.5)
d_embb_cc_s1   = c1.e2e_delay(0, 1, eq1, 5.5)
d_urllc_mec_s1 = c1.e2e_delay(1, 0, eq1, 5.5)
d_urllc_cc_s1  = c1.e2e_delay(1, 1, eq1, 5.5)
embb_mec  = round(eq1[0,0] * p.M1);  embb_cc  = round(eq1[0,1] * p.M1)
urllc_mec = round(eq1[1,0] * p.M2);  urllc_cc = round(eq1[1,1] * p.M2)
mec_gbps_s1 = (embb_mec*p.rho_embb + urllc_mec*p.rho_urllc)*5.5/1000
cc_gbps_s1  = (embb_cc*p.rho_embb  + urllc_cc*p.rho_urllc)*5.5/1000
avg_embb_s1   = eq1[0,0]*d_embb_mec_s1  + eq1[0,1]*d_embb_cc_s1
avg_urllc_s1  = eq1[1,0]*d_urllc_mec_s1 + eq1[1,1]*d_urllc_cc_s1
vio_s1 = c1.count_violations(eq1, 5.5)
print(f"  x_eMBB_MEC={eq1[0,0]:.3f} {'✓' if abs(eq1[0,0]-0.156)<0.002 else '✗ MISMATCH'}")
print(f"  x_URLLC_MEC={eq1[1,0]:.3f} {'✓' if abs(eq1[1,0]-0.222)<0.002 else '✗ MISMATCH'}")
print(f"  MEC load={mec_gbps_s1:.1f} Gbps (paper: 12.9) {'✓' if abs(mec_gbps_s1-12.9)<0.2 else '✗'}")
print(f"  CC load={cc_gbps_s1:.1f} Gbps (paper: 58.6) {'✓' if abs(cc_gbps_s1-58.6)<0.2 else '✗'}")
print(f"  eMBB MEC delay={d_embb_mec_s1:.1f}ms (paper: 27.9) {'✓' if abs(d_embb_mec_s1-27.9)<0.5 else '✗'}")
print(f"  eMBB CC delay={d_embb_cc_s1:.1f}ms (paper: 17.9) {'✓' if abs(d_embb_cc_s1-17.9)<0.5 else '✗'}")
print(f"  avg eMBB delay={avg_embb_s1:.1f}ms (paper: 19.5) {'✓' if abs(avg_embb_s1-19.5)<0.5 else '✗'}")
print(f"  URLLC MEC delay={d_urllc_mec_s1:.1f}ms (paper: 19.5) {'✓' if abs(d_urllc_mec_s1-19.5)<0.5 else '✗'}")
print(f"  URLLC CC delay={d_urllc_cc_s1:.1f}ms (paper: 17.9) {'✓' if abs(d_urllc_cc_s1-17.9)<0.5 else '✗'}")
print(f"  avg URLLC delay={avg_urllc_s1:.1f}ms (paper: 18.3) {'✓' if abs(avg_urllc_s1-18.3)<0.5 else '✗'}")
print(f"  Iterations={r1['n_iter']} (paper: 505) {'✓' if r1['n_iter']==505 else '✗'}")
print(f"  eMBB vio at eq={vio_s1['eMBB']} (paper: 0) {'✓' if vio_s1['eMBB']==0 else '✗'}")
print(f"  URLLC vio at eq step={vio_s1['URLLC']} (paper: 26316 cumulative)")

# ──────────────────────────────────────────────────────────────────
# CLAIM 4: S3 MEC Overload (static from 0.9)
# ──────────────────────────────────────────────────────────────────
print("\n[CLAIM] S3 MEC Overload 5.5x: x_eMBB=0.156, x_URLLC=0.223, 670 iters")
c3 = EGTController(params=p)
c3.x = np.array([[0.9, 0.1], [0.9, 0.1]])
r3 = c3.run_to_equilibrium(load_mult=5.5, max_iter=2000, dt=0.05)
eq3 = r3["equilibrium"]
print(f"  x_eMBB_MEC={eq3[0,0]:.3f} {'✓' if abs(eq3[0,0]-0.156)<0.002 else '✗'}")
print(f"  x_URLLC_MEC={eq3[1,0]:.3f} (paper: 0.223) {'✓' if abs(eq3[1,0]-0.223)<0.003 else '✗'}")
print(f"  Iterations={r3['n_iter']} (paper: 670) {'✓' if r3['n_iter']==670 else '✗'}")
embb_mec3  = round(eq3[0,0]*p.M1); urllc_mec3 = round(eq3[1,0]*p.M2)
embb_cc3   = round(eq3[0,1]*p.M1); urllc_cc3  = round(eq3[1,1]*p.M2)
mec_s3 = (embb_mec3*p.rho_embb + urllc_mec3*p.rho_urllc)*5.5/1000
cc_s3  = (embb_cc3*p.rho_embb   + urllc_cc3*p.rho_urllc)*5.5/1000
print(f"  MEC={mec_s3:.1f} Gbps (paper: 12.9) {'✓' if abs(mec_s3-12.9)<0.3 else '✗'}")
print(f"  CC={cc_s3:.1f} Gbps (paper: 58.6) {'✓' if abs(cc_s3-58.6)<0.3 else '✗'}")

# ──────────────────────────────────────────────────────────────────
# CLAIM 5: S4 CC Overload (static from 0.05)
# ──────────────────────────────────────────────────────────────────
print("\n[CLAIM] S4 CC Overload 5.5x: x_eMBB=0.128, x_URLLC=0.198, 270 iters")
c4 = EGTController(params=p)
c4.x = np.array([[0.05, 0.95], [0.05, 0.95]])
r4 = c4.run_to_equilibrium(load_mult=5.5, max_iter=2000, dt=0.05)
eq4 = r4["equilibrium"]
embb_mec4  = round(eq4[0,0]*p.M1); urllc_mec4 = round(eq4[1,0]*p.M2)
embb_cc4   = round(eq4[0,1]*p.M1); urllc_cc4  = round(eq4[1,1]*p.M2)
mec_s4 = (embb_mec4*p.rho_embb + urllc_mec4*p.rho_urllc)*5.5/1000
cc_s4  = (embb_cc4*p.rho_embb   + urllc_cc4*p.rho_urllc)*5.5/1000
print(f"  x_eMBB_MEC={eq4[0,0]:.3f} (paper: 0.128) {'✓' if abs(eq4[0,0]-0.128)<0.002 else '✗'}")
print(f"  x_URLLC_MEC={eq4[1,0]:.3f} (paper: 0.198) {'✓' if abs(eq4[1,0]-0.198)<0.003 else '✗'}")
print(f"  Iterations={r4['n_iter']} (paper: 270) {'✓' if r4['n_iter']==270 else '✗'}")
print(f"  MEC={mec_s4:.1f} Gbps (paper: 11.2) {'✓' if abs(mec_s4-11.2)<0.3 else '✗'}")
print(f"  CC={cc_s4:.1f} Gbps (paper: 60.3) {'✓' if abs(cc_s4-60.3)<0.3 else '✗'}")

# ──────────────────────────────────────────────────────────────────
# CLAIM 6: Baseline 50/50 at 5.5x
# ──────────────────────────────────────────────────────────────────
print("\n[CLAIM] Baseline 50/50: MEC=35.8Gbps, CC=35.8Gbps, eMBB avg=20736ms, URLLC=388ms")
c_b = EGTController(params=p)
c_b.x = np.array([[0.5, 0.5], [0.5, 0.5]])
d_mec_b_e  = c_b.e2e_delay(0, 0, c_b.x, 5.5)
d_cc_b_e   = c_b.e2e_delay(0, 1, c_b.x, 5.5)
d_mec_b_u  = c_b.e2e_delay(1, 0, c_b.x, 5.5)
d_cc_b_u   = c_b.e2e_delay(1, 1, c_b.x, 5.5)
avg_b_e = 0.5*d_mec_b_e + 0.5*d_cc_b_e
avg_b_u = 0.5*d_mec_b_u + 0.5*d_cc_b_u
mec_b = (400*p.rho_embb + 100*p.rho_urllc)*5.5/1000
cc_b  = (400*p.rho_embb + 100*p.rho_urllc)*5.5/1000
vio_b = c_b.count_violations(c_b.x, 5.5)
print(f"  MEC load={mec_b:.1f} Gbps (paper: 35.8) {'✓' if abs(mec_b-35.8)<0.1 else '✗'}")
print(f"  CC load={cc_b:.1f} Gbps (paper: 35.8) {'✓' if abs(cc_b-35.8)<0.1 else '✗'}")
print(f"  MEC eMBB delay={d_mec_b_e:.0f}ms (paper: ~41500) {'✓' if abs(d_mec_b_e-41465)<200 else '✗'}")
print(f"  CC eMBB delay={d_cc_b_e:.3f}ms (paper: 6.6) {'✓' if abs(d_cc_b_e-6.6)<0.2 else '✗'}")
print(f"  MEC URLLC delay={d_mec_b_u:.1f}ms (paper: 769) {'✓' if abs(d_mec_b_u-769)<5 else '✗'}")
print(f"  Avg eMBB delay={avg_b_e:.0f}ms (paper: 20736) {'✓' if abs(avg_b_e-20736)<50 else '✗'}")
print(f"  Avg URLLC delay={avg_b_u:.1f}ms (paper: 388) {'✓' if abs(avg_b_u-388)<5 else '✗'}")
print(f"  eMBB vio={vio_b['eMBB']} (paper: 400) {'✓' if vio_b['eMBB']==400 else '✗'}")
print(f"  URLLC vio={vio_b['URLLC']} (paper: 100) {'✓' if vio_b['URLLC']==100 else '✗'}")

# ──────────────────────────────────────────────────────────────────
# CLAIM 7: S2 coarse epsilon trap
# ──────────────────────────────────────────────────────────────────
print("\n[CLAIM] S2 coarse trap: x_eMBB=0.380, MEC delay=2.4e6ms, MEC load=49.4Gbps")
c2t = EGTController(params=p)
c2t.x = np.array([[0.5, 0.5], [0.5, 0.5]])
r2t = c2t.run_to_equilibrium(load_mult=10.0, max_iter=2000, dt=0.05)
eq2t = r2t["equilibrium"]
d_mec_t = c2t.e2e_delay(0, 0, eq2t, 10.0)
d_cc_t  = c2t.e2e_delay(0, 1, eq2t, 10.0)
embb_mec_t = round(eq2t[0,0]*p.M1); urllc_mec_t = round(eq2t[1,0]*p.M2)
embb_cc_t  = round(eq2t[0,1]*p.M1); urllc_cc_t  = round(eq2t[1,1]*p.M2)
mec_t_gbps = (embb_mec_t*p.rho_embb + urllc_mec_t*p.rho_urllc)*10.0/1000
print(f"  x_eMBB_MEC={eq2t[0,0]:.3f} (paper: 0.380) {'✓' if abs(eq2t[0,0]-0.380)<0.003 else '✗'}")
print(f"  MEC delay={d_mec_t:.2e}ms (paper: ~2.4e6) {'✓' if d_mec_t > 1e6 else '✗'}")
print(f"  MEC load={mec_t_gbps:.1f} Gbps (paper: 49.4) {'✓' if abs(mec_t_gbps-49.4)<1 else '✗'}")

# ──────────────────────────────────────────────────────────────────
# CLAIM 8: S2 true NE (tight epsilon)
# ──────────────────────────────────────────────────────────────────
print("\n[CLAIM] S2 tight NE: x_eMBB=0.136, avg delay=188.8ms, 7673 iters")
p_tight = SystemParams(epsilon=1e-5)
c2n = EGTController(params=p_tight)
c2n.x = np.array([[0.5, 0.5], [0.5, 0.5]])
r2n = c2n.run_to_equilibrium(load_mult=10.0, max_iter=10000, dt=0.05)
eq2n = r2n["equilibrium"]
d_mec_n = c2n.e2e_delay(0, 0, eq2n, 10.0)
d_cc_n  = c2n.e2e_delay(0, 1, eq2n, 10.0)
avg_n   = eq2n[0,0]*d_mec_n + eq2n[0,1]*d_cc_n
print(f"  x_eMBB_MEC={eq2n[0,0]:.3f} (paper: 0.136) {'✓' if abs(eq2n[0,0]-0.136)<0.002 else '✗'}")
print(f"  avg delay={avg_n:.1f}ms (paper: 188.8) {'✓' if abs(avg_n-188.8)<2 else '✗'}")
print(f"  iters={r2n['n_iter']} (paper: 7673) {'✓' if r2n['n_iter']==7673 else '✗'}")

# ──────────────────────────────────────────────────────────────────
# CLAIM 9: Abstract — "under 100 iterations" claim
# ──────────────────────────────────────────────────────────────────
print("\n[CLAIM] Abstract: 'converges in under 100 iterations across all conditions'")
print(f"  S1 static cold-start iters = {r1['n_iter']} {'✗ WRONG (505)' if r1['n_iter'] > 100 else '✓'}")
print(f"  S3 static cold-start iters = {r3['n_iter']} {'✗ WRONG (670)' if r3['n_iter'] > 100 else '✓'}")
print(f"  S4 static cold-start iters = {r4['n_iter']} {'✗ WRONG (270)' if r4['n_iter'] > 100 else '✓'}")
print(f"  *** This abstract claim is INCORRECT and must be fixed ***")

# ──────────────────────────────────────────────────────────────────
# CLAIM 10: Load from simulation results JSON
# ──────────────────────────────────────────────────────────────────
print("\n[CLAIM] Cumulative violations from simulation results JSON")
try:
    df = pd.read_json(os.path.join(BASE_DIR, "results/multi_scenario_results.json"))
    for sc, grp in df.groupby("scenario"):
        e_vio = grp["vio_eMBB"].sum()
        u_vio = grp["vio_URLLC"].sum()
        print(f"  {sc}: eMBB vio={e_vio}  URLLC vio={u_vio}")
except Exception as ex:
    print(f"  Could not load results JSON: {ex}")

print("\n" + "=" * 70)
print("ERRORS REQUIRING PAPER CORRECTIONS:")
print("=" * 70)
print("  1. Abstract line 'converges in under 100 iterations across all")
print("     evaluated conditions' is WRONG.")
print("     Truth: S1=505 iters, S3=670 iters, S4=270 iters (static cold-start).")
print("     Warm-start tracking for S2 per-step = 1-147 iters.")
print("")
print("  2. Conclusion section contains: 'the system doesn't converges to a")
print("     stable equilibrium in under 100 iterations in all evaluated")
print("     conditions, inconsistent with the theoretical bound'")
print("     This is a typo ('doesn't converges') and a self-contradiction.")
print("     Suggested fix: 'the EGT controller converges to a stable")
print("     equilibrium in under 700 iterations across all evaluated")
print("     scenarios, with warm-start step tracking completing in 1")
print("     iteration per step once the system reaches the active")
print("     equilibrium.'")
