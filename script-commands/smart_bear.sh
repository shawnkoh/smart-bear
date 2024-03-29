#!/bin/zsh

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Smart Bear
# @raycast.mode fullOutput
# @raycast.refreshTime 1h

# Optional parameters:
# @raycast.icon 🤖
# @raycast.packageName sg.shawnkoh.smart-bear

# Documentation:
# @raycast.author Shawn Koh
# @raycast.authorURL https://github.com/shawnkoh

cd ~/repos/shawnkoh/notes ;

git add -A && git commit -m "Commit unexpected changes" ;

python3 ~/repos/andymatuschak/Bear-Markdown-Export/bear_export_sync.py --out ~/repos/shawnkoh/notes/bear --backup ~/repos/shawnkoh/notes/bear-backup ;

cd ~/repos/shawnkoh/smart-bear ;

smart-bear backlinks ;

python3 ~/repos/andymatuschak/Bear-Markdown-Export/bear_export_sync.py --out ~/repos/shawnkoh/notes/bear --backup ~/repos/shawnkoh/notes/bear-backup ;
cd ~/repos/shawnkoh/notes ;
git add -A && git commit -m "Commit imported changes to Bear" ;
git push ;

smart-bear anki ;

