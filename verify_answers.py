"""
Full verification script for peer-review answers.
Run this to confirm every number reported in the paper and in the peer-review response.
"""
from egt_controller import EGTController, SystemParams
import numpy as np
import pandas as pd

p = SystemParams(epsilon=0.01)

# ------------------------------------------------------------------
# 1. Alevizaki Fig 2 validation (k values calibrated correctly?)
# ------------------------------------------------------------------
print("=== 1. ALEVIZAKI FIG 2 VALIDATION ===")
p_val = SystemParams(M1=130, M2=70, rho_embb=100.0, rho_urllc=100.0, epsilon=0.01)
c_val = EGTController(params=p_val)
c_val.x = np.array([[0.5, 0.5], [0.5, 0.5]])
res_val = c_val.run_to_equilibrium(load_mult=1.0, max_iter=2000, dt=0.05)
eq = res_val["equilibrium"]
print(f"  G1 eMBB  @ MEC: {eq[0,0]*100:.2f}%  (Expected ~17.8%)")
print(f"  G2 URLLC @ MEC: {eq[1,0]*100:.2f}%  (Expected ~32.0%)")
print(f"  Iterations     : {res_val['n_iter']}")
print()

# ------------------------------------------------------------------
# 2. S1 standard peak — static from 0.5
# ------------------------------------------------------------------
print("=== 2. S1 STATIC PEAK CONVERGENCE (5.5x, start 0.5) ===")
c1 = EGTController(params=p)
c1.x = np.array([[0.5, 0.5], [0.5, 0.5]])
res1 = c1.run_to_equilibrium(load_mult=5.5, max_iter=2000, dt=0.05)
eq1 = res1["equilibrium"]
d_embb_mec_s1 = c1.e2e_delay(0, 0, eq1, 5.5)
d_embb_cc_s1  = c1.e2e_delay(0, 1, eq1, 5.5)
d_urllc_mec_s1 = c1.e2e_delay(1, 0, eq1, 5.5)
d_urllc_cc_s1  = c1.e2e_delay(1, 1, eq1, 5.5)
print(f"  x_eMBB_MEC    : {eq1[0,0]:.4f}  x_URLLC_MEC: {eq1[1,0]:.4f}")
print(f"  MEC eMBB delay: {d_embb_mec_s1:.3f} ms   CC eMBB delay: {d_embb_cc_s1:.3f} ms")
print(f"  MEC URLLC delay:{d_urllc_mec_s1:.3f} ms   CC URLLC delay:{d_urllc_cc_s1:.3f} ms")
print(f"  Iterations     : {res1['n_iter']}")
# Weighted average delays at this equilibrium
p_full = SystemParams()
embb_mec_ues  = round(eq1[0,0] * p_full.M1)
embb_cc_ues   = round(eq1[0,1] * p_full.M1)
urllc_mec_ues = round(eq1[1,0] * p_full.M2)
urllc_cc_ues  = round(eq1[1,1] * p_full.M2)
mec_mbps = (embb_mec_ues * p_full.rho_embb + urllc_mec_ues * p_full.rho_urllc) * 5.5
cc_mbps  = (embb_cc_ues  * p_full.rho_embb + urllc_cc_ues  * p_full.rho_urllc) * 5.5
print(f"  MEC load: {mec_mbps/1000:.2f} Gbps   CC load: {cc_mbps/1000:.2f} Gbps   Total: {(mec_mbps+cc_mbps)/1000:.2f} Gbps")
avg_embb   = eq1[0,0]*d_embb_mec_s1  + eq1[0,1]*d_embb_cc_s1
avg_urllc  = eq1[1,0]*d_urllc_mec_s1 + eq1[1,1]*d_urllc_cc_s1
print(f"  Avg eMBB delay: {avg_embb:.1f} ms   Avg URLLC delay: {avg_urllc:.1f} ms")
print()

# ------------------------------------------------------------------
# 3. S3 MEC overload — static from 0.9
# ------------------------------------------------------------------
print("=== 3. S3 STATIC MEC OVERLOAD (5.5x, start 0.9) ===")
c3 = EGTController(params=p)
c3.x = np.array([[0.9, 0.1], [0.9, 0.1]])
res3 = c3.run_to_equilibrium(load_mult=5.5, max_iter=2000, dt=0.05)
eq3 = res3["equilibrium"]
print(f"  x_eMBB_MEC    : {eq3[0,0]:.4f}  x_URLLC_MEC: {eq3[1,0]:.4f}")
print(f"  Iterations     : {res3['n_iter']}")
print()

# ------------------------------------------------------------------
# 4. S4 CC overload — static from 0.05
# ------------------------------------------------------------------
print("=== 4. S4 STATIC CC OVERLOAD (5.5x, start 0.05) ===")
c4 = EGTController(params=p)
c4.x = np.array([[0.05, 0.95], [0.05, 0.95]])
res4 = c4.run_to_equilibrium(load_mult=5.5, max_iter=2000, dt=0.05)
eq4 = res4["equilibrium"]
print(f"  x_eMBB_MEC    : {eq4[0,0]:.4f}  x_URLLC_MEC: {eq4[1,0]:.4f}")
print(f"  Iterations     : {res4['n_iter']}")
print()

# ------------------------------------------------------------------
# 5. S2 coarse epsilon local trap (static 10x from 0.5)
# ------------------------------------------------------------------
print("=== 5. S2 COARSE EPSILON TRAP (10x, static from 0.5) ===")
c2_trap = EGTController(params=p)
c2_trap.x = np.array([[0.5, 0.5], [0.5, 0.5]])
res2_trap = c2_trap.run_to_equilibrium(load_mult=10.0, max_iter=2000, dt=0.05)
eq2t = res2_trap["equilibrium"]
d_mec_trap = c2_trap.e2e_delay(0, 0, eq2t, 10.0)
d_cc_trap  = c2_trap.e2e_delay(0, 1, eq2t, 10.0)
avg_delay_trap = eq2t[0,0]*d_mec_trap + eq2t[0,1]*d_cc_trap
print(f"  x_eMBB_MEC    : {eq2t[0,0]:.4f}  x_URLLC_MEC: {eq2t[1,0]:.4f}")
print(f"  MEC eMBB delay: {d_mec_trap:.1f} ms")
print(f"  CC  eMBB delay: {d_cc_trap:.1f} ms")
print(f"  Avg eMBB delay: {avg_delay_trap:.1f} ms")
print(f"  Iterations     : {res2_trap['n_iter']}")
print()

# ------------------------------------------------------------------
# 6. S2 tight epsilon true Nash Equilibrium
# ------------------------------------------------------------------
print("=== 6. S2 TIGHT EPSILON TRUE NASH NE (10x, eps=1e-5) ===")
p_tight = SystemParams(epsilon=1e-5)
c2_tight = EGTController(params=p_tight)
c2_tight.x = np.array([[0.5, 0.5], [0.5, 0.5]])
res2_tight = c2_tight.run_to_equilibrium(load_mult=10.0, max_iter=10000, dt=0.05)
eq2n = res2_tight["equilibrium"]
d_mec_ne = c2_tight.e2e_delay(0, 0, eq2n, 10.0)
d_cc_ne  = c2_tight.e2e_delay(0, 1, eq2n, 10.0)
avg_ne   = eq2n[0,0]*d_mec_ne + eq2n[0,1]*d_cc_ne
print(f"  x_eMBB_MEC    : {eq2n[0,0]:.5f}")
print(f"  MEC eMBB delay: {d_mec_ne:.3f} ms  CC eMBB delay: {d_cc_ne:.3f} ms")
print(f"  Avg eMBB delay: {avg_ne:.1f} ms")
print(f"  Iterations     : {res2_tight['n_iter']}")
print()

# ------------------------------------------------------------------
# 7. S2 dynamic tracking equilibrium (start from end of Phase I)
# ------------------------------------------------------------------
print("=== 7. S2 DYNAMIC TRACKING (10x, start from Phase I end) ===")
c2_track = EGTController(params=p)
c2_track.x = np.array([[0.5, 0.5], [0.5, 0.5]])
# Simulate Phase I (ramp up to 1.0x over 90 steps)
for t in range(90):
    mult_i = 1.0 * (t + 1) / 90
    c2_track.run_to_equilibrium(load_mult=mult_i, max_iter=2000, dt=0.05)
x_phase1_end = c2_track.x.copy()
print(f"  x after Phase I: eMBB_MEC={x_phase1_end[0,0]:.4f}  URLLC_MEC={x_phase1_end[1,0]:.4f}")
# Now step into 10x peak
res2_track = c2_track.run_to_equilibrium(load_mult=10.0, max_iter=2000, dt=0.05)
eq2_track = res2_track["equilibrium"]
d_mec_tr = c2_track.e2e_delay(0, 0, eq2_track, 10.0)
d_cc_tr  = c2_track.e2e_delay(0, 1, eq2_track, 10.0)
avg_tr   = eq2_track[0,0]*d_mec_tr + eq2_track[0,1]*d_cc_tr
print(f"  x_eMBB_MEC tracking: {eq2_track[0,0]:.4f}  x_URLLC_MEC: {eq2_track[1,0]:.4f}")
print(f"  MEC delay: {d_mec_tr:.1f} ms   CC delay: {d_cc_tr:.1f} ms")
print(f"  Avg eMBB delay: {avg_tr:.1f} ms")
print(f"  Iterations at first 10x step: {res2_track['n_iter']}")
print()

# ------------------------------------------------------------------
# 8. Static baseline 50/50 at 5.5x
# ------------------------------------------------------------------
print("=== 8. BASELINE STATIC 50/50 at 5.5x ===")
c_base = EGTController(params=p)
c_base.x = np.array([[0.5, 0.5], [0.5, 0.5]])
d_mec_base_embb  = c_base.e2e_delay(0, 0, c_base.x, 5.5)
d_cc_base_embb   = c_base.e2e_delay(0, 1, c_base.x, 5.5)
d_mec_base_urllc = c_base.e2e_delay(1, 0, c_base.x, 5.5)
d_cc_base_urllc  = c_base.e2e_delay(1, 1, c_base.x, 5.5)
avg_base_embb  = 0.5*d_mec_base_embb  + 0.5*d_cc_base_embb
avg_base_urllc = 0.5*d_mec_base_urllc + 0.5*d_cc_base_urllc
mec_base = (400*10 + 100*25)*5.5
cc_base  = (400*10 + 100*25)*5.5
print(f"  MEC eMBB delay:  {d_mec_base_embb:.1f} ms")
print(f"  CC  eMBB delay:  {d_cc_base_embb:.3f} ms")
print(f"  MEC URLLC delay: {d_mec_base_urllc:.1f} ms")
print(f"  CC  URLLC delay: {d_cc_base_urllc:.3f} ms")
print(f"  Avg eMBB delay:  {avg_base_embb:.1f} ms")
print(f"  Avg URLLC delay: {avg_base_urllc:.1f} ms")
print(f"  MEC load: {mec_base/1000:.2f} Gbps   CC load: {cc_base/1000:.2f} Gbps")
print()
