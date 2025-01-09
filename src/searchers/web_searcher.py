import os
from ..utils.plist_reader import read_plist_file

def get_built_in_searches():
    """Get built-in web searches from Alfred preferences."""
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

def get_custom_web_searches():
    """Get custom web searches from Alfred preferences."""
    web_searches_path = os.path.expanduser(
        "~/Library/Application Support/Alfred/Alfred.alfredpreferences/preferences/features/websearch/prefs.plist"
    )
    custom_searches = []
    
    web_searches = read_plist_file(web_searches_path)
    if web_searches:
        custom_sites = web_searches.get('customSites', {})
        
        for site_id, site_data in custom_sites.items():
            if not site_data.get('enabled', True):
                continue
                
            custom_searches.append({
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
    
    return custom_searches 