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
                        "title": data['keyword'],
                        "subtitle": f"Search {search_dir.title()} for {{query}}... → {url_template}",
                        "arg": url_template,
                        "variables": {
                            "keyword": data['keyword'],
                            "display_text": f"Search {search_dir.title()}",
                            "url": url_template
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
        
        # Get custom searches
        web_searches = read_plist_file(web_searches_path)
        if web_searches:
            custom_sites = web_searches.get('customSites', {})
            
            for site_id, site_data in custom_sites.items():
                if not site_data.get('enabled', True):
                    continue
                    
                items.append({
                    "title": site_data.get('keyword', ''),
                    "subtitle": f"{site_data.get('text', '')} → {site_data.get('url', '')}",
                    "arg": site_data.get('url', ''),
                    "variables": {
                        "keyword": site_data.get('keyword', ''),
                        "display_text": site_data.get('text', ''),
                        "url": site_data.get('url', '')
                    }
                })
        
        return {"items": items}
        
    except Exception as e:
        return {
            "items": [{
                "title": "Error reading web searches",
                "subtitle": str(e),
                "valid": False
            }]
        }

if __name__ == "__main__":
    # Get query from Alfred
    query = sys.argv[1] if len(sys.argv) > 1 else ""
    
    # Get and filter results
    results = get_web_searches()
    
    if query:
        filtered_items = []
        query = query.lower()
        for item in results["items"]:
            if (query in item["title"].lower() or 
                query in item["subtitle"].lower()):
                filtered_items.append(item)
        results["items"] = filtered_items
    
    # Output results to Alfred
    print(json.dumps(results)) 