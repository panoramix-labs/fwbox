.. image:: fwbox.png

Firmware debugging box: a python REPL running locally and running
commands for debugging firmware on a local or remote machine.

For now, very few commands are supported, and only for the sigrok-cli back-end.


Building
********

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

   # Build and install the package
   python -m build
   pip install .


Example session
***************

Running ``fwbox`` will trigger a scan for local devices:

.. code-block:: console

   -- Scanning all runners...
   -- platform lap1
   -- scannning for SigrokRunner on lap1
   $ sigrok-cli --scan
   $ sigrok-cli --driver demo --config  --show
   -- Shell ready. Type 'help' or '?' to list commands.

The prompt is ``fwbox$``, and extra commands run by ``fwbox`` are shown with a leading ``$``:

.. code-block:: console

   fwbox$

The ``list`` will show the available devices and their state:

.. code-block:: console

   fwbox$ list
   $ sigrok-cli --driver demo --config  --show
   [OK] lap1:SigrokRunner:demo: ['D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7']

Running the ``ssh`` comand permits to access more hosts from remote:

.. code-block:: console

   fwbox$ ssh 172.22.0.3
   -- platform lap1
   -- scannning for SigrokRunner on lap1
   $ sigrok-cli --scan
   -- platform 172.22.0.3
   -- scannning for SigrokRunner on 172.22.0.3
   $ ssh -oControlMaster=auto -oControlPath=%d/.ssh/%C 172.22.0.3 'sigrok-cli' '--scan'
   $ ssh -oControlMaster=auto -oControlPath=%d/.ssh/%C 172.22.0.3 'sigrok-cli' '--driver' 'demo' '--config' '' '--show'
   $ ssh -oControlMaster=auto -oControlPath=%d/.ssh/%C 172.22.0.3 'sigrok-cli' '--driver' 'fx2lafw' '--config' 'conn=1.4' '--show'

An 8-channel logic analyzyer is now available:

.. code-block:: console

   fwbox$ list
   $ sigrok-cli --driver demo --config  --show
   [OK] lap1:SigrokRunner:demo: ['D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7']
   $ ssh -oControlMaster=auto -oControlPath=%d/.ssh/%C 172.22.0.3 'sigrok-cli' '--driver' 'demo' '--config' '' '--show'
   [OK] 172.22.0.3:SigrokRunner:demo: ['D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7']
   $ ssh -oControlMaster=auto -oControlPath=%d/.ssh/%C 172.22.0.3 'sigrok-cli' '--driver' 'fx2lafw' '--config' 'conn=1.4' '--show'
   [OK] 172.22.0.3:SigrokRunner:fx2lafw:conn=1.4: ['D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7']

Now if I unplug the logic analyzer and attach it to my local computer, it appears as a local device:

.. code-block:: console

   fwbox$ refresh
   ...
   fwbox$ list
   $ sigrok-cli --driver demo --config  --show
   [OK] lap1:SigrokRunner:demo: ['D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7']
   $ sigrok-cli --driver fx2lafw --config conn=1.48 --show
   [OK] lap1:SigrokRunner:fx2lafw:conn=1.48: ['D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7']
   $ ssh -oControlMaster=auto -oControlPath=%d/.ssh/%C 172.22.0.3 'sigrok-cli' '--driver' 'demo' '--config' '' '--show'
   [OK] 172.22.0.3:SigrokRunner:demo: ['D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7']
