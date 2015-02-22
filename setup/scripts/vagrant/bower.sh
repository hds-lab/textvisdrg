# Install some global NPM modules we might need

loggy "Installing bower..."
exists 'bower' || npm install -g bower
failif "ERROR: Error installing bower."


