import os
import re
import shutil

# 1. Move oai_db.sql to config/
if os.path.exists('oai_db.sql'):
    shutil.move('oai_db.sql', 'config/oai_db.sql')

# 2. Update docker-compose.yaml
dc_path = 'docker-compose.yaml'
if os.path.exists(dc_path):
    with open(dc_path, 'r') as f:
        content = f.read()
    content = content.replace('./oai_db.sql:', './config/oai_db.sql:')
    with open(dc_path, 'w') as f:
        f.write(content)

# 3. Fix paths in scripts/verify_status.py
vs_path = 'scripts/verify_status.py'
if os.path.exists(vs_path):
    with open(vs_path, 'r') as f:
        content = f.read()
    
    # Add sys.path
    if 'sys.path.insert(0' not in content:
        content = content.replace('import subprocess, json, os, datetime\nimport numpy as np', 
                                  'import subprocess, json, os, datetime, sys\nimport numpy as np\nsys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/python")))\n')
    
    # Fix dict paths
    content = content.replace('"egt_controller.py":', '"src/python/egt_controller.py":')
    content = content.replace('"validate_fig2.py":', '"scripts/validate_fig2.py":')
    content = content.replace('"stadium_simulation.py":', '"src/python/stadium_simulation.py":')
    content = content.replace('"oai_db.sql":', '"config/oai_db.sql":')
    
    # Ensure any results paths are using project root
    content = content.replace('"results/', 'os.path.join(os.path.dirname(__file__), "../results/") + "')
    content = content.replace("open(\"results/", "open(os.path.join(os.path.dirname(__file__), \"../results/") + "\"")
    content = content.replace("'results/stadium_results.json'", 'os.path.join(os.path.dirname(__file__), "../results/stadium_results.json")')
    
    # We may have messed up string concatenation if we simply replaced '"results/'.
    # Let's be careful. Let's do it via regex or just write a reliable python script fix.
