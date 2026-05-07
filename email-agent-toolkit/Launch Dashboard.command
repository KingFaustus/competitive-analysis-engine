#!/bin/bash
cd /Users/alexstephens27/competitive-analysis-agent-1/email-agent-toolkit

# Apply custom icon to this file
ICON="$(pwd)/dashboard_icon.png"
SELF="$(pwd)/Launch Dashboard.command"
if [ -f "$ICON" ]; then
    osascript -e "
use framework \"AppKit\"
set img to (current application's NSImage's alloc()'s initWithContentsOfFile:(\"$ICON\"))
(current application's NSWorkspace's sharedWorkspace()'s setIcon:img forFile:(\"$SELF\") options:0)
" 2>/dev/null
fi

export ANTHROPIC_API_KEY="$(security find-generic-password -s 'anthropic_api_key' -w 2>/dev/null)"
caffeinate -i python3 run_dashboard.py
