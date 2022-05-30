source ~/.config/bash_custom_functions.sh

# set PATH so it includes user's private ~/.local/bin if it exists
if [ -d "$HOME/.local/bin" ] ; then
    PATH="$HOME/.local/bin:$PATH"
fi

# setup zoxide
eval "$(zoxide init bash)"

# setup starship prompt
eval "$(starship init bash)"

# setup custom aliases
alias byb='byobu'
alias '..'='cd ..'

set +H

bind -m emacs-standard -x '"\C-h": __fzf_history__'
bind -m emacs-standard -x '"\C-o": __fzf_cd__'
bind -m emacs-standard -x '"\C-p": fzf_file_widget'
