*******
Plebnet
*******

|jenkins_build|

*A self-replicating autonomous Tribler exit-node.*

Documentation
=============
 - The full report regarding this project can be found `here <https://github.com/Tribler/tribler/files/2133729/Bachelor_Project_BotNet.pdf>`_
 - The main issue regarding this project can be found `here <https://github.com/Tribler/tribler/issues/2925>`_

Description
===========
After the first instance is installed on a VPS, PlebNet will run Tribler as an exit-node and earn credits,
which will be used to acquire new VPS instances for the next generation PlebNet agents. This should eventually create a
community of exit-nodes for Tribler, thus creating a reliable and sufficiently large capacity for anonymous data
transfer through the Tribler network

Initialisation
==============
The first instance can be installed by downloading the file create-child.sh in Plebnet/plebnet/clone and call:

.. code-block:: console

   ./create-child.sh <parameter> <value>

::

   Usage: ./create-child.sh <parameter> <value>
      -h --help              Shows this help message
      -i --ip                Ip address of the server to run install on
      -p --password          Root password of the server
      -t --testnet           Install agent in testnet mode (default 0)
      -e --exitnode          Run as exitnode for tribler
      -conf --config         (optional) VPN configuration file (.ovpn)
                             Requires the destination config name.
                             Example: -conf source_config.ovpn dest_config.ovpn
      -cred --credentials    (optional) VPN credentials file (.conf)
                             Requires the destination credentials name.
                             Example -cred source_credentials.conf dest_credentials.conf
      -b --branch            (optional) Branch of code to install from (default master)

    
This installs all dependencies (Tribler, Electrum, Cloudomate and ofcourse PlebNet).
After installation the "plebnet setup" is called and a cron job is set up to regularly call "plebnet check".

**exitnode is off by default.** Using :code:`-e` flag when executing :code:`create-child.sh` will install PlebNet in eixtnode mode. 

This check function checks whether the agent instance has acquired sufficient funds to buy a new VPS and spawn a new
child instance. If this is the case, the PlebNet agent will execute the previously mentioned steps on the new server and
the community has welcomed a newborn.


Running PlebNet locally
=====================
For running PlebNet locally, the following steps are necessary:

- All dependencies installed via the create-child.sh script, must be installed manually.
- Download PlebNet and all submodules by running the following command:

.. code-block:: console

    git clone --recurse-submodules https://github.com/Tribler/PlebNet.git
    
- Go to the main folder and execute the following command:

.. code-block:: console

    pip install .
    
- To install PlebNet locally, do the same as one would for a remote server, but with your own IP address:

.. code-block:: console
    bash create-child.sh -i 127.0.0.1 -p <pass> 
    
- **note** that a cron job is created in :code:`/etc/cron.d/plebnet`, which calls :code:`plebnet check` every 5 minutes. To disable this, remove the file. 

Usage
-----

You can also install PlebNet locally by installing the dependencies from :code:`plebnet/clone/install.sh` and creating the necessary folders that :code:`plebnet/clone/create-child.sh` would create. After that, you need to call :code:`plebnet setup`, if the flag **--exitnode** is provided, Tribler will be run as exitnode.

:code:`plebnet conf setup` allows you to set the github issues configurations. So when a root agent is created, setting the github issuer configurations allows the agent and its children to create issues.
To set the configurations:
:code:`plebnet conf setup -gu <usernme> -gp <password> -go <repo owner> -gr <git repo> -ga 1`.

**note that an account and repository dedicated to git issues only needs to be created for this functionality**.

The rest of :code:`plebnet` commands:

::


   usage: plebnet [-h]
                  {setup,check,conf,irc}
                  ...

   positional arguments:
    {setup,check,conf,irc}
       setup               Run the setup of PlebNet
       check               Checks if the plebbot is able to clone
       conf                Allows changing the configuration files
       irc                 Provides access to the IRC client

   optional arguments:
     -h, --help            show this help message and exit


   usage: plebnet setup [-h] [--testnet] [--exitnode]

   optional arguments:
     -h, --help  show this help message and exit
     --testnet   Use TBTC instead of BTC
     --exitnode  Run as exitnode for Tribler


   usage: plebnet irc [-h] {status,start,stop,restart}

   positional arguments:
     {status,start,stop,restart}
       status              Provides information regarding the status of the IRC Client
       start               Starts the IRC Client
       stop                Stops the IRC Client
       restart             Restarts the IRC Client

   optional arguments:
     -h, --help            show this help message and exit

Configuring
-----------
All PlebNet configurations are stored inside the :code:`~/.config/` directory.
When testing, you can modify these files and PlebNet will apply the new values.

plebnet_setup.cfg
~~~~~~~~~~~~~~~~~
This file contains the configuration of the agent.

::

  [irc]
  channel = #plebnet123
  server = irc.undernet.org
  port = 6667
  nick_def = plebbot
  nick = plebbot2930
  timeout = 60

  [vps]
  host = linevast
  initdate = 15:06:33 02-05-2018
  finaldate = 02-06-2018

  [vpn]
  installed = 0
  host = azirevpn
  child_prefix = child_
  own_prefix = own
  config_name = _config.ovpn
  credentials_name = _credentials.conf
  running = 0
  pid = 0

  [paths]
  plebnet_config = ~/.plebnet.cfg
  plebnet_home = ~/PlebNet
  tribler_home = ~/PlebNet/tribler
  logger_path = ~/data
  vpn_config_path = ~/

  [filenames]
  logger_file = plebnet.logs

  [pids]
  tribler_pid = twistd_tribler.pid
  tunnel_helper_pid = twistd_th.pid
  irc_pid = Documents/ircbot.pid

  [github]
  username = unset
  password = unset
  owner = unset
  repo = unset
  active = 0

  [wallets]
  testnet = 0
  testnet_created = 0
  initiate_once = 1
  password = plebnet

  [active]
  logger = 1
  verbose = 1

  [tribler]
  exitnode = 1

Each setting can be modified so that the next :code:`plebnet check` is run with different settings. 

DNA.json
~~~~~~~~
This file contains the provider weights for choosing providers and the agent's identity.

::

   {
       "Self": "twosync",
       "VPS": {
           "linevast": 0.5,
           "twosync": 0.5,
           "blueangelhost": 0.5,
           "undergroundprivate": 0.5
       },
       "tree": "plebbot2930"
   }
  
To restrict the provider choice of PlebNet, the value of the provider should be set to a very high number (>5000).
  
The :code:`"tree"` key indicates the current child's depth in the cluster starting from its root. The first value is the root node's :code:`IRC` nickname (due to its semi uniqueness). 
Some tree examples:

.. code-block:: python

   plebbot2930      # root node, it is the first of its inheritance tree
   plebbot2930.0    # this is the first child of the root node (child index 0)
   plebbot2930.1    # second child of root node
   plebbot2930.0.0  # second child of the first child (first grandchild)
   plebbot2930.0.5  # fifth grandchild
  
Using this, each node's origin can be identified in IRC (and in the PlebNet VISION tool). 

plebnet.json
~~~~~~~~~~~~
This file contains the agent's transactions and is used to keep track of servers to be installed.

::

  {
     "last_offer_date": 1530783430.253793, 
     "transactions": [
        "391a8ebeb10041c02585941357889c8a7d0531cbdf643540bd4c0cbd2272909d"
     ], 
     "expiration_date": 1533291353.528893, 
     "last_offer": {
        "BTC": 0.0014060814961627155, 
        "MB": 930
     }, 
     "installed": [], 
     "child_index": 1, 
     "chosen_provider": [
        "linevast", 
        0, 
        0.0014401424067158812
     ], 
     "bought": [
        [
         "linevast",
         "296b20d6885787054c3f94a4d8e87b39b1289c991c06ec419d2774a5358e8c9a", 
         7
        ]
     ]
     "excluded_providers": []
  }

In this example, :code:`Linevast` was the purchased server to be installed when its ready. The :code:`bought` list contains servers the agents needs to install. After installing, the entry is removed from :code:`bought` and put in :code:`installed`.

Checking the state of the agent
-------------------------------

IRC and PlebNet VISION (:code:`tools/vision`) can be used to check how the network and agents are doing. You can also check the agent on the server itself. When Tribler is running, its :code:`HTTP API` on port :code:`8085` can be queried for checking status, among other things (see :code:`plebnet/controllers/`). To kill Tribler, kill :code:`twistd` processes (although the cron job will start it again on the next iteration if it's not removed).

Use :code:`curl` to use the :code:`HTTP API`:

Triber settings
~~~~~~~~~~~~~~~
:code:`curl http://localhost:8085/settings`

Wallets
~~~~~~~~~~~~~~~
:code:`curl http://localhost:8085/wallets`
Shows the created wallets, Bitcoins can be sent to this address to test the agent's purchasing and installing abilities.

Market
~~~~~~~~~~~~~~~
You can find some useful market requests in the :code:`plebnet/controllers/market_controller.py` file.

State
~~~~~~~~~~~~~~~
:code:`curl http://localhost:8085/state` Shows the state of Tribler and exceptions.

VPN
====
VPN is currently only possible on LineVast. In Cloudomate, the functionalities to enable :code:`TUN/TAP` via the control panel was added. The agent checks for the VPN configurations by searching for files: :code:`own_config.ovpn` and :code:`own_credentials.conf`, these can be initialized from :code:`create-child.sh`. When the VPN is installed, ssh access to the server is **terminated**, which means that you can't access it from its normal IP. Use the **client panel** by logging in with the credentials (which should be mailed to the bot's main shared email address) and use the **serial console** to logon to the server.

To check if a machine suports vpn: :code:`cat /dev/net/tun`, the output should read 'File desciptor in bad state'. If the output reads 'No such file or directory', :code:`TUN/TAP` should be enabled from the control panel (which for Linevast happens automatically through Cloudomate).

.. |jenkins_build| image:: https://jenkins.tribler.org/job/GH_PlebNet/badge/icon
    :target: https://jenkins.tribler.org/job/GH_PlebNet
    :alt: Build status on Jenkins
