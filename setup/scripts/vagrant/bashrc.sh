#!/bin/bash

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
