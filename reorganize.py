import os
import shutil
import subprocess

def run(cmd):
    print("Running:", cmd)
    subprocess.run(cmd, shell=True)

# Create directories
dirs = ['src/python', 'src/go', 'scripts', 'docs', 'paper', 'config']
for d in dirs:
    os.makedirs(d, exist_ok=True)

# Define file destinations
# Tracked files (use git mv)
tracked_moves = {
    'egt_controller.py': 'src/python/',
    'multi_scenario_sim.py': 'src/python/',
    'stadium_simulation.py': 'src/python/',
    
    'pass5_analysis.py': 'scripts/',
    'pass6_analysis.py': 'scripts/',
    'verify_answers.py': 'scripts/',
    'verify_paper.py': 'scripts/',
    'verify_status.py': 'scripts/',
    
    'Discrepency_file.md': 'docs/',
    'limitations.md': 'docs/',
    'modification-peer-review.md': 'docs/',
    'parameter_details.md': 'docs/',
    'pass5-peer-review-response.md': 'docs/',
    'pass6-peer-review-response.md': 'docs/',
    'pass7-peer-review-response.md': 'docs/',
    'UpfSelectionAjay-3.pdf': 'docs/',
    
    'stadium_paper_final.tex': 'paper/',
    'stadium_paper_revised.tex': 'paper/'
}

# Untracked files (use shutil.move)
untracked_moves = {
    'example.go': 'src/go/',
    'nas.go': 'src/go/',
    'ngap.go': 'src/go/',
    
    'check_a_param.py': 'scripts/',
    'extract_pdf.py': 'scripts/',
    'pass7_analysis.py': 'scripts/',
    
    'alevizaki_ref.pdf': 'docs/',
    
    'scenarios_diagram.png': 'paper/',
    'traffic_timeline.png': 'paper/',
    
    'gnbsim.json': 'config/',
    'gnbsim_100.json': 'config/',
    'gnbsim_1000.json': 'config/',
    'upf_cc.yaml': 'config/',
    'upf_mec.yaml': 'config/',
    'provision_100.sql': 'config/',
    'provision_1000.sql': 'config/',
    
    'multi_scenario_1000ue.json': 'results/',
    'multi_scenario_1000ue.png': 'results/',
    'multi_scenario_100ue.json': 'results/',
    'multi_scenario_100ue.png': 'results/',
    'multi_scenario_results.json': 'results/',
    'multi_scenario_results.png': 'results/'
}

for src, dst in tracked_moves.items():
    if os.path.exists(src):
        run(f"git mv {src} {dst}")

for src, dst in untracked_moves.items():
    if os.path.exists(src):
        # some results might already be in results/, so check if src == dst
        if not src.startswith(dst):
            target = os.path.join(dst, os.path.basename(src))
            if not os.path.exists(target):
                shutil.move(src, dst)

print("Reorganization complete.")
