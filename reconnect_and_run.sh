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
echo "  STEP 5 — Build and run gnbsim natively"
echo "══════════════════════════════════════"
# Extract the pre-built binary from the Docker image to avoid Docker SCTP issues
docker compose build gnbsim 2>&1 | tail -5
docker create --name gnbsim-extract egt-stadium-gnbsim true 2>/dev/null || true
docker cp gnbsim-extract:/gnbsim/bin/gnbsim /tmp/gnbsim-bin 2>/dev/null || \
  docker cp gnbsim-extract:/gnbsim/bin/gnbsim-bin /tmp/gnbsim-bin 2>/dev/null || true
docker rm gnbsim-extract 2>/dev/null || true

# Copy config to /tmp so binary finds it in CWD
cp ~/egt-stadium/config/gnbsim.json /tmp/gnbsim.json
chmod +x /tmp/gnbsim-bin

echo "  Testing network path to AMF (.132)..."
ping -c 3 192.168.70.132 || echo "  [WARNING] AMF unreachable from host"

echo "  Starting gnbsim natively and monitoring (timeout 30s)..."
cd /tmp && timeout 30 /tmp/gnbsim-bin 2>&1 | tee /tmp/gnbsim.log &
GNBSIM_PID=$!
sleep 30
wait $GNBSIM_PID 2>/dev/null || true
cd ~/egt-stadium

echo ""
echo "══════════════════════════════════════"
echo "  STEP 6 — Check results"
echo "══════════════════════════════════════"
echo "--- gnbsim logs (raw) ---"
cat /tmp/gnbsim.log 2>/dev/null || echo "  (no log file found)"

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
