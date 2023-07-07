# setup custom aliases
alias '..'='cd ..'
alias 'rm_pkg_residual'="sudo apt remove --purge `dpkg -l | grep '^rc' | awk '{print $2}'`"
alias hx='helix-23.05-x86_64.AppImage'
alias helix='helix-23.05-x86_64.AppImage'
alias sar='python3 ~/.config/scripts/search_and_replace.py'
alias tr_trailing='sed -e "s/ \{1,\}$//"'
alias inc="xargs -I {} echo '1 + {}' | bc"
