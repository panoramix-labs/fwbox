fwbox
#####

Firmware debugging box: a python REPL running locally and running
commands for debugging firmware on a local or remote machine.

For now, very few commands are supported, and only for the sigrok-cli back-end.


Building and running
********************

This project is not yet on pip, but can be installed from an URL:

.. code-block:: console

   pip install git+https://github.com/panoramix-labs/fwbox

For hacking on it, it can also be built manually this way:

.. code-block:: console

   # Clone the repo
   git clone https://github.com/panoramix-labs/fwbox
   cd fwbox

   # Enable a virtual environment
   python -m venv .venv
   . .venv/activate

   # build and install the package
   python -m build
   pip install .
