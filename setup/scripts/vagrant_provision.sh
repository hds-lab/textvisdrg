#!/bin/bash

# Expects 1 argument, the full path to the project files

set -e
PROJECT_ROOT=$1
source ${PROJECT_ROOT}/setup/scripts/functions.sh
export DEBIAN_FRONTEND=noninteractive
set +e

PHPMYADMIN_PW=phpmyadmin
DBROOTPASS=root
VAGRANT_HOME=/home/vagrant

# Make sure the machine is updated
loggy "Updating system..."
buffer_fail "apt-get update" "ERROR: Could not download package info."
buffer_fail "apt-get upgrade -y" "ERROR: Could not update system."

# Install some global NPM modules we might need
loggy "Installing global npm packages..."
! exists 'bower' && buffer_fail "npm install -g bower" "ERROR: Error installing bower."
! exists 'grunt' && buffer_fail "npm install -g grunt-cli" "ERROR: Error installing grunt-cli."

# Make a fake node_modules folder
mkdir ${VAGRANT_HOME}/node_modules
chown vagrant:vagrant ${VAGRANT_HOME}/node_modules
ln -s ${VAGRANT_HOME}/node_modules ${PROJECT_ROOT}/node_modules
chown vagrant:vagrant ${PROJECT_ROOT}/node_modules

# Make sure the mysql service is started
loggy "Configuring MySQL..."

service mysql start
echo "Service started"
# Set a root password
mysql -u root -p$DBROOTPASS || mysqladmin -u root password $DBROOTPASS
echo "MySQL root user has password: $DBROOTPASS"

# Install phpmyadmin for convenience
loggy "Installing PHP and phpmyadmin..."
! exists 'php5' && buffer_fail "apt-get install -y php5" "ERROR: Error installing php5."
echo 'phpmyadmin phpmyadmin/dbconfig-install boolean true' | debconf-set-selections
echo 'phpmyadmin phpmyadmin/mysql/app-pass password $PHPMYADMIN_PW' | debconf-set-selections
echo 'phpmyadmin phpmyadmin/app-password-confirm password $PHPMYADMIN_PW' | debconf-set-selections
echo 'phpmyadmin phpmyadmin/mysql/admin-pass password $DBROOTPASS' | debconf-set-selections
echo 'phpmyadmin phpmyadmin/reconfigure-webserver multiselect apache2' | debconf-set-selections
buffer_fail "apt-get install -y phpmyadmin" "ERROR: Error installing phpmyadmin."

# make sure it is linked to phpmyadmin
if ! [ -e /etc/apache2/conf.d/phpmyadmin.conf ]; then
    ln -s /etc/phpmyadmin/apache.conf /etc/apache2/conf.d/phpmyadmin.conf
fi
service apache2 restart

# Fail if error after this
set -e

# Create a database table
DBHOST=localhost
DBPORT=3306
DBNAME=codingdb
DBUSER=dbuser
DBPASS=dbpass

loggy "Creating database..."

# Create a database just for the project
cat <<EOF | mysql -u root -p$DBROOTPASS -h $DBHOST
CREATE DATABASE IF NOT EXISTS \`$DBNAME\` CHARACTER SET utf8 COLLATE utf8_general_ci;
GRANT ALL PRIVILEGES ON \`$DBNAME\`.* TO '$DBUSER'@'$DBHOST' IDENTIFIED BY '$DBPASS';
GRANT USAGE ON *.* TO '$DBUSER'@'$DBHOST';
EOF

echo "    DATABASE_URL=mysql://$DBUSER:$DBPASS@$DBHOST:$DBPORT/$DBNAME"

loggy "Running development setup script...\n-----------------------------------"

VENV_NAME=$(basename $PROJECT_ROOT)
su --login -c "${PROJECT_ROOT}/setup/scripts/dev_setup.sh $PROJECT_ROOT $DBHOST $DBPORT $DBNAME $DBUSER $DBPASS" vagrant

loggy "-----------------------------------"

# Add the workon command to the bashrc
loggy "Augmenting user's bashrc file..."

if grep -q 'workon' ${VAGRANT_HOME}/.bashrc; then
    echo "workon already in bashrc"
else
    echo "workon $VENV_NAME" >> ${VAGRANT_HOME}/.bashrc
    echo "added workon to bashrc"
fi

if grep -q 'remount' ${VAGRANT_HOME}/.bashrc; then
    echo "remount already in bashrc"
else
    echo "alias remount_vagrant='sudo mount -o remount home_vagrant_textvisdrg'" >> ${VAGRANT_HOME}/.bashrc
    echo "added remount_vagrant to bashrc"
fi

loggy "Access the database at http://localhost:8000/phpmyadmin"
loggy "SSH into localhost:2222 (vagrant/vagrant) and run 'fab runserver'\n  then try http://localhost:8080"
