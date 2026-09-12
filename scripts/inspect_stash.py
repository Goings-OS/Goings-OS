import subprocess
import sys

out = subprocess.check_output('git stash show -p "stash@{0}"', shell=True).decode('utf-8', errors='ignore')
for block in out.split('diff --git '):
    if 'middleware/model_armor.py' in block or 'ingress_gateway.py' in block:
        sys.stdout.buffer.write(b'=== FOUND BLOCK ===\n')
        sys.stdout.buffer.write(block[:600].encode('utf-8', errors='ignore'))
        sys.stdout.buffer.write(b'\n')

