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
The choice of next VPS is dictated by QTable (Q-Learning).

**What is Q-Learning?**

Q-Learning is a reinforcement learning technique. The aim of this technique
is to learn how to act in the environment.
The update values in Q-Table is as follows:

.. image:: http://latex.codecogs.com/gif.latex?Q_%7Bnew%7D%28s_%7Bt%7D%2Ca_%7Bt%7D%29%5Cleftarrow%20%281-lr%29&plus;lr*%28reward%20&plus;discount%20*%5Cmax_%7Ba%7D%28s_%7Bt&plus;1%7D%2Ca%29%29

``discount`` is a discount factor (how important are gains of future steps

``lr`` is a learning rate

``st`` is a current state

``s(t+1)`` is a next step

**Reinforcement Mappings**

We define few mappings which are used in Reinforcement Learning jargon:

- ``states`` - VPS offers

- ``environment`` – transition matrix between states. This kind of dictates what reinforcement we will get by choosing certain transition. Initially all 0s.

- ``current_state`` – current VPS option

**Initial values**

Initial values for QTable are calculated according to the formula bellow:

.. image:: http://latex.codecogs.com/gif.latex?%5Cfrac%7B1%7D%7Bprice%5E3%7D*%20bandwidth


**How does it works in Dollybot?**

In Dollybot we use form of Q-Learning, as we are not fully aware of the environment and our reinforcements for each state, we try to learn them on the go.

Environment is getting updated by each try of replication:

- when node manages to buy new option and replicate environment is updated positively (all transitions leading to ``current_state``)

- when nodes fails to buy option environment is getting updated negatively (transition between ``current_state`` and chosen failed state)

After updating the environment values qtables are recalculated one more time to find action maximizing our possible gains for each state.

**What is passed to the child?**

- his state (provider name + option name)

- name (to have some id)

- tree of replications

- providers_offers (all VPSs offer for all providers)

- current qtable

**Final remarks about RL**

Currently VPSs are chosen using QTable , VPNs not.

To choose option from QTable we use exponential distribution with lambda converging decreasingly to 1. As lambda is changing with number of replications process seems to be similar to **simulated annealing**.

The current version is using simple formula to choose which kth best option to choose:

.. image:: http://latex.codecogs.com/gif.latex?%5Cleft%20%5Clfloor%201%20-%20%5Cfrac%7B1%7D%7Bno%5C_replications%20&plus;%203%7D%20%5Cright%20%5Crfloor

Market Strategies
=================

Plebnet has different options market strategies, they can be configured in the configuration file ``~/.config/plebnet_setup.cfg``, under the strategies section. The strategy to be configured can be changed in the name configuration (possible options are ``last_day_sell``, ``constant_sell`` and ``simple_moving_average``), if it's not configured, last_day_sell will by applied by default.

There are two main types of strategies to sell the gained reputation for bitcoin: 

- Blind Strategies focus only on replication independently of the current value of reputation.
- Orderbook-based Strategies focus on getting the most value of the gained reputation, using the history of transactions and having endless options of possible algorithms to use to decide when to sell and when to hold on to the reputation.

Blind Strategies
----------------

Plebnet currently has two options for Blind Strategies: LastDaySell and ConstantSell. Both of the strategies try to obtain enough bitcoin to lease a certain amount of VPS to replicate to. This number can be configured in the ``vps_count`` parameter in the strategy section of the configuration file, if it is not configured, 1 will be used by default.

LastDaySell waits until there is one day left until the expiration of the current VPS lease and then places an order on the market selling all available reputation for the amount of bitcoin needed for the configured number of replications. This order is updated hourly with the new income.

ConstantSell, as soon as it is first called, places an order on the market selling all available reputation for the amount of bitcoin needed for the configured number of replications. This order is updated hourly with the new income.

Orderbok-based Strategies
-------------------------

Plebnet has one Orderbook-based Strategy: SimpleMovingAverage. This strategy tries to get the most of the market by evaluating the current price (the price of the last transaction) against a simple moving average of 30 periods, using days as periods.
This strategy accumulates reputation while the market is not favorable to selling - when the current price is lower than the moving average. It will accumulate up until a maximum of 3 days worth of reputation. When this maximum is reached, even if the market is not favorable, reputation is sold at production rate - the bot waits until the end of the 4th day of accumulation and then places an order selling a full day's worth of reputation.
If the market is favorable - the current price is higher than the moving average - it will evaluate how much higher it is. To do this the strategy uses the standard deviation of the moving average. If it is not above the moving average plus twice the standard deviation, only a full day's worth of reputation is sold. If it is between this value and the moving plus three times the standard deviation, it will sell two days' worth of reputation, if it is higher than the moving average plus three times the standard deviation it will sell three days' worth of reputation.

This strategy doesn't assume market liquidity - even though all placed orders are market orders (orders placed at the last price), it confirms if the last token sell was completely fulfilled, only partially or not at all and takes that into account for the next iteration. 

If Plebnet could not gather any history of market transactions, this strategy will replace itself with LastDaySell. 

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
- Market strategies based on other financial analysis' (i.e: other moving averages may be interesting)
- Market strategy based on deep learning
- Explore additional sources of income: Bitcoin donations, torrent seeding...

