#!/bin/bash

# Collection of useful functions

function loggy {
    # Prints a message in green with lots of space around it.
    # If the 2nd parameter is error, message is red
    # http://misc.flogisoft.com/bash/tip_colors_and_formatting

    case "$2" in
        error)
            # Red text
            echo -e $'\e[1m\e[31m'
            ;;
        warn)
            # Red text
            echo -e $'\e[33m'
            ;;
        *)
            # Green text
            echo -e $'\e[32m'
            ;;
    esac

    echo -e $1
    echo -e $'\e[0m'
}

function exists {
    # Checks if a command exists, returns a status code
    command -v $1 &> /dev/null
    return $?
}

function started {
    # Checks if a service is running
    service $1 status | grep "running" &> /dev/null
    return $?
}

function service_exists {
    service $1 status &> /dev/null
    return $?
}

# Call with a prompt string. The user may type yes or no
# The default is no.
# If any second argument is provided, the default is yes
function confirm {
    
    if [ -z "$2" ]; then
        defaults="[y/N]"
    else
        defaults="[Y/n]"
    fi
    
    read -r -p "${1:-Are you sure?} $defaults " response
    
    case $response in
        [yY][eE][sS]|[yY]) 
            true
            ;;
        [nN][oO]|[nN])
            false
            ;;
        *)
            if [ -z "$2" ]; then
                false
            else
                true
            fi
            ;;
    esac
}

# Call with a question for the user like name=$(prompt "what is your name?")
# A default value can also be provided as a 2nd arg.
function prompt {
    if [ -z "$2" ]; then
        read -r -p "$1 " response
    else
        read -r -p "$1 [$2] " response
        if [ -z "$response" ]; then
            response=$2
        fi
    fi
    echo $response
}

# Call after a previous command, with an error message as the argument
function failif {
    if [ $? -gt 0 ]; then
	loggy "${1:-Error!}" "error"
	exit 1
    fi
}

# Call with a filename to remove global permissions
function secure {
    chmod o-rwx $1
    failif "Failed to remove global permissions on $1"
}

function generateRandomString {
    python -c 'import random, string; print "".join([random.SystemRandom().choice(string.digits + string.letters) for i in range(100)])'
}

function buffer_fail {
    echo "    $1"
    output="$($1 2>&1)"
    if [ $? -gt 0 ]; then
        loggy "${output}" "error"
        loggy "----------" "error"
        loggy "$2" "error"
        exit 1
    fi
    echo "    Success."
}
