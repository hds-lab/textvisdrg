# Install some global NPM modules we might need

loggy "Installing global npm packages..."
! exists 'bower' && buffer_fail "npm install -g bower" "ERROR: Error installing bower."
! exists 'grunt' && buffer_fail "npm install -g grunt-cli" "ERROR: Error installing grunt-cli."

