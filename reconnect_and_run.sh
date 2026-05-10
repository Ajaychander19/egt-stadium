#!/usr/bin/env bash
# ============================================================
# EGT-Stadium reconnect script
# Run this after ssh ajay@luxray.srcd.imta.fr
# ============================================================
set -euo pipefail
cd ~/egt-stadium
source venv/bin/activate 2>/dev/null || true

echo ""
echo "══════════════════════════════════════"
echo "  STEP 1 — Check core network status"
echo "══════════════════════════════════════"
docker compose ps

echo ""
echo "══════════════════════════════════════"
echo "  STEP 2 — Verify EGT controller"
echo "══════════════════════════════════════"
python3 -c "
from egt_controller import SystemParams
p = SystemParams()
print(f'  k_mec={p.k_mec:.3e}  k_cc={p.k_cc:.3e}  ratio={p.k_mec/p.k_cc:.0f}x  ✓')
"

echo ""
echo "══════════════════════════════════════"
echo "  STEP 3 — Pull gnbsim image"
echo "══════════════════════════════════════"
docker pull rohankharade/gnbsim:latest 2>&1 | tail -3

echo ""
echo "══════════════════════════════════════"
echo "  STEP 4 — Sync updated files from git"
echo "══════════════════════════════════════"
git pull origin main 2>&1 || git pull origin master 2>&1 || echo "  (no remote changes to pull)"

echo ""
echo "══════════════════════════════════════"
echo "  STEP 5 — Start gnbsim"
echo "══════════════════════════════════════"
docker compose up -d --build gnbsim
echo "  Checking container status..."
docker inspect gnbsim --format '{{.State.Status}}'

echo "  Testing network path to AMF (.132)..."
docker exec gnbsim ping -c 3 192.168.70.132 || echo "  [WARNING] AMF unreachable from gnbsim container"

echo "  Monitoring UE registration (timeout 45s)..."
for i in {1..45}; do
    STATUS=$(docker inspect gnbsim --format '{{.State.Status}}' 2>/dev/null)
    if [ "$STATUS" != "running" ]; then
        echo "  [ERROR] gnbsim container stopped! Check logs below."
        break
    fi
    # If we see "PDU Session Establishment" or "Registered", we can exit early on success
    if docker logs gnbsim 2>&1 | grep -qE "PDU Session Establishment|Registered"; then
        echo "  [SUCCESS] UE Registered and Session Established!"
        break
    fi
    sleep 1
done

echo ""
echo "══════════════════════════════════════"
echo "  STEP 6 — Check results"
echo "══════════════════════════════════════"
echo "--- gnbsim logs (raw) ---"
docker logs gnbsim --tail 50

echo ""
echo "--- AMF: Registration logs ---"
docker logs oai-amf --tail 100 | grep -iE "registration|imsi|pdu" || echo "  No registration logs found in AMF"

echo ""
echo "--- SMF: PDU sessions ---"
docker logs oai-smf 2>&1 | grep -iE "pdu|session|upf|established|selected|anchor" | tail -10

echo ""
echo "--- UPF-MEC: GTP tunnels ---"
docker logs oai-upf-mec 2>&1 | grep -iE "gtp|pfcp|far|pdr|tunnel|session" | tail -10

echo ""
echo "--- UPF-CC: GTP tunnels ---"
docker logs oai-upf-cc 2>&1 | grep -iE "gtp|pfcp|far|pdr|tunnel|session" | tail -10

echo ""
echo "══════════════════════════════════════"
echo "  STEP 7 — Run stadium simulation"
echo "══════════════════════════════════════"
python3 stadium_simulation.py --smf http://localhost:8080
ls -lh results/

echo ""
echo "══════════════════════════════════════"
echo "  STEP 8 — Health check"
echo "══════════════════════════════════════"
python3 verify_status.py

echo ""
echo "══════════════════════════════════════"
echo "  STEP 9 — Commit final state"
echo "══════════════════════════════════════"
git add -A
git commit -m "feat: gnbsim UE attach + final stadium simulation results"
git push
echo "  Done."
