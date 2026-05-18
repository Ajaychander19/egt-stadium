import os

def fix_base(path):
    if not os.path.exists(path):
        return
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    # Replace BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) 
    # with BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    # (If it's a src/python or scripts script that needs depth 2)
    # Wait, scripts/ are at depth 1 (e.g. scripts/verify_paper.py), so `..` is correct for them!
    # Ah, `scripts/verify_paper.py` is at depth 1. `os.path.dirname` -> `scripts`. `..` -> root.
    # But `src/python/multi_scenario_sim.py` is at depth 2. `os.path.dirname` -> `src/python`. `../..` -> root.
    
    if path.startswith('src/python'):
        code = code.replace(
            'BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))',
            'BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))'
        )
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)

fix_base('src/python/multi_scenario_sim.py')
fix_base('src/python/stadium_simulation.py')
print("Fixed bases.")
