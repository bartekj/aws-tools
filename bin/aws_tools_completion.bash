if [ -d "$HOME/.local/bin" ] ; then
    PATH="$HOME/.local/bin:$PATH"
fi

function __aws_env_update() {
    eval $(aws-env-update.py $@)
}

function __aws_roll_keys() {
    aws-roll-keys.py $@
}

function __awsenv_ps1() {
    if [ -e "$HOME/.aws/credentials" ]; then
        ps=$(cat $HOME/.aws/.env 2>/dev/null)
    fi
    if [ -n "$AWS_ENV" ]; then
        ps="$AWS_ENV"
    fi
    echo "<$ps>"
}

function __aws_envs() {
    COMPREPLY=()
    local words=( "${COMP_WORDS[@]}" )
    local word="${COMP_WORDS[COMP_CWORD]}"
    words=("${words[@]:1}")
    local completions="$(ls $HOME/.aws/env*asc | cut -d "." -f 3)"
    COMPREPLY=( $(compgen -W "$completions" -- "$word") )
}

complete -F __aws_envs awsenv
