.. _step_by_step_install:

************************
Package Installation
************************

To install epx-results, you can either use pip or clone the repo from GitHub and build the source code.
Either way, be sure to read the :ref:`epxresults_dependencies` section prior to installation.

Using pip
====================

<provide instructions for installing with pip>

.. _install_from_source:

Building from source
====================

If you don't install the latest release using pip,
you can instead clone the cource code and call the setup file.
This is the most common way to install epx-results if you want versions of the
code that have been updated since the latest official release. In this case,
after installation it is particularly important that you follow the instructions
in the :ref:`verifying_your_installation` section below.

Before installation, be sure you have installed the package dependencies
described in the :ref:`epxresults_dependencies` section.
If you will be :ref:`installing_epxresults_with_virtualenv`,
activate the environment before following the instructions below.
The first step is to clone the epx-results repository::

	git clone git@github.com:Epistemix-com/epx-results.git
	cd epx-results

Installing one of the official releases
------------------------------------------

All official releases of the code are tagged with their version name, e.g., v1.0.
To install a particular release::

	git checkout v1.0
	python setup.py install

This will install the v1.0 release of the code. Other official release versions (e.g., v1.1) can be installed similarly.

Installing the most recent main branch
------------------------------------------

If you prefer to use the most recent version of the code::

	git checkout main
	python setup.py install

This will install the main branch of the code that is currently under development. While the features in the official releases have a stable API, new features being developed in the main branch may not. However, the main branch may have new features and/or performance enhancements that you may wish to use for your science application. A concerted effort is made to ensure that only thoroughly tested and documented code appears in the public main branch, though epx-results users should be aware of the distinction between the bleeding edge version in main and the official release version available through pip.


.. _epxresults_dependencies:

Dependencies
============

If you install epx-results using pip, then most of your dependencies will be handled for you automatically. 

<add list of explicit dependencies here>

.. _verifying_your_installation:

Verifying your installation
==============================

After installing the code and its dependencies, fire up a Python interpreter and
check that the version number matches what you expect:

.. code:: python

	import epxresults
	print(epxresults.__version__)

If the version number is not what it should be, this likely means you have a previous
installation that is superseding the version you tried to install. This *should* be accomplished by doing `pip uninstall epxresults` before your new installation, but you may need to uninstall the previous build "manually". Like all python packages, you can find the installation location as follows:

.. code:: python

	import epxresults
	print(epxresults.__file__)

This will show where your active version is located on your machine. You can manually delete this copy of epxresults prior to your new installation to avoid version conflicts. (There may be multiple copies of epxresults in this location, depending on how may times you have previously installed the code - all such copies may be deleted prior to reinstallation).

Once you have installed the package, see :ref:`getting_started` for instructions on how to get up and running.

Testing your installation
=========================

<provide instructions on running a testing suite>


Troubleshooting
==================

<provide any troubleshooting hints here>



