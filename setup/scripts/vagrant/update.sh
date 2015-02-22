#!/bin/bash

# Make sure the machine is updated
loggy "Updating system..."
buffer_fail "apt-get update" "ERROR: Could not download package info."
buffer_fail "apt-get upgrade -y" "ERROR: Could not update system."
