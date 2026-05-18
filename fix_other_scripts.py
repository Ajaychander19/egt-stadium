import os

base_py = '''import os
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
'''

def update_file(path, depth=2):
    if not os.path.exists(path):
        return
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    # insert BASE_DIR if not present
    if 'BASE_DIR =' not in code:
        # put it after imports
        imports_end = 0
        lines = code.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                imports_end = i + 1
        
        bd_str = 'import os\nBASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ' + ('".."' if depth==2 else '".."') + '))\n'
        if depth == 1:
            bd_str = 'import os\nBASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))\n'
        
        lines.insert(imports_end, bd_str)
        code = '\n'.join(lines)
    
    # replace "results/" with os.path.join(BASE_DIR, "results/")
    code = code.replace('"results/', 'os.path.join(BASE_DIR, "results/')
    code = code.replace("'results/", "os.path.join(BASE_DIR, 'results/")
    
    # Fix instances where they are now os.path.join(BASE_DIR, "results/xxx") string concatenations
    import re
    # Match os.path.join(BASE_DIR, "results/foo.json") properly
    # Actually, replacing "results/foo" with os.path.join(BASE_DIR, "results/foo")
    # Wait, the replace above makes it: df.to_json(os.path.join(BASE_DIR, "results/stadium_results.json", ...)
    # Wait, it needs to be closed.
    # Ah, the replace `"results/xxx"` -> `os.path.join(BASE_DIR, "results/xxx")`
    # Let's use regex.
    code = re.sub(r'("results/[^"]+")', r'os.path.join(BASE_DIR, \1)', code)
    code = re.sub(r"('results/[^']+')", r"os.path.join(BASE_DIR, \1)", code)
    
    # Let's clean up double joins if we applied it twice
    code = code.replace('os.path.join(BASE_DIR, os.path.join(BASE_DIR,', 'os.path.join(BASE_DIR,')
    code = code.replace('))")', ')")')
    
    # Write back
    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)

update_file('src/python/multi_scenario_sim.py', 2)
update_file('src/python/stadium_simulation.py', 2)
update_file('scripts/verify_paper.py', 2)
update_file('scripts/pass5_analysis.py', 2)
update_file('scripts/pass6_analysis.py', 2)
update_file('scripts/pass7_analysis.py', 2)

print("Updated paths.")
