import os
import re

vs_path = r'C:\Users\Sini T P\.gemini\antigravity\scratch\egt_stadium_files\scripts\verify_status.py'
with open(vs_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add BASE_DIR calculation at the top after imports
code = code.replace(
    'import subprocess, json, os, datetime\nimport numpy as np',
    'import subprocess, json, os, datetime, sys\nimport numpy as np\n'
    'BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))\n'
    'sys.path.insert(0, os.path.join(BASE_DIR, "src", "python"))'
)

# 2. Update the files dictionary keys to point to correct relative paths (they will be checked relative to BASE_DIR)
code = code.replace('"egt_controller.py":', '"src/python/egt_controller.py":')
code = code.replace('"validate_fig2.py":', '"scripts/validate_fig2.py":')
code = code.replace('"stadium_simulation.py":', '"src/python/stadium_simulation.py":')
code = code.replace('"oai_db.sql":', '"config/oai_db.sql":')

# 3. Use BASE_DIR for file existence check
code = code.replace(
    'exists = os.path.isfile(path)',
    'exists = os.path.isfile(os.path.join(BASE_DIR, path))'
)

# 4. Use BASE_DIR for json loading
code = code.replace(
    'with open("results/stadium_results.json") as f:',
    'with open(os.path.join(BASE_DIR, "results/stadium_results.json")) as f:'
)

# 5. Use BASE_DIR for json saving
code = code.replace(
    'with open("results/verification_log.json", "w") as f:',
    'with open(os.path.join(BASE_DIR, "results/verification_log.json"), "w") as f:'
)

with open(vs_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated verify_status.py")
