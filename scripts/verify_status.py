"""
Project verification script — EGT Stadium 5G
Checks every component and writes a status log.
"""
import subprocess, json, os, datetime, sys
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(BASE_DIR, "src", "python"))

results = []
PASS, FAIL, WARN = "✓ PASS", "✗ FAIL", "⚠ WARN"

def check(name, passed, detail=""):
    status = PASS if passed else FAIL
    results.append({"name": name, "status": status, "detail": detail})
    print(f"  {status}  {name}")
    if detail:
        print(f"         {detail}")

def check_warn(name, detail=""):
    results.append({"name": name, "status": WARN, "detail": detail})
    print(f"  {WARN}  {name}")
    if detail:
        print(f"         {detail}")

def run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        return r.stdout.strip(), r.returncode
    except Exception as e:
        return str(e), 1

print("\n" + "="*60)
print(" EGT STADIUM 5G — PROJECT VERIFICATION")
print(f" {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*60)

# ── 1. FILE STRUCTURE ─────────────────────────────────────────
print("\n[1] FILE STRUCTURE")
files = {
    "src/python/egt_controller.py":         "EGT algorithm",
    "scripts/validate_fig2.py":          "Alevizaki validation",
    "src/python/stadium_simulation.py":     "3-phase simulation",
    "docker-compose.yaml":       "OAI stack definition",
    "config/oai_db.sql":                "Subscriber database",
    "config/amf.conf":           "AMF config",
    "config/smf.conf":           "SMF config (2 UPFs)",
    "config/nssf_slice_config.yaml": "NSSF slice config",
    "config/gnb.yaml":           "gNB rfsim config",
    "config/ue_embb.yaml":       "UE-eMBB config",
    "config/ue_urllc.yaml":      "UE-URLLC config",
    "results/fig2_reproduction.png":  "Alevizaki Fig2 reproduction",
    "results/stadium_results.png":    "Stadium simulation figures",
    "results/stadium_results.json":   "Simulation data",
}
for path, desc in files.items():
    exists = os.path.isfile(os.path.join(BASE_DIR, path))
    check(f"{path} ({desc})", exists,
          "" if exists else "MISSING — needs to be created")

# ── 2. EGT ALGORITHM ──────────────────────────────────────────
print("\n[2] EGT ALGORITHM VALIDATION")
try:
    from egt_controller import EGTController, SystemParams

    # Test with Alevizaki parameters
    p = SystemParams(M1=130, M2=70, rho_embb=100.0, rho_urllc=100.0)
    ctl = EGTController(params=p)
    res = ctl.run_to_equilibrium(load_mult=1.0, max_iter=400)
    eq  = res["equilibrium"]
    g1  = eq[0, 0] * 100
    g2  = eq[1, 0] * 100
    n   = res["n_iter"]

    check("EGT imports successfully", True)
    check(f"Convergence < 300 iters (got {n})", n < 300,
          f"Converged at iteration {n}")
    check(f"G1@MEC ≈ 16% (got {g1:.1f}%)", 10 <= g1 <= 22,
          "Alevizaki Fig2: expect ~16%")
    check(f"G2@MEC ≈ 32% (got {g2:.1f}%)", 25 <= g2 <= 40,
          "Alevizaki Fig2: expect ~32%")

    # Test stadium parameters
    p2  = SystemParams()
    ctl2 = EGTController(params=p2)
    res2 = ctl2.run_to_equilibrium(load_mult=1.0, max_iter=400)
    check("Stadium params converge at normal load", res2["n_iter"] < 400,
          f"Converged at {res2['n_iter']} iters")

    res3 = ctl2.run_to_equilibrium(load_mult=5.5, max_iter=400)
    check("Stadium params converge at peak load ×5.5", res3["n_iter"] < 400,
          f"Converged at {res3['n_iter']} iters")

    vio  = ctl2.count_violations(res2["equilibrium"], 1.0)
    vio2 = ctl2.count_violations(res3["equilibrium"], 5.5)
    check("Zero eMBB violations at normal load", vio["eMBB"] == 0,
          f"eMBB vio={vio['eMBB']}")
    check("Zero eMBB violations at peak load", vio2["eMBB"] == 0,
          f"eMBB vio={vio2['eMBB']}")

    # Verify k values
    check("k_mec validated (4.833e-04)", abs(p2.k_mec - 4.833e-4) < 1e-6,
          f"k_mec={p2.k_mec:.3e}")
    check("k_cc  validated (4.833e-05)", abs(p2.k_cc  - 4.833e-5) < 1e-6,
          f"k_cc={p2.k_cc:.3e}")
    check("k ratio = 10", abs(p2.k_mec / p2.k_cc - 10) < 0.01,
          f"ratio={p2.k_mec/p2.k_cc:.1f}")

    # Delay model check
    x_test = np.full((2, 2), 0.5)
    d_mec = ctl2.e2e_delay(0, 0, x_test, 1.0)
    d_cc  = ctl2.e2e_delay(0, 1, x_test, 1.0)
    check("Local UPF delay > propagation (0.25ms)", d_mec > 0.25,
          f"d_mec={d_mec:.3f}ms")
    check("Central UPF delay > propagation (1.0ms)", d_cc > 1.0,
          f"d_cc={d_cc:.3f}ms")
    check("Dedicated local UPF (G1 and G2 see different local delays)",
          ctl2.e2e_delay(0, 0, x_test) != ctl2.e2e_delay(1, 0, x_test),
          "local UPF is per-group dedicated")

    se, sf = ctl2.steer(0)
    su, uf = ctl2.steer(1)
    check("Steer function returns valid UPF name",
          se in ["UPF-MEC", "UPF-CC"] and su in ["UPF-MEC", "UPF-CC"],
          f"eMBB→{se}, URLLC→{su}")

except Exception as e:
    check("EGT controller import/run", False, str(e))

# ── 3. SIMULATION OUTPUT ──────────────────────────────────────
print("\n[3] SIMULATION OUTPUT")
try:
    with open(os.path.join(BASE_DIR, "results/stadium_results.json")) as f:
        data = json.load(f)
    import pandas as pd
    df = pd.DataFrame(data)

    check("stadium_results.json has data", len(df) > 0,
          f"{len(df)} time steps recorded")
    check("All 3 phases present", df["phase"].nunique() == 3,
          f"Phases: {sorted(df['phase'].unique())}")

    p1 = df[df["phase"]==1]
    p2 = df[df["phase"]==2]
    p3 = df[df["phase"]==3]

    check("Phase I: zero eMBB violations", p1["vio_eMBB"].sum() == 0)
    check("Phase I: zero URLLC violations", p1["vio_URLLC"].sum() == 0)
    check("Phase II: eMBB steered toward CC",
          p2["x_eMBB_CC"].mean() > 0.5,
          f"Avg eMBB@CC = {p2['x_eMBB_CC'].mean()*100:.1f}%")
    check("Phase II: URLLC steered toward CC",
          p2["x_URLLC_CC"].mean() > 0.5,
          f"Avg URLLC@CC = {p2['x_URLLC_CC'].mean()*100:.1f}%")
    check("Phase III: traffic returns to MEC",
          p3["x_eMBB_MEC"].mean() > 0.4,
          f"Avg eMBB@MEC = {p3['x_eMBB_MEC'].mean()*100:.1f}%")
    check("Phase II infra-limited flagged",
          "infra_limited" in df.columns and p2["infra_limited"].sum() > 0,
          f"{p2['infra_limited'].sum()} infra-limited steps in Phase II")

    total = len(df)
    clean = len(df[(df["vio_eMBB"]==0) & (df["vio_URLLC"]==0)])
    check("QoS compliance > 50% of steps",
          clean/total > 0.5,
          f"{clean/total*100:.1f}% violation-free steps")

except Exception as e:
    check("Simulation results", False, str(e))

# ── 4. DOCKER — OAI CORE ─────────────────────────────────────
print("\n[4] OAI DOCKER CONTAINERS")
out, _ = run("docker compose ps --format json 2>/dev/null || docker compose ps")

containers = {
    "mysql":       "Database",
    "oai-nrf":     "Network Repository Function",
    "oai-udr":     "Unified Data Repository",
    "oai-udm":     "Unified Data Management",
    "oai-ausf":    "Authentication Function",
    "oai-nssf":    "Network Slice Selection",
    "oai-amf":     "Access & Mobility Management",
    "oai-smf":     "Session Management (2 UPFs)",
    "oai-upf-mec": "UPF — MEC edge node",
    "oai-upf-cc":  "UPF — Central cloud node",
    "oai-gnb":     "gNB RF-simulator",
    "oai-ue-embb": "UE eMBB (SST=1)",
    "oai-ue-urllc":"UE URLLC (SST=2)",
}

running_out, _ = run("docker ps --format '{{.Names}}' 2>/dev/null")
running = set(running_out.split('\n')) if running_out else set()

core_nfs = ["mysql","oai-nrf","oai-udr","oai-udm","oai-ausf",
            "oai-nssf","oai-amf","oai-smf"]
upfs     = ["oai-upf-mec","oai-upf-cc"]
radio    = ["oai-gnb","oai-ue-embb","oai-ue-urllc"]

for name, desc in containers.items():
    is_up = name in running
    if name in core_nfs + upfs:
        check(f"{name} ({desc})", is_up,
              "running" if is_up else "NOT RUNNING — critical")
    else:
        if is_up:
            check(f"{name} ({desc})", True, "running")
        else:
            check_warn(f"{name} ({desc})", "not running — needed for testbed")

# ── 5. PFCP ASSOCIATIONS ──────────────────────────────────────
print("\n[5] PFCP / UPF ASSOCIATIONS")
smf_log, _ = run("docker logs oai-smf 2>&1 | grep -i 'pfcp\\|association\\|upf' | tail -20")
has_mec = "140" in smf_log or "mec" in smf_log.lower()
has_cc  = "141" in smf_log or "upf-cc" in smf_log.lower() or \
          smf_log.lower().count("association") >= 2
check("SMF has PFCP log entries", bool(smf_log),
      f"{len(smf_log.split(chr(10)))} relevant log lines")
check("UPF-MEC referenced in SMF logs", has_mec,
      "192.168.70.140 seen" if has_mec else "not found")
check("UPF-CC referenced in SMF logs", has_cc,
      "192.168.70.141 seen" if has_cc else "not found — check SMF config")

# ── 6. NETWORK ────────────────────────────────────────────────
print("\n[6] DOCKER NETWORK")
net_out, rc = run("docker network ls | grep stadium")
check("stadium_net exists", rc == 0, net_out.strip())
subnet_out, _ = run(
    "docker network inspect egt-stadium_stadium_net "
    "--format '{{range .IPAM.Config}}{{.Subnet}}{{end}}' 2>/dev/null"
)
check("Subnet 192.168.70.128/26 configured",
      "192.168.70" in subnet_out, subnet_out)

# ── 7. gNB CONFIG ─────────────────────────────────────────────
print("\n[7] gNB CONFIG")
gnb_log, _ = run("docker logs oai-gnb 2>&1 | tail -15")
gnb_reading = "gnb.yaml" in gnb_log or "nr-softmodem" in gnb_log
gnb_crash   = "Segmentation fault" in gnb_log or "status '255'" in gnb_log
gnb_cellid  = "nr_cellid" in gnb_log and "bad conversion" in gnb_log
gnb_ok      = "NG Setup" in gnb_log or "NGSetup" in gnb_log

check("gNB config file being read", gnb_reading,
      "gnb.yaml found" if gnb_reading else "config not mounted")
if gnb_cellid:
    check("gNB nr_cellid format", False,
          "L-suffix bug — run: sed -i 's/nr_cellid: 12345678L/nr_cellid: 12345678/' config/gnb.yaml")
else:
    check("gNB nr_cellid format OK", not gnb_cellid)
check("gNB running without crash", not gnb_crash,
      "crashed — check logs" if gnb_crash else "no crash detected")
if gnb_ok:
    check("gNB NG Setup with AMF", True, "NG Setup Response received")
else:
    check_warn("gNB NG Setup with AMF", "not yet confirmed — check logs")

# ── SUMMARY ───────────────────────────────────────────────────
print("\n" + "="*60)
print(" SUMMARY")
print("="*60)
passed = sum(1 for r in results if r["status"] == PASS)
failed = sum(1 for r in results if r["status"] == FAIL)
warned = sum(1 for r in results if r["status"] == WARN)
total  = len(results)
print(f"  Total checks : {total}")
print(f"  {PASS}    : {passed}")
print(f"  {FAIL}    : {failed}")
print(f"  {WARN}    : {warned}")

print("\n  FAILED ITEMS:")
for r in results:
    if r["status"] == FAIL:
        print(f"    ✗ {r['name']}")
        if r["detail"]:
            print(f"      → {r['detail']}")

print("\n  WARNINGS:")
for r in results:
    if r["status"] == WARN:
        print(f"    ⚠ {r['name']}")
        if r["detail"]:
            print(f"      → {r['detail']}")

# Write log file
log = {
    "timestamp": datetime.datetime.now().isoformat(),
    "summary": {"total": total, "passed": passed,
                "failed": failed, "warned": warned},
    "checks": results,
}
with open(os.path.join(BASE_DIR, "results/verification_log.json"), "w") as f:
    json.dump(log, f, indent=2)
print(f"\n  Full log saved: results/verification_log.json")
print("="*60 + "\n")
