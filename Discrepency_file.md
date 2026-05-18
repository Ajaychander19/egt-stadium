# Discrepancy Report: Research Paper vs. Repository Contents

A thorough analysis of the draft LaTeX research paper was conducted against the latest contents of the `egt-stadium` GitHub repository. While the majority of the paper accurately reflects the configuration and simulation scripts present in the repository, the following critical discrepancies were identified:

## 1. Missing `gnbsim` Source Code and O(1) Modifications
**Paper Claim:** Section IV states, *"we developed an emulation testbed using OpenAirInterface (OAI) and a modified version of the gnbsim emulator... Supporting 1,000 concurrent PDU sessions required architectural changes to the standard per-UE processing model... re-engineering the emulator's user-plane architecture into a multiplexed engine using shared sharedEncap and sharedDecap loops with $O(1)$ lookup maps---specifically IpToCamper and TeidToCamper..."*

**Repository Reality:** The modified Go source code for `gnbsim` is **completely absent** from the repository. 
- The file `Dockerfile.gnbsim` attempts to build the emulator by running `go build -o /gnbsim-example .` in an `example` directory, but neither the `example` directory nor any Go source files exist in the repository root. 
- Furthermore, the script `reconnect_and_run.sh` pulls a pre-built Docker image (`rohankharade/gnbsim:latest`) rather than building your modified version from source.
**Action Required:** You must commit the modified `gnbsim` Go source code (including the `IpToCamper` and `TeidToCamper` map implementations) to the repository, or at least link to a separate repository/submodule containing it. Without this, reviewers cannot verify the $O(1)$ user-plane enhancements claimed in the paper.

## 2. Missing BLSTM Predictor Prototype
**Paper Claim:** Section III.G states, *"A Bidirectional LSTM (BLSTM) predictor module is prototyped for future integration into the control loop."*

**Repository Reality:** There is no evidence of a BLSTM prototype in the repository codebase. None of the Python scripts (`egt_controller.py`, `multi_scenario_sim.py`, `stadium_simulation.py`, `verify_answers.py`, `verify_paper.py`) import machine learning libraries (such as TensorFlow or PyTorch) or contain any LSTM architecture definitions.
**Action Required:** If this module was prototyped as claimed, the prototype code or a Jupyter notebook demonstrating it should be included in the repository.

## 3. PDU Session Concurrency Configuration Mismatch
**Paper Claim:** The paper mentions 1,000 concurrent PDU sessions via $M_1=800$ and $M_2=200$.
**Repository Reality:** The database dump `provision_1000.sql` (730KB) confirms that 1,000 UEs are indeed provisioned. However, the default `docker-compose.yaml` file mounts `oai_db.sql` (2.3KB), which typically contains far fewer UEs (likely around 10-20 default OAI UEs). 
**Action Required:** Update `docker-compose.yaml` to mount `provision_1000.sql` by default, or explicitly document in the README that reviewers must change the mounted database file to replicate the 1,000 UE testbed scenario.

---
**Conclusion:** The Python simulation models (EGT Replicator Dynamics) and Docker multi-UPF configurations accurately match the paper. However, the critical C/Go-level modifications to the `gnbsim` user-plane architecture are missing from the public codebase and must be added to support the emulation claims made in Section IV.
