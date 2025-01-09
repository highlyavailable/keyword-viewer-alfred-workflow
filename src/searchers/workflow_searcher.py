import os
from ..utils.plist_reader import read_plist_file

def get_workflow_searches():
    """Get workflow searches from Alfred preferences."""
    base_path = os.path.expanduser(
        "~/Library/Application Support/Alfred/Alfred.alfredpreferences/workflows"
    )
    workflow_searches = []
    
    # Common Alfred workflow input types
    input_types = [
        'alfred.workflow.input.keyword',
        'alfred.workflow.input.scriptfilter',
        'alfred.workflow.input.filefilter',
        'alfred.workflow.input.argument',
        'alfred.workflow.input.box'
    ]
    
    # Walk through all workflow directories
    for root, dirs, files in os.walk(base_path):
        if 'info.plist' in files:
            plist_path = os.path.join(root, 'info.plist')
            data = read_plist_file(plist_path)
            
            if not data or 'objects' not in data:
                continue
            
            workflow_name = data.get('name', '')
            workflow_desc = data.get('description', '')
            workflow_creator = data.get('createdby', '')
            workflow_website = data.get('webaddress', '')
            
            # Get default values from user configuration
            default_values = {}
            user_config = data.get('userconfigurationconfig', [])
            for config_item in user_config:
                var_name = config_item.get('variable', '')
                if var_name:
                    default_values[var_name] = config_item.get('config', {}).get('default', '')
                
            # Look for keyword inputs
            for obj in data['objects']:
                if obj.get('type') in input_types:
                    config = obj.get('config', {})
                    keyword = config.get('keyword', '')
                    if keyword and isinstance(keyword, str):
                        # If it's a variable reference, get the default value
                        if keyword.startswith('{var:') and keyword.endswith('}'):
                            var_name = keyword[5:-1]  # Strip {var: and }
                            keyword = default_values.get(var_name, var_name)
                    
                    text = config.get('text', '')
                    subtext = config.get('subtext', '')
                    title = config.get('title', '')
                    script = config.get('script', '')
                    
                    if keyword:
                        # Find connected actions
                        uid = obj.get('uid')
                        destinations = []
                        actions = []
                        
                        if uid and 'connections' in data:
                            for dest in data['connections'].get(uid, []):
                                dest_uid = dest.get('destinationuid')
                                if dest_uid:
                                    for dest_obj in data['objects']:
                                        if dest_obj.get('uid') == dest_uid:
                                            dest_type = dest_obj.get('type', '')
                                            dest_config = dest_obj.get('config', {})
                                            
                                            if dest_type == 'alfred.workflow.action.openurl':
                                                url = dest_config.get('url', '')
                                                if url:
                                                    destinations.append(url)
                                            actions.append(dest_type.split('.')[-1])
                        
                        # Build a descriptive subtitle
                        if title and subtext:
                            display_text = f"{title} - {subtext}"
                        else:
                            display_text = text or title or subtext or workflow_desc or "No description"
                        
                        workflow_type = obj.get('type').split('.')[-1]
                        creator_text = f" by {workflow_creator}" if workflow_creator else ""
                        
                        # Create searchable text that includes all relevant fields
                        searchable_text = f"{keyword} {workflow_name} {workflow_desc} {text} {subtext} {title} {workflow_creator}".lower()
                        
                        workflow_searches.append({
                            "title": f"{workflow_name}: {keyword}",
                            "subtitle": f"[Workflow{creator_text}] {display_text}",
                            "arg": keyword,
                            "variables": {
                                "keyword": keyword,
                                "display_text": display_text,
                                "workflow_name": workflow_name,
                                "workflow_desc": workflow_desc,
                                "workflow_creator": workflow_creator,
                                "workflow_website": workflow_website,
                                "workflow_type": workflow_type,
                                "script": script,
                                "url": ','.join(destinations) if destinations else '',
                                "type": "workflow",
                                "searchable_text": searchable_text
                            }
                        })
    
    return workflow_searches 