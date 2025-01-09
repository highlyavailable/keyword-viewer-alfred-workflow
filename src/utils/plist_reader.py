import json
import subprocess

def read_plist_file(plist_path):
    """Read and convert a plist file to JSON format."""
    try:
        result = subprocess.run(
            ['plutil', '-convert', 'json', '-o', '-', plist_path],
            capture_output=True,
            text=True
        )
        return json.loads(result.stdout)
    except Exception:
        return None 