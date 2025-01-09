#!/usr/bin/env python3

import json
import os
import sys

from src.searchers.web_searcher import get_built_in_searches, get_custom_web_searches
from src.searchers.workflow_searcher import get_workflow_searches
from src.searchers.alias_searcher import get_shell_aliases

def get_all_searches():
    """Get all searches from all sources."""
    items = []
    
    try:
        # Get built-in searches
        items.extend(get_built_in_searches())
        
        # Get workflow searches
        items.extend(get_workflow_searches())
        
        # Get shell aliases
        items.extend(get_shell_aliases())
        
        # Get custom web searches
        items.extend(get_custom_web_searches())

        return {"items": items}
        
    except Exception as e:
        return {
            "items": [{
                "title": "Error reading searches",
                "subtitle": str(e),
                "valid": False
            }]
        }

def filter_results(items, filter_type=None, search_query=""):
    """Filter results based on type and search query."""
    filtered_items = []

    
    for item in items:
        # Apply type filter if specified
        if filter_type and item["variables"]["type"] != filter_type:
            continue
        
        # If there's no search query after the filter, include all items of that type
        if not search_query:
            filtered_items.append(item)
            continue
            
        # Get searchable text based on type
        searchable_text = item["variables"].get("searchable_text", "").lower()
        if not searchable_text:
            # Fallback to concatenating all searchable fields
            searchable_fields = [
                item["title"],
                item["subtitle"],
                item["variables"].get("keyword", ""),
                item["variables"].get("display_text", "")
            ]
            searchable_text = " ".join(field for field in searchable_fields if field).lower()
        
        # Add item if search query matches
        if search_query in searchable_text:
            filtered_items.append(item)
    
    return filtered_items

if __name__ == "__main__":
    # Get query from Alfred
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    # Debug logging
    debug_log_path = os.path.expanduser('~/Desktop/alfred_debug.log')
    with open(debug_log_path, 'a') as f:
        f.write(f"\nReceived args: {sys.argv}\n")
        f.write(f"Args: {args}\n")
    
    # Get all results
    results = get_all_searches()
    
    if args:
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
        elif first_arg == "_alias":
            filter_type = "alias"
            search_query = " ".join(args[1:]).lower() if len(args) > 1 else ""
        elif first_arg == "_cmd":
            filter_type = "command"
            search_query = " ".join(args[1:]).lower() if len(args) > 1 else ""
        elif first_arg == "_git":
            filter_type = "git"
            search_query = " ".join(args[1:]).lower() if len(args) > 1 else ""
        elif first_arg == "web":
            filter_type = "websearch"
            search_query = " ".join(args[1:]).lower() if len(args) > 1 else ""
        elif first_arg == "wf":
            filter_type = "workflow"
            search_query = " ".join(args[1:]).lower() if len(args) > 1 else ""
        else:
            search_query = " ".join(args).lower()
        
        # Filter results
        filtered_items = filter_results(results["items"], filter_type, search_query)
        
        results["items"] = filtered_items
    
    # Output results to Alfred
    print(json.dumps(results)) 