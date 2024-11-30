fwbox
#####

Firmware debugging box: a python REPL running locally and running
commands for debugging firmware on a local or remote machine.

For now, very few commands are supported, and only for the sigrok-cli back-end.


Building and running
********************

This is not in condition to be published to pip yet, so building manually is required:

.. code-block:: console

   git clone https://github.com/panoramix-labs/fwbox
   cd fwbox
   python -m build
   pip install .
