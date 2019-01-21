*******
Plebnet
*******

|jenkins_build|

*A self-replicating autonomous Tribler exit-node.*

**Plebnet** is an Internet-deployed Darwinian reinforcement learning based on self-replicating. Also referred to as a *botnet for good*, it consists of many generations of autonomous entities living on VPS instances with VPN installed, running Tribler_ exit-nodes, and routing torrent traffic in our Tor-like network.

While providing privacy and anonymity for regular Tribler users, it is earning reputation in form of MB tokens stored on Trustchain, which are in turn put on sale for Bitcoin on a fully decentralized Tribler marketplace. Once the bot earns enough Bitcoin, it buys a new VPS instance using Cloudomate_, and finally self-replicates.


Bootstrapping
=============

The first running node needs to be installed manually. One of the options is to buy a VPS using Cloudomate, and install Plebnet from a local system using the ``plebnet/clone/create-child.sh`` script.

::

   Usage: ./create-child.sh [options]
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


Example:

.. code-block:: console

    ./create-child.sh -i <ip> -p <password> -e -b develop


For development purposes, it is also useful to know how to run Plebnet locally.

Lifecycle
=========

The life of a bot starts by executing ``plebnet setup`` command, which prepares the initial configuration, starts an IRC bot, and creates a cronjob running ``plebnet check`` command every 5 minutes.

The whole lifecycle is then managed by the ``check`` command. First, it ensures Tribler is running. Then it selects a candidate VPS provider and a specific server configuration for the next generation, and calculates the price. One of the pre-defined market strategies is used to convert obtained MB tokens to Bitcoin. Once enough resources are earned, it purchases the selected VPS and VPN options using Cloudomate.

Finally, it connects to the purchased server over SSH, downloads the latest Plebnet source code from GitHub, install required dependencies, sets up VPN, and runs ``plebnet setup`` to bring the child to life. At that moment, the parent selects a new candidate VPS and continues to maximize its offspring until the end of its own contract expiration.


Reinforcement Learning
======================
The choice of next VPS is dictated by QTable.

We define few mappings which are used in Reinforcement Learning:

-``states`` - VPS offers

-``environment`` – transition matrix between states. This kind of dictates what reinforcement we will get by choosing certain transition. Initially all 0s.

-``current_state`` – current VPS option

Initial values for QTable are calculated according to the formula bellow:

``1/(price^3) * bandwidth``

Environment is getting updated by each try of replication:

-when node manages to buy new option and replicate environment is updated positively (all transitions leading to ``current_state``)

-when nodes fails to buy option environment is getting updated negatively (transition between ``current_state`` and chosen failed state)
While we update the environment QTable entries are getting updated consequently.

What is passed to the child?

-his state (provider name + option name)

-name (to have some id)

-tree of replications

-``providers_offers`` (all VPSs offer for all providers)

-current ``qtable``


Currently VPSs are chosen using QTable , VPNs not.

To choose option from QTable we use exponential distribution with lambda converging decreasingly to 1. As lambda is changing with number of replications process seems to be similar to ``simulated annealing``.


Market Strategies
=================

Continuous Procurement Bot
==========================

In case of insufficient market liquidity, it might be needed to artificially boost MB demand by selling Bitcoin on the market. This is where **buybot** comes into play. It periodically lists all bids on the market, orders them by price and places asks matching the amount and price of bids exactly. It is also possible to make a limit order, so only asks for the bids of price less or equal the limit price would be placed.

.. code-block:: console

    Usage: ./buybot.py <limit price>


Visualization
==============

While the network is fully autonomous, there is a desire to observe its evolution over time. It is possible to communicate with the living bots over an IRC channel defined in ``plebnet_setup.cfg``, using a few simple commands implemented in ``ircbot.py``. Note that all commands only serve for retriving information (e.g. amount of data uploaded, wallet balance, etc.) and do not allow to change the bot's state.

**Plebnet Vision** is a tool allowing to track the state of the botnet over time and visualize the family tree of the whole network. The ``tracker`` module periodically requests the state of all bots and stores it into a file. The ``vision`` module is then a Flask web server which constructs a network graph and generates charts showing how the amount of uploaded and downloaded data, number of Tribler market matchmakers, and MB balance changed over time.


.. image:: https://user-images.githubusercontent.com/1707075/48701343-8d4a4a00-ebee-11e8-87d6-0aecb94caf76.gif
    :width: 60%

After installing the required dependencies, the Flask server and the tracker bot can be started by:

::

    python tools/vision/app_py.py

The HTTP server is running on the port ``5500``.

.. |jenkins_build| image:: https://jenkins-ci.tribler.org/job/GH_PlebNet/badge/icon
    :target: https://jenkins-ci.tribler.org/job/GH_PlebNet
    :alt: Build status on Jenkins

.. _Cloudomate: https://github.com/Tribler/cloudomate
.. _Tribler: https://github.com/Tribler/tribler

Future Work
===========

- Gossip learning protocol using IPv8 overlay: enable collective learning by sharing QTable updates with a secure message authentication
- QTable for VPN selection: learn which VPN works the best and which VPS providers ignore DMCA notices and thus do not require VPN
- Market strategy based on deep learning
- Explore additional sources of income: Bitcoin donations, torrent seeding...

