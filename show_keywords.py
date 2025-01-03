#!/usr/bin/env python3
import json
import os
import sys
import subprocess
from pathlib import Path

def read_plist_file(plist_path):
    try:
        result = subprocess.run(
            ['plutil', '-convert', 'json', '-o', '-', plist_path],
            capture_output=True,
            text=True
        )
        return json.loads(result.stdout)
    except Exception:
        return None

def get_workflow_searches():
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

def get_built_in_searches():
    base_path = os.path.expanduser(
        "~/Library/Application Support/Alfred/Alfred.alfredpreferences/preferences/features/websearch"
    )
    built_in_searches = []
    
    # Known built-in search directories
    search_dirs = ['amazon', 'duckduckgo', 'google', 'youtube']
    
    for search_dir in search_dirs:
        plist_path = os.path.join(base_path, search_dir, 'prefs.plist')
        if os.path.exists(plist_path):
            data = read_plist_file(plist_path)
            if data and 'keyword' in data:
                url_template = {
                    'amazon': 'https://www.amazon.com/s?k={query}',
                    'duckduckgo': 'https://duckduckgo.com/?q={query}',
                    'google': 'https://www.google.com/search?q={query}',
                    'youtube': 'https://www.youtube.com/results?search_query={query}'
                }.get(search_dir)
                
                if url_template:
                    built_in_searches.append({
                        "title": f"{search_dir.title()}: {data['keyword']}",
                        "subtitle": f"[Web Search] Search {search_dir.title()} for {{query}}",
                        "arg": data['keyword'],
                        "variables": {
                            "keyword": data['keyword'],
                            "display_text": f"Search {search_dir.title()}",
                            "url": url_template,
                            "type": "websearch"
                        }
                    })
    
    return built_in_searches

def get_web_searches():
    # Direct path to Alfred's web search preferences
    web_searches_path = os.path.expanduser(
        "~/Library/Application Support/Alfred/Alfred.alfredpreferences/preferences/features/websearch/prefs.plist"
    )
    
    items = []
    
    try:
        # Get built-in searches
        items.extend(get_built_in_searches())
        
        # Get workflow searches
        items.extend(get_workflow_searches())
        
        # Get custom searches
        web_searches = read_plist_file(web_searches_path)
        if web_searches:
            custom_sites = web_searches.get('customSites', {})
            
            for site_id, site_data in custom_sites.items():
                if not site_data.get('enabled', True):
                    continue
                    
                items.append({
                    "title": f"{site_data.get('text', '')}: {site_data.get('keyword', '')}",
                    "subtitle": f"[Web Search] {site_data.get('url', '')}",
                    "arg": site_data.get('keyword', ''),
                    "variables": {
                        "keyword": site_data.get('keyword', ''),
                        "display_text": site_data.get('text', ''),
                        "url": site_data.get('url', ''),
                        "type": "websearch"
                    }
                })
        
        return {"items": items}
        
    except Exception as e:
        return {
            "items": [{
                "title": "Error reading searches",
                "subtitle": str(e),
                "valid": False
            }]
        }

if __name__ == "__main__":
    # Get query from Alfred
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    # Debug logging
    debug_log_path = os.path.expanduser('~/Desktop/alfred_debug.log')
    with open(debug_log_path, 'a') as f:
        f.write(f"\nReceived args: {sys.argv}\n")
        f.write(f"Args: {args}\n")
    
    # Get and filter results
    results = get_web_searches()
    
    if args:
        filtered_items = []
        first_arg = args[0].lower()
        
        # Check for type filter as first word
        filter_type = None
        search_query = ""
        
        if first_arg == "_web":
            filter_type = "websearch"
            search_query = " ".join(args[1:]).lower() if len(args) > 1 else ""
        elif first_arg == "_work":
            filter_type = "workflow"
            search_query = " ".join(args[1:]).lower() if len(args) > 1 else ""
        elif first_arg == "web":
            filter_type = "websearch"
            search_query = " ".join(args[1:]).lower() if len(args) > 1 else ""
        elif first_arg == "wf":
            filter_type = "workflow"
            search_query = " ".join(args[1:]).lower() if len(args) > 1 else ""
        else:
            search_query = " ".join(args).lower()
        
        for item in results["items"]:
            # Apply type filter if specified
            if filter_type and item["variables"]["type"] != filter_type:
                continue
            
            # If there's no search query after the filter, include all items of that type
            if not search_query:
                filtered_items.append(item)
                continue
                
            # For web searches, look for the search term in all relevant fields
            if item["variables"]["type"] == "websearch":
                searchable_text = f"{item['title']} {item['subtitle']} {item['variables']['keyword']} {item['variables']['display_text']}".lower()
                if search_query in searchable_text:
                    filtered_items.append(item)
            # For workflows, use the existing searchable_text field
            elif item["variables"]["type"] == "workflow":
                if (search_query in item["variables"].get("searchable_text", "") or
                    search_query in item["title"].lower() or 
                    search_query in item["subtitle"].lower()):
                    filtered_items.append(item)
        
        results["items"] = filtered_items
    
    # Output results to Alfred
    print(json.dumps(results)) 