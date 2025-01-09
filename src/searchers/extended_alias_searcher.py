import os
import subprocess
from pathlib import Path

def get_extended_aliases():
    """Get various types of aliases and shortcuts."""
    alias_searches = []
    
    # Add npm aliases from package.json files
    npm_aliases = get_npm_scripts()
    alias_searches.extend(npm_aliases)
    
    # Add Docker Compose services
    docker_aliases = get_docker_compose_services()
    alias_searches.extend(docker_aliases)
    
    # Add Make targets
    make_aliases = get_makefile_targets()
    alias_searches.extend(make_aliases)
    
    return alias_searches

def get_npm_scripts():
    """Get npm scripts from package.json."""
    results = []
    try:
        if os.path.exists('package.json'):
            with open('package.json') as f:
                data = json.loads(f.read())
                scripts = data.get('scripts', {})
                for name, command in scripts.items():
                    results.append({
                        "title": f"NPM Script: {name}",
                        "subtitle": f"[NPM] {command}",
                        "arg": f"npm run {name}",
                        "variables": {
                            "keyword": name,
                            "display_text": command,
                            "type": "npm_script",
                            "searchable_text": f"{name} {command}".lower()
                        }
                    })
    except Exception:
        pass
    return results

def get_docker_compose_services():
    """Get services from docker-compose.yml."""
    results = []
    compose_files = ['docker-compose.yml', 'docker-compose.yaml']
    
    for file in compose_files:
        if os.path.exists(file):
            try:
                import yaml
                with open(file) as f:
                    data = yaml.safe_load(f)
                    services = data.get('services', {})
                    for name, config in services.items():
                        description = f"Image: {config.get('image', 'custom')} Port: {config.get('ports', [])}"
                        results.append({
                            "title": f"Docker Service: {name}",
                            "subtitle": f"[Docker] {description}",
                            "arg": f"docker-compose up {name}",
                            "variables": {
                                "keyword": name,
                                "display_text": description,
                                "type": "docker_service",
                                "searchable_text": f"{name} {description}".lower()
                            }
                        })
            except Exception:
                continue
    return results

def get_makefile_targets():
    """Get targets from Makefile."""
    results = []
    if os.path.exists('Makefile'):
        try:
            output = subprocess.run(['make', '-qp'], 
                                 capture_output=True, 
                                 text=True).stdout
            targets = []
            for line in output.split('\n'):
                if ':' in line and not line.startswith('\t'):
                    target = line.split(':')[0].strip()
                    if target and not target.startswith('.'):
                        targets.append(target)
            
            for target in targets:
                results.append({
                    "title": f"Make Target: {target}",
                    "subtitle": f"[Make] Run make {target}",
                    "arg": f"make {target}",
                    "variables": {
                        "keyword": target,
                        "display_text": f"Make target: {target}",
                        "type": "make_target",
                        "searchable_text": f"{target}".lower()
                    }
                })
        except Exception:
            pass
    return results 