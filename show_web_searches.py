#!/usr/bin/env python3
import json
import os
import sys
import subprocess
from pathlib import Path

def get_web_searches():
    # Direct path to Alfred's web search preferences
    web_searches_path = os.path.expanduser(
        "~/Library/Application Support/Alfred/Alfred.alfredpreferences/preferences/features/websearch/prefs.plist"
    )
    
    try:
        # Use plutil to convert plist to json
        result = subprocess.run(
            ['plutil', '-convert', 'json', '-o', '-', web_searches_path],
            capture_output=True, 
            text=True
        )
        
        web_searches = json.loads(result.stdout)
        custom_sites = web_searches.get('customSites', {})
        
        # Format the results for Alfred
        items = []
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