#!/bin/bash

# Make sure the mysql service is started
loggy "Configuring MySQL..."

service mysql start
echo "Service started"
# Set a root password
mysql -u root -p$DBROOTPASS || mysqladmin -u root password $DBROOTPASS
echo "MySQL root user has password: $DBROOTPASS"

loggy "Creating database..."

# Create a database just for the project
cat <<EOF | mysql -u root -p$DBROOTPASS -h $DBHOST
CREATE DATABASE IF NOT EXISTS \`$DBNAME\` CHARACTER SET utf8 COLLATE utf8_general_ci;
GRANT ALL PRIVILEGES ON \`$DBNAME\`.* TO '$DBUSER'@'$DBHOST' IDENTIFIED BY '$DBPASS';
GRANT ALL PRIVILEGES ON \`$TEST_DBNAME\`.* TO '$DBUSER'@'$DBHOST' IDENTIFIED BY '$DBPASS';
GRANT USAGE ON *.* TO '$DBUSER'@'$DBHOST';
EOF

echo "    DATABASE_URL=mysql://$DBUSER:$DBPASS@$DBHOST:$DBPORT/$DBNAME"
