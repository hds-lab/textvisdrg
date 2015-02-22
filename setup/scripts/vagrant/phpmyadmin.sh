# Install phpmyadmin for convenience

loggy "Installing PHP and phpmyadmin..."

exists 'php5' || apt-get install -y php5
failif "ERROR: Error installing php5."

echo 'phpmyadmin phpmyadmin/dbconfig-install boolean true' | debconf-set-selections
echo 'phpmyadmin phpmyadmin/mysql/app-pass password $PHPMYADMIN_PW' | debconf-set-selections
echo 'phpmyadmin phpmyadmin/app-password-confirm password $PHPMYADMIN_PW' | debconf-set-selections
echo 'phpmyadmin phpmyadmin/mysql/admin-pass password $DBROOTPASS' | debconf-set-selections
echo 'phpmyadmin phpmyadmin/reconfigure-webserver multiselect apache2' | debconf-set-selections
apt-get install -y phpmyadmin
failif "ERROR: Error installing phpmyadmin."

# make sure it is linked to phpmyadmin
if ! [ -e /etc/apache2/conf.d/phpmyadmin.conf ]; then
    ln -s /etc/phpmyadmin/apache.conf /etc/apache2/conf.d/phpmyadmin.conf
fi
service apache2 restart

