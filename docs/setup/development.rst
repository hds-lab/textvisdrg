Development Setup
=================

To run this project, you can either set up your own machine or use a
virtual Ubuntu machine with Vagrant. There are separate instructions for
each below:

.. contents::
    :local:

Run in a VM
-----------

There is configuration included to run this project inside an Ubuntu
virtual machine controlled by Vagrant.
This is especially recommended on Windows. If you go this route, you can
skip the Manual Setup section below.

Instead, follow these steps:

1. Install `Vagrant <https://www.vagrantup.com/downloads.html>`_ and
   `Virtualbox <https://www.virtualbox.org/wiki/Downloads>`_

2. Start the virtual machine.

This will download a basic Ubuntu image, install some additional
software on it, and perform the initial project setup.

.. note::

    **If you are on windows**: You should run this command in an
    Administrator cmd.exe or Powershell.

    .. code-block:: bash

        $ vagrant up

3. Once your Ubuntu VM is started, you can SSH into it with
   ``vagrant ssh``. This will use a key-based authentication to log you
   into the VM.

You can also log in using any SSH client (e.g. PuTTY), at
``localhost:2222``. The username and password are both ``vagrant``, or
you can also configure key-based auth: use ``vagrant ssh-config`` to
find the private key for accessing the VM.

When you log in, your terminal will automatically drop into a Python
virtualenv and cd to ``/home/vagrant/textvisdrg``.

Manual Setup
------------

You will need to have the following packages installed:

-  MySQL 5.5
-  Python 2.7 and `pip <https://pip.pypa.io/en/latest/installing.html>`_
-  `virtualenv <http://virtualenv.readthedocs.org/en/latest/virtualenv.html>`_
-  `virtualenvwrapper <http://virtualenvwrapper.readthedocs.org/en/latest/install.html>`_
   (recommended)
-  `Node.js <https://github.com/joyent/node/wiki/Installing-Node.js-via-package-manager>`_
-  `Bower <http://bower.io/>`_

Once you have the above prerequisites working, clone this repository to
your machine.

Go to the directory where you have cloned the repository and run the
setup script, as below:

.. code-block:: bash

    $ cd textvisdrg
    $ ./setup/scripts/dev_setup.sh

This script will perform the following steps for you:

1. Check that your system has the prerequisites available.
2. Prompt you for database settings. If it can't reach the database, it
   will give you a snippet of MySQL code needed to create the database
   with the supplied settings.
3. Create a Python virtual environment. This keeps Python packages
   needed for this project from interfering with any other packages you
   already have installed on your system.
4. Creates a ``.env`` file in your project directory that sets
   environment variables for Django, most importantly the database
   connection settings.
5. Installs python packages, NPM packages, and bower packages (using the
   ``fab dependencies`` command).
6. Runs the database migrations (using ``fab migrate``).

