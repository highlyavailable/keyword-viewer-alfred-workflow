import os

def get_shell_aliases():
    """Get aliases from shell configuration files."""
    alias_searches = []
    shell_files = [
        os.path.expanduser('~/.zshrc'),
        os.path.expanduser('~/.bashrc'),
        os.path.expanduser('~/.bash_aliases'),
        os.path.expanduser('~/.aliases'),
        os.path.expanduser('~/.zsh_aliases')
    ]
    
    for shell_file in shell_files:
        if not os.path.exists(shell_file):
            continue
            
        try:
            with open(shell_file, 'r') as f:
                lines = f.readlines()
                
            for line in lines:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                    
                # Look for alias definitions
                if line.startswith('alias '):
                    # Remove 'alias ' prefix
                    alias_def = line[6:].strip()
                    if '=' in alias_def:
                        name, command = alias_def.split('=', 1)
                        name = name.strip()
                        # Remove surrounding quotes if present
                        command = command.strip().strip("'").strip('"')
                        
                        # Create searchable text
                        searchable_text = f"{name} {command}".lower()
                        
                        alias_searches.append({
                            "title": f"Alias: {name}",
                            "subtitle": f"[Shell Alias] {command}",
                            "arg": name,
                            "variables": {
                                "keyword": name,
                                "display_text": command,
                                "type": "alias",
                                "searchable_text": searchable_text,
                                "source_file": shell_file
                            }
                        })
        except Exception as e:
            print(f"Error reading {shell_file}: {str(e)}", file=sys.stderr)
    
    return alias_searches 