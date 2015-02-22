#!/bin/bash
# Set up a local development environment
# Prequisites:
# - Python 2.7 with pip and virtualenv, optionally virtualenvwrapper
# - npm with bower
# - MySQL
#
# Usage:
#
# Prompts the user for database settings
#   ./dev_setup.sh
# Provide database settings on the command line:
#   ./dev_setup.sh dbhost dbport dbname dbuser dbpass

set -e

function script_dir {
    cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd
}

SCRIPTS_DIR=$(script_dir)
source $SCRIPTS_DIR/functions.sh

PROJECT_ROOT=$(cd $(script_dir) && cd ../.. && pwd)
VENV_NAME=$(basename $PROJECT_ROOT)
DATABASE_CHARSET=utf8mb4
DATABASE_COLLACTION=utf8mb4_unicode_ci

if ! ([ $# -eq 0 ] || [ $# -eq 5 ]); then

    loggy "ERROR: Must be called with 0 or 5 arguments." "error"

    echo "Script usage:"
    echo "  Prompts the user for database settings:"
    echo "    ./dev_setup.sh"
    echo "  Provide database settings on the command line:"
    echo "    ./dev_setup.sh dbhost dbport dbname dbuser dbpass"
    echo
    exit 1
fi





loggy "CHECKING SYSTEM SETUP"

if exists 'npm'; then
    NPM_EXE=$(which npm)
else
    loggy "ERROR: Node package manager (npm) not available.\nPlease install node.js on your machine." "error"
    loggy "See: https://github.com/joyent/node/wiki/Installing-Node.js-via-package-manager"
    exit 1
fi
echo "Using npm at $NPM_EXE"

if ! exists 'bower'; then
    loggy "ERROR: Bower not installed.\nPlease install Bower on your machine.\nExample: sudo npm install -g bower" "error"
    exit 1
fi

if exists 'mysql'; then
    MYSQL_EXE=$(which mysql)
else
    loggy "ERROR: MySQL not installed.\nPlease install MySQl on your machine." "error"
    exit 1
fi
echo "Using mysql at $MYSQL_EXE"

if exists 'python2.7'; then
    PYTHON_EXE=$(which python2.7)
elif exists 'python' && [[ $(python --version 2>&1) == *"2.7"* ]]; then
    PYTHON_EXE=$(which python)
else
    loggy "ERROR: Python 2.7 not available.\nPlease install Python 2.7 on your machine." "error"
    exit 1
fi
echo "Using python at $PYTHON_EXE"

if exists 'pip2.7'; then
    PIP_EXE=$(which pip2.7)
elif exists 'pip' && [[ $(pip --version) == *"2.7"* ]]; then
    PIP_EXE=$(which pip)
else
    loggy "ERROR: pip not available.\nPlease add pip to your python distribution.\nExample: sudo easy_install pip." "error"
    exit 1
fi

if ! (exists 'virtualenvwrapper.sh' || exists 'virtualenv'); then
    loggy "ERROR: Virtualenv (and optionally virtualenvwrapper) must be installed.\nPlease install virtualenv on you machine.\nExample: sudo $PIP_EXE install virtualenv virtualenvwrapper" "error"
    exit 1
fi

if exists 'virtualenvwrapper.sh' && [ -z "$WORKON_HOME" ]; then
    loggy "It is recommended that you load virtualenvwrapper on login.\nYou can add the following to ~/.bashrc :" "warn"
    echo "------"
    echo "export WORKON_HOME=$HOME/.virtualenvs"
    echo "source \$(which virtualenvwrapper_lazy.sh)"
    echo "------"
fi

loggy "Confirmed Python 2.7, pip, virtualenv, mysql, npm, and bower."



loggy "MYSQL DATABASE SETUP"

if [ $# -eq 5 ]; then
    DATABASE_HOST=$1
    DATABASE_PORT=$2
    DATABASE_NAME=$3
    DATABASE_USER=$4
    DATABASE_PASS=$5
else
    loggy "Please provide information for accessing the database.\nIf the database does not exist, you will be prompted to create it."

    DATABASE_HOST=$(prompt "Hostname:" "localhost")
    DATABASE_PORT=$(prompt "Port:" "3306")
    DATABASE_NAME=$(prompt "Database name:" "textvisdrg")
    DATABASE_USER=$(prompt "User:" "textvisdrg")
    DATABASE_PASS=$(prompt "Password:" $DATABASE_USER)
fi

function test_database {
    echo "Testing connection settings..."

    # Try and connect to the database using these credentials
    mysql -h $DATABASE_HOST -P $DATABASE_PORT -u $DATABASE_USER -p$DATABASE_PASS $DATABASE_NAME 2> /dev/null << EOF
show tables;
EOF

    if [ $? -gt 0 ]; then
        loggy "The database does not yet exist.\nYou may run the following script to create it:" "warn"
        echo "--------------"
        cat << EOF
CREATE DATABASE IF NOT EXISTS ${DATABASE_NAME}
    DEFAULT CHARACTER SET = '${DATABASE_CHARSET}'
    DEFAULT COLLATE = '${DATABASE_COLLATION}';
GRANT USAGE ON *.* to ${DATABASE_USER}@localhost identified by '${DATABASE_PASS}';
GRANT ALL PRIVILEGES ON ${DATABASE_NAME}.* TO ${DATABASE_USER}@localhost;
FLUSH PRIVILEGES;
EOF
        echo "--------------"

        if ! confirm "Press enter once you have created the database" "yes"; then
            loggy "User cancelled." "warn"
            exit 1
        fi

        false
    else
        true
    fi
}

# Keep trying until the database is ready
test_database
while [ $? -gt 0 ];
do
    test_database
done

echo "Database connection successful."



loggy "PYTHON VIRTUAL ENVIRONMENT SETUP"


echo "Configuring Python virtualenv '$VENV_NAME'..."

if exists 'virtualenvwrapper.sh'; then
    
    echo "Using virtualenvwrapper..."
    
    # Set up virtualenv and virtualenvwrapper
    source $(which virtualenvwrapper.sh)

    # Create it
    rmvirtualenv $VENV_NAME
    mkvirtualenv --system-site-packages --python="${PYTHON_EXE}" -a "$PROJECT_ROOT" "$VENV_NAME" || echo "mkvirtualenv returns weird exit statuses"

    failif "ERROR: Could not create virtualenv"

elif exists 'virtualenv'; then

    echo "Using plain virtualenv..."
    echo "Virtual environment location: ${PROJECT_ROOT}/.virtualenv"
    virtualenv --system-site-packages --python="${PYTHON_EXE}" "${PROJECT_ROOT}/.virtualenv"
    failif "ERROR: Could not create virtualenv"
    
    source "${PROJECT_ROOT}/.virtualenv/bin/activate"
    failif "ERROR: Unable to load virtualenv"
else

    loggy "ERROR: Virtualenv (optionally with virtualenvwrapper) must be installed" "error"
    exit 1

fi


loggy "Installing Fabric..."
pip install -q Fabric path.py
failif "ERROR: Error installing Fabric and path.py... aborting."

loggy "Installing dependencies..."
fab dependencies:dev
failif "ERROR: Error running fab dependencies"

loggy "Creating new .env file..."
SECRET_KEY=$(generateRandomString)
GOOGLE_ANALYTICS_ID=
SERVER_HOST=0.0.0.0
PORT=8000
SETTINGS_MODULE=msgvis.settings.dev
export DATABASE_HOST DATABASE_PORT DATABASE_NAME DATABASE_USER DATABASE_PASS
export SECRET_KEY GOOGLE_ANALYTICS_ID
export SERVER_HOST PORT SETTINGS_MODULE
fab interpolate_env

loggy "Installing additional dependencies and migrating database..."

# Bring up the database
fab migrate

loggy "Development setup complete."
