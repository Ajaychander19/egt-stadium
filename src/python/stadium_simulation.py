"""
Stadium 3-phase simulation with PDB-aware EGT steering.
"""
import json, logging
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from egt_controller import EGTController, SystemParams
import os
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))


logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [SIM] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("sim")

PHASES = {
    1: {"label": "Phase I — Ramp-up",    "mins": 30, "mult": 1.0, "ramp": True},
    2: {"label": "Phase II — Peak",       "mins": 45, "mult": 5.5, "ramp": False},
    3: {"label": "Phase III — Dispersal", "mins": 20, "mult": 0.3, "ramp": False},
}
STEPS_PER_MIN = 3

def run(smf_url=None):
    p   = SystemParams()
    ctl = EGTController(params=p, smf_base_url=smf_url)
    records, global_t = [], 0
    prev_mult = 0.01

    for ph, cfg in PHASES.items():
        n = cfg["mins"] * STEPS_PER_MIN
        log.info(f"\n{'='*50}\n{cfg['label']} | {n} steps\n{'='*50}")

        for t in range(n):
            if cfg["ramp"]:
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
            infra_limited = (d_urllc_mec > p.PDB_urllc and
                             d_urllc_cc  > p.PDB_urllc)

            st = ctl.status(mult)
            se, _ = ctl.steer(0)
            su, _ = ctl.steer(1)

            records.append({
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
            })
            global_t += 1
            prev_mult = mult

            if t % (STEPS_PER_MIN * 5) == 0:
                flag = " [INFRA-LIMITED]" if infra_limited else ""
                log.info(f"  t={t:3d} x{mult:.2f} | "
                         f"eMBB->{se} URLLC->{su} | vio={vio}{flag}")

    df = pd.DataFrame(records)
    df.to_json(os.path.join(BASE_DIR, "results/stadium_results.json"), orient="records", indent=2)
    log.info("Saved: results/stadium_results.json")
    return df


def plot(df):
    t = df["global_t"].values
    bounds = [df[df["phase"]==p]["global_t"].max() for p in [1, 2]]

    def vlines(ax):
        for b in bounds:
            ax.axvline(b, color="gray", ls=":", lw=0.8, alpha=0.5)

    def phase_labels(ax, frac=0.93):
        ylo, yhi = ax.get_ylim()
        y = ylo + (yhi - ylo) * frac
        pts = [0] + bounds + [t[-1]]
        for i, lbl in enumerate(["I", "II", "III"]):
            ax.text((pts[i]+pts[i+1])/2, y, f"Ph.{lbl}",
                    ha="center", fontsize=9, color="gray", style="italic")

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(
        "Stadium 5G EGT UPF Steering — 3-Phase Simulation\n"
        r"$M_1=800$ eMBB (SST=1), $M_2=200$ URLLC (SST=2), "
        r"halftime spike $\times5.5$",
        fontsize=12
    )

    ax = axes[0, 0]
    ax.plot(t, df["x_eMBB_MEC"],  "b-",  lw=2, label="eMBB -> UPF-MEC")
    ax.plot(t, df["x_eMBB_CC"],   "b--", lw=2, label="eMBB -> UPF-CC")
    ax.plot(t, df["x_URLLC_MEC"], "r-",  lw=2, label="URLLC -> UPF-MEC")
    ax.plot(t, df["x_URLLC_CC"],  "r--", lw=2, label="URLLC -> UPF-CC")
    vlines(ax)
    ax.set(title=r"(a) Population fractions $x^g_i(t)$",
           ylabel="Fraction of sessions", xlabel="Time step", ylim=(0, 1))
    ax.legend(fontsize=8, loc="center right")
    ax.grid(alpha=0.3); phase_labels(ax)

    ax = axes[0, 1]
    ax.plot(t, df["d_eMBB_MEC"],  "b-",  lw=2, label="eMBB @ MEC")
    ax.plot(t, df["d_eMBB_CC"],   "b--", lw=2, label="eMBB @ CC")
    ax.plot(t, df["d_URLLC_MEC"], "r-",  lw=2, label="URLLC @ MEC")
    ax.plot(t, df["d_URLLC_CC"],  "r--", lw=2, label="URLLC @ CC")
    ax.axhline(10,  color="r", ls=":", lw=1.5, alpha=0.8, label="URLLC PDB (10 ms)")
    ax.axhline(300, color="b", ls=":", lw=1.5, alpha=0.5, label="eMBB PDB (300 ms)")
    vlines(ax)
    ax.set(title="(b) End-to-end delay per slice and UPF",
           ylabel="Delay (ms)", xlabel="Time step")
    ax.legend(fontsize=7); ax.grid(alpha=0.3); phase_labels(ax)

    ax = axes[1, 0]
    il = df["infra_limited"].values
    ax.fill_between(t, df["vio_eMBB"],  alpha=0.6, color="steelblue",
                    label="eMBB violations")
    ax.fill_between(t, df["vio_URLLC"], alpha=0.4, color="tomato",
                    label="URLLC violations")
    if il.any():
        ax.fill_between(t, 0, df["vio_URLLC"],
                        where=il.astype(bool), alpha=0.3, color="orange",
                        hatch="///",
                        label="Infrastructure-limited\n(both UPFs exceed PDB)")
    vlines(ax)
    ax.set(title="(c) UEs exceeding PDB (QoS violations)",
           ylabel="Number of UEs", xlabel="Time step")
    ax.legend(fontsize=8); ax.grid(alpha=0.3); phase_labels(ax)

    ax  = axes[1, 1]
    ax2 = ax.twinx()
    l1, = ax.plot(t,  df["load_mult"],   "k-",      lw=2,
                  label="Load multiplier")
    l2, = ax2.plot(t, df["n_iter_conv"], color="purple", lw=1.5,
                   alpha=0.8, label="Iterations to converge")
    vlines(ax)
    ax.set(title="(d) Load profile vs EGT convergence speed",
           xlabel="Time step", ylabel="Load multiplier")
    ax2.set_ylabel("Iterations to converge", color="purple")
    ax2.tick_params(axis="y", colors="purple")
    ax.legend(handles=[l1, l2], fontsize=8, loc="upper left")
    ax.grid(alpha=0.3); phase_labels(ax)

    plt.tight_layout()
    plt.savefig(os.path.join(BASE_DIR, "results/stadium_results.png"), dpi=150, bbox_inches="tight")
    log.info("Saved: results/stadium_results.png")

    print(f"\n{'='*55}\nSIMULATION SUMMARY\n{'='*55}")
    for ph, cfg in PHASES.items():
        sub = df[df["phase"] == ph]
        il_steps = sub["infra_limited"].sum()
        print(f"\n  {cfg['label']}:")
        print(f"    Avg eMBB@MEC:    {sub['x_eMBB_MEC'].mean()*100:.1f}%")
        print(f"    Avg URLLC@MEC:   {sub['x_URLLC_MEC'].mean()*100:.1f}%")
        print(f"    eMBB violations: {sub['vio_eMBB'].sum():,} UE-steps")
        print(f"    URLLC vio:       {sub['vio_URLLC'].sum():,} UE-steps")
        print(f"    Infra-limited:   {il_steps} steps ({il_steps/len(sub)*100:.0f}% of phase)")
        print(f"    Avg conv iters:  {sub['n_iter_conv'].mean():.1f}")
    tot   = len(df)
    clean = len(df[(df["vio_eMBB"]==0) & (df["vio_URLLC"]==0)])
    il_total = df["infra_limited"].sum()
    print(f"\n  QoS compliance: {clean/tot*100:.1f}% of steps violation-free")
    print(f"  Infra-limited:  {il_total} steps ({il_total/tot*100:.1f}%)")
    print(f"{'='*55}")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--smf", default=None)
    args = ap.parse_args()
    df = run(smf_url=args.smf)
    plot(df)
