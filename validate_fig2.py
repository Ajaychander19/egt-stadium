"""
Reproduce Alevizaki et al. (2021) Fig. 2 exactly.
Key fix: use Alevizaki's original delay formulation (Eq. 5)
where t_UPF_i = exp(k_i * rho_UE * sum_g(M_g * x_i^g))
NOT the capacity-normalised version used in the stadium model.
"""
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ── Alevizaki's exact parameters ─────────────────────────────────────────────
M1, M2       = 130, 70          # UE populations
rho_UE       = 100.0            # Mbps per UE (same for both groups in Alevizaki)
t_prop_mec   = 0.25             # ms  (local UPF)
t_prop_cc    = 1.0              # ms  (central UPF, 4× further)
k_mec        = 4.89e-4          # exponent for local UPF  ← CORRECTED SCALE
k_cc         = 0.49e-4          # exponent for central UPF (ratio 10:1)
beta         = 1.0
epsilon      = 0.01
dt           = 0.05             # fine time step to show ~100 iterations

# ── Delay model: Alevizaki Eq. 5 ─────────────────────────────────────────────
def upf_delay(upf_idx, x):
    """t_UPFi = exp(k_i * rho_UE * (M1*x[0,i] + M2*x[1,i]))"""
    ks = [k_mec, k_cc]
    total_ues = M1 * x[0, upf_idx] + M2 * x[1, upf_idx]
    return np.exp(ks[upf_idx] * rho_UE * total_ues)

def e2e_delay(group, upf_idx, x):
    t_props = [t_prop_mec, t_prop_cc]
    return t_props[upf_idx] + upf_delay(upf_idx, x)

def payoff(group, upf_idx, x):
    return 1.0 / max(e2e_delay(group, upf_idx, x), 1e-12)

# ── Replicator dynamics ───────────────────────────────────────────────────────
def step(x):
    x_new = x.copy()
    for g in range(2):
        u     = np.array([payoff(g, i, x) for i in range(2)])
        u_bar = float(np.dot(x[g], u))
        dx    = beta * (u - u_bar) * x[g]
        x_new[g] = np.clip(x[g] + dx * dt, 1e-6, 1-1e-6)
        x_new[g] /= x_new[g].sum()
    return x_new

def is_converged(x):
    for g in range(2):
        u = np.array([payoff(g, i, x) for i in range(2)])
        if np.max(np.abs(u - u.mean())) > epsilon:
            return False
    return True

# ── Run ───────────────────────────────────────────────────────────────────────
x = np.full((2, 2), 0.5)
traj, delays = [x.copy()], []

for it in range(500):
    delays.append([[e2e_delay(g, i, x) for i in range(2)] for g in range(2)])
    x = step(x)
    traj.append(x.copy())
    if is_converged(x):
        print(f"Converged at iteration {it+1}")
        break

traj   = np.array(traj)
delays = np.array(delays)
iters  = np.arange(len(traj))
d_ax   = np.arange(len(delays))

# ── Plot ──────────────────────────────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle(
    r"Alevizaki et al. (2021) Fig. 2 — corrected reproduction"
    "\n"
    r"$M_1=130,\ M_2=70,\ \rho_{UE}=100\ \mathrm{Mbps},\ k_{mec}/k_{cc}=10$",
    fontsize=11
)

# (a) Strategy trajectories
ax1.plot(iters, traj[:,0,0], "b-",  lw=2, label="Group 1 (eMBB) — Local UPF")
ax1.plot(iters, traj[:,0,1], "b--", lw=2, label="Group 1 (eMBB) — Central UPF")
ax1.plot(iters, traj[:,1,0], "r-",  lw=2, label="Group 2 (URLLC) — Local UPF")
ax1.plot(iters, traj[:,1,1], "r--", lw=2, label="Group 2 (URLLC) — Central UPF")
ax1.set(xlabel="Iterations", ylabel="Probability distribution of strategies",
        title="(a) Strategy trajectories", ylim=(0, 1))
ax1.legend(fontsize=9); ax1.grid(alpha=0.3)
ax1.text(0.97, 0.5,
         f"Eq: G1@MEC={traj[-1,0,0]*100:.0f}%\nEq: G2@MEC={traj[-1,1,0]*100:.0f}%",
         transform=ax1.transAxes, ha="right", va="center", fontsize=9,
         bbox=dict(boxstyle="round", fc="white", alpha=0.8))

# (b) Delay convergence
ax2.plot(d_ax, delays[:,0,0], "b-",  lw=2, label="Local UPF — Group 1")
ax2.plot(d_ax, delays[:,1,0], "r-",  lw=2, label="Local UPF — Group 2")
ax2.plot(d_ax, delays[:,0,1], "g--", lw=2, label="Central UPF")
mean_eq = float(np.mean(delays[-10:]))
ax2.axhline(mean_eq, color="k", ls=":", lw=1.5,
            label=f"Theoretical avg ({mean_eq:.2f} ms)")
ax2.set(xlabel="Iterations", ylabel="Delay (ms)",
        title="(b) Delay convergence to equilibrium")
ax2.legend(fontsize=9); ax2.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("results/fig2_reproduction.png", dpi=150, bbox_inches="tight")

# ── Report ────────────────────────────────────────────────────────────────────
eq     = traj[-1]
spread = delays[-1].max() - delays[-1].min()
ok     = spread < 0.05 and 80 < len(traj) < 150

print("\n" + "="*55)
print("VALIDATION RESULTS")
print("="*55)
print(f"  Converged at : {len(traj)-1} iterations  (want 80–120)")
print(f"  G1 at MEC    : {eq[0,0]*100:.1f}%  (want ~16%)")
print(f"  G2 at MEC    : {eq[1,0]*100:.1f}%  (want ~32%)")
print(f"  Delay spread : {spread:.4f} ms  (want < 0.05)")
print(f"  Result       : {'✓ PASS' if ok else '✗ FAIL — check k scale'}")
print(f"  Saved        : results/fig2_reproduction.png")
print("="*55)
