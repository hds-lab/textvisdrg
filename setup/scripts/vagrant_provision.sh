#!/bin/bash

# Expects 1 argument, the full path to the project files

set -e
PROJECT_ROOT=$1
source ${PROJECT_ROOT}/setup/scripts/functions.sh
export DEBIAN_FRONTEND=noninteractive

PHPMYADMIN_PW=phpmyadmin
DBROOTPASS=root
VAGRANT_HOME=/home/vagrant
VAGRANT_USER=vagrant
VENV_NAME=$(basename $PROJECT_ROOT)

DBHOST=localhost
DBPORT=3306
DBNAME=textvisdrg
DBUSER=dbuser
DBPASS=dbpass
DBCHARSET=utf8mb4
DBCOLLATION=utf8mb4_unicode_ci
TEST_DBNAME=test_$DBNAME

SCRIPTS_DIR=$PROJECT_ROOT/setup/scripts
source "${SCRIPTS_DIR}/vagrant/update.sh"
source "${SCRIPTS_DIR}/vagrant/mysql.sh"
source "${SCRIPTS_DIR}/vagrant/memcached.sh"
source "${SCRIPTS_DIR}/vagrant/phpmyadmin.sh"
source "${SCRIPTS_DIR}/vagrant/scipy.sh"
source "${SCRIPTS_DIR}/vagrant/bower.sh"

loggy "Running development setup script...\n-----------------------------------"

su --login -c "${SCRIPTS_DIR}/dev_setup.sh $DBHOST $DBPORT $DBNAME $DBUSER $DBPASS" $VAGRANT_USER

loggy "-----------------------------------"

source "${SCRIPTS_DIR}/vagrant/bashrc.sh"

loggy "Access the database at http://localhost:8000/phpmyadmin"
loggy "SSH into localhost:2222 (vagrant/vagrant) and run 'fab runserver'\n  then try http://localhost:8080"
