"""
Stadium Multi-Scenario Simulation — Capacity-Constrained EGT Steering
Scenarios:
  S1 — Normal 3-Phase Stadium Event (Ramp-up / Peak / Dispersal)
  S2 — Extreme Halftime Spike (10x load, tests URLLC limits)
  S3 — MEC Overload Spillover (MEC saturated, eMBB forced to CC)
  S4 — CC Overload Spillover (CC saturated, eMBB spills to MEC)
"""
import json, logging
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd
from egt_controller import EGTController, SystemParams
import os
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))


logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [SIM] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("sim")

# ── Standard 3-Phase Definition ──────────────────────────────────────────────
PHASES = {
    1: {"label": "Phase I — Ramp-up",    "mins": 30, "mult": 1.0,  "ramp": True},
    2: {"label": "Phase II — Peak",       "mins": 45, "mult": 5.5,  "ramp": False},
    3: {"label": "Phase III — Dispersal", "mins": 20, "mult": 0.3,  "ramp": False},
}
STEPS_PER_MIN = 3

# ── Helper: run one scenario ──────────────────────────────────────────────────

def run_scenario(scenario_phases, label, smf_url=None, x_init=None):
    """Run EGT simulation for a given phase profile, return DataFrame."""
    p   = SystemParams()
    ctl = EGTController(params=p, smf_base_url=smf_url)
    if x_init is not None:
        ctl.x = np.array(x_init)
    records, global_t, prev_mult = [], 0, 0.01

    for ph, cfg in scenario_phases.items():
        n = cfg["mins"] * STEPS_PER_MIN
        log.info(f"[{label}] {cfg['label']} — {n} steps @ x{cfg.get('mult',1.0)}")

        for t in range(n):
            if cfg.get("ramp", False):
                mult = cfg["mult"] * (t + 1) / n
            else:
                if t < 10:
                    mult = prev_mult + (cfg["mult"] - prev_mult) * (t + 1) / 10
                else:
                    mult = cfg["mult"]

            ctl.poll_smf()
            res = ctl.run_to_equilibrium(load_mult=mult, max_iter=400, dt=0.05)
            vio = ctl.count_violations(ctl.x, mult)

            d_urllc_mec = ctl.e2e_delay(1, 0, ctl.x, mult)
            d_urllc_cc  = ctl.e2e_delay(1, 1, ctl.x, mult)
            infra_limited = (d_urllc_mec > p.PDB_urllc and d_urllc_cc > p.PDB_urllc)

            st = ctl.status(mult)
            se, _ = ctl.steer(0)
            su, _ = ctl.steer(1)

            # Absolute UE counts
            embb_mec_ues  = round(ctl.x[0, 0] * p.M1)
            embb_cc_ues   = round(ctl.x[0, 1] * p.M1)
            urllc_mec_ues = round(ctl.x[1, 0] * p.M2)
            urllc_cc_ues  = round(ctl.x[1, 1] * p.M2)

            # Throughput Mbps
            mec_mbps = (embb_mec_ues * p.rho_embb) + (urllc_mec_ues * p.rho_urllc)
            cc_mbps  = (embb_cc_ues  * p.rho_embb) + (urllc_cc_ues  * p.rho_urllc)

            records.append({
                "scenario":      label,
                "phase":         ph,
                "phase_label":   cfg["label"],
                "global_t":      global_t,
                "load_mult":     round(mult, 3),
                **{k: round(v, 4) for k, v in st.items()},
                "vio_eMBB":      vio["eMBB"],
                "vio_URLLC":     vio["URLLC"],
                "infra_limited": int(infra_limited),
                "d_urllc_mec":   round(d_urllc_mec, 3),
                "d_urllc_cc":    round(d_urllc_cc, 3),
                "n_iter_conv":   res["n_iter"],
                "steer_eMBB":    se,
                "steer_URLLC":   su,
                "embb_mec_ues":  embb_mec_ues,
                "embb_cc_ues":   embb_cc_ues,
                "urllc_mec_ues": urllc_mec_ues,
                "urllc_cc_ues":  urllc_cc_ues,
                "mec_mbps":      round(mec_mbps, 1),
                "cc_mbps":       round(cc_mbps, 1),
            })
            global_t += 1
            prev_mult = mult

    return pd.DataFrame(records)


# ── Scenario Definitions ──────────────────────────────────────────────────────

def run_all(smf_url=None):
    results = {}

    # S1: Standard 3-Phase Event
    log.info("="*60 + "\nS1: Standard Stadium 3-Phase Event\n" + "="*60)
    results["S1_Standard"] = run_scenario(PHASES, "S1_Standard", smf_url)

    # S2: Extreme Spike (10x halftime — stress test)
    extreme_phases = {
        1: {"label": "Phase I — Ramp-up",       "mins": 30, "mult": 1.0,  "ramp": True},
        2: {"label": "Phase II — Extreme Spike", "mins": 45, "mult": 10.0, "ramp": False},
        3: {"label": "Phase III — Dispersal",    "mins": 20, "mult": 0.3,  "ramp": False},
    }
    log.info("="*60 + "\nS2: Extreme 10x Halftime Spike\n" + "="*60)
    results["S2_ExtremePeak"] = run_scenario(extreme_phases, "S2_ExtremePeak", smf_url)

    # S3: MEC Overload — start all sessions on MEC, watch spillover to CC
    log.info("="*60 + "\nS3: MEC Overload — eMBB Spillover to CC\n" + "="*60)
    mec_overload_phases = {
        1: {"label": "Phase I — MEC Overload",  "mins": 30, "mult": 3.0, "ramp": False},
        2: {"label": "Phase II — Sustained",    "mins": 45, "mult": 5.5, "ramp": False},
        3: {"label": "Phase III — Dispersal",   "mins": 20, "mult": 0.3, "ramp": False},
    }
    # Start with 90% of all sessions at MEC to simulate MEC-first policy
    results["S3_MECOverload"] = run_scenario(
        mec_overload_phases, "S3_MECOverload", smf_url,
        x_init=[[0.9, 0.1], [0.9, 0.1]]
    )

    # S4: CC Overload — start all sessions on CC, watch spillover to MEC
    log.info("="*60 + "\nS4: CC Overload — eMBB Spillover to MEC\n" + "="*60)
    cc_overload_phases = {
        1: {"label": "Phase I — CC Overload",   "mins": 30, "mult": 5.0, "ramp": False},
        2: {"label": "Phase II — Sustained",    "mins": 45, "mult": 5.5, "ramp": False},
        3: {"label": "Phase III — Dispersal",   "mins": 20, "mult": 0.3, "ramp": False},
    }
    # Start with 95% of sessions at CC
    results["S4_CCOverload"] = run_scenario(
        cc_overload_phases, "S4_CCOverload", smf_url,
        x_init=[[0.05, 0.95], [0.05, 0.95]]
    )

    return results


# ── Plotting ──────────────────────────────────────────────────────────────────

def plot_all(results):
    fig = plt.figure(figsize=(22, 24))
    fig.suptitle(
        "Stadium 5G EGT — Multi-Scenario Capacity-Constrained UPF Selection\n"
        r"$M_1=800$ eMBB (SST=1), $M_2=200$ URLLC (SST=2) | "
        r"UPF-MEC cap=100, UPF-CC cap=1000 | "
        r"$k_{mec}/k_{cc}=10$",
        fontsize=13, y=0.98
    )
    gs = gridspec.GridSpec(len(results), 3, figure=fig, hspace=0.55, wspace=0.35)

    colors = {"eMBB@MEC": "#2196F3", "eMBB@CC": "#64B5F6",
              "URLLC@MEC": "#F44336", "URLLC@CC": "#EF9A9A"}

    for row, (name, df) in enumerate(results.items()):
        t = df["global_t"].values

        # Panel 1: Population fractions
        ax1 = fig.add_subplot(gs[row, 0])
        ax1.plot(t, df["x_eMBB_MEC"],  color=colors["eMBB@MEC"],   lw=2, label="eMBB→MEC")
        ax1.plot(t, df["x_eMBB_CC"],   color=colors["eMBB@CC"],    lw=2, ls="--", label="eMBB→CC")
        ax1.plot(t, df["x_URLLC_MEC"], color=colors["URLLC@MEC"],  lw=2, label="URLLC→MEC")
        ax1.plot(t, df["x_URLLC_CC"],  color=colors["URLLC@CC"],   lw=2, ls="--", label="URLLC→CC")
        ax1.set(title=f"{name}\n(a) Population Fractions", ylabel="Fraction", ylim=(0,1))
        ax1.legend(fontsize=7, loc="upper right")
        ax1.grid(alpha=0.3)

        # Panel 2: E2E Delay with PDB lines
        ax2 = fig.add_subplot(gs[row, 1])
        ax2.plot(t, df["d_eMBB_MEC"],  color=colors["eMBB@MEC"],   lw=2, label="eMBB@MEC")
        ax2.plot(t, df["d_eMBB_CC"],   color=colors["eMBB@CC"],    lw=2, ls="--", label="eMBB@CC")
        ax2.plot(t, df["d_URLLC_MEC"], color=colors["URLLC@MEC"],  lw=2, label="URLLC@MEC")
        ax2.plot(t, df["d_URLLC_CC"],  color=colors["URLLC@CC"],   lw=2, ls="--", label="URLLC@CC")
        ax2.axhline(10,  color="red",   ls=":", lw=1.5, alpha=0.8, label="URLLC PDB=10ms")
        ax2.axhline(300, color="blue",  ls=":", lw=1.5, alpha=0.5, label="eMBB PDB=300ms")
        ax2.set(title=f"(b) E2E Delay (ms)", ylabel="Delay (ms)")
        ax2.legend(fontsize=7); ax2.grid(alpha=0.3)

        # Panel 3: Violations + Throughput
        ax3 = fig.add_subplot(gs[row, 2])
        ax3b = ax3.twinx()
        ax3.fill_between(t, df["vio_eMBB"],  alpha=0.5, color="steelblue", label="eMBB vio")
        ax3.fill_between(t, df["vio_URLLC"], alpha=0.4, color="tomato",    label="URLLC vio")
        ax3b.plot(t, df["mec_mbps"], color="green",  lw=1.5, alpha=0.8, label="MEC Mbps")
        ax3b.plot(t, df["cc_mbps"],  color="purple", lw=1.5, alpha=0.8, ls="--", label="CC Mbps")
        ax3.set(title=f"(c) Violations & Throughput", ylabel="UEs exceeding PDB")
        ax3b.set_ylabel("Throughput (Mbps)", color="gray")
        lines1, lbl1 = ax3.get_legend_handles_labels()
        lines2, lbl2 = ax3b.get_legend_handles_labels()
        ax3.legend(lines1+lines2, lbl1+lbl2, fontsize=7, loc="upper left")
        ax3.grid(alpha=0.3)

    plt.savefig(os.path.join(BASE_DIR, "results/multi_scenario_results.png"), dpi=150, bbox_inches="tight")
    log.info("Saved: results/multi_scenario_results.png")


# ── Summary Report ────────────────────────────────────────────────────────────

def print_summary(results):
    print(f"\n{'='*70}")
    print("MULTI-SCENARIO SIMULATION SUMMARY")
    print(f"{'='*70}")
    for name, df in results.items():
        tot   = len(df)
        clean = len(df[(df["vio_eMBB"]==0) & (df["vio_URLLC"]==0)])
        il    = df["infra_limited"].sum()
        peak_mec = df["mec_mbps"].max()
        peak_cc  = df["cc_mbps"].max()
        avg_embb_mec  = df["x_eMBB_MEC"].mean() * 100
        avg_urllc_mec = df["x_URLLC_MEC"].mean() * 100

        print(f"\n  [{name}]")
        print(f"    QoS compliance:      {clean/tot*100:.1f}% steps violation-free")
        print(f"    Infra-limited steps: {il} ({il/tot*100:.1f}% of phase)")
        print(f"    Avg eMBB @ MEC:      {avg_embb_mec:.1f}%")
        print(f"    Avg URLLC @ MEC:     {avg_urllc_mec:.1f}%")
        print(f"    Peak MEC throughput: {peak_mec:.0f} Mbps")
        print(f"    Peak CC throughput:  {peak_cc:.0f} Mbps")
        print(f"    eMBB violations:     {df['vio_eMBB'].sum():,} UE-steps")
        print(f"    URLLC violations:    {df['vio_URLLC'].sum():,} UE-steps")

    print(f"\n{'='*70}")

    # Save combined JSON
    combined = pd.concat(list(results.values()))
    combined.to_json(os.path.join(BASE_DIR, "results/multi_scenario_results.json"), orient="records", indent=2)
    log.info("Saved: results/multi_scenario_results.json")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--smf", default=None)
    args = ap.parse_args()

    results = run_all(smf_url=args.smf)
    plot_all(results)
    print_summary(results)
