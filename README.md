# Alfred Keyword Viewer

This workflow helps you discover and search through all keywords used in your Alfred setup. It shows keywords from your installed workflows, web searches (both built-in and custom), making it easy to find and remember all your Alfred shortcuts.

## Usage

- Type `kw` to see all keywords
- Type `kw <search terms>` to find keywords matching your search (e.g., `kw google maps`)
- Use filters to narrow down results:
  - `kw _web` to show only web search keywords
  - `kw _work` to show only workflow keywords
  - `kw _alias` to show only shell aliases
  - Add search terms after any filter: `kw _web google maps` or `kw _work git push`

## What You'll See

Each result shows:

- For web searches:
  - Title: `SearchName: keyword`
  - Subtitle: `[Web Search] URL or search template`
- For workflows:
  - Title: `WorkflowName: keyword`
  - Subtitle: `[Workflow by Creator] Description`
- For shell aliases:
  - Title: `AliasName: alias`
  - Subtitle: `[Shell Alias] Actual command`

## Why It's Useful

- Find forgotten keywords when you have many workflows installed
- Discover keywords that might conflict across different workflows
- Quick overview of all available shortcuts in your Alfred setup
- Search through descriptions and names to find the workflow or search you need

Perfect for power users with many workflows or anyone who wants to better organize their Alfred keywords.

## Potential Future Improvements

- Add workflow version information to help track updates
- Show workflow bundle IDs to identify unique workflows
- Include workflow website/documentation links when available
- Display workflow categories or tags if defined
- Add workflow compatibility information (minimum Alfred version)
- Show related keywords from the same workflow
- Include workflow hotkey information if configured
