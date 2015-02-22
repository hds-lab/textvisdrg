#!/bin/bash

# Make sure the machine is updated
loggy "Updating system..."

apt-get update -q
failif "ERROR: Could not download package info."

apt-get upgrade -y -q
failif "ERROR: Could not update system."
