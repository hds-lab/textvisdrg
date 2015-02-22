#!/bin/bash

loggy "Install scipy & numpy..."
apt-get install -y libatlas-dev libblas-dev liblapack-dev gfortran
apt-get install -y python-numpy python-scipy
