*******
Plebnet
*******

|jenkins_build|

*A self-replicating autonomous Tribler exit-node*

Documentation
=============
 - The full report regarding this project can be found `here <https://github.com/Tribler/tribler/files/2025931/Bachelor_Project_2018_BotNet.pdf>`_
 - The main issue regarding this project can be found `here <https://github.com/Tribler/tribler/issues/2925>`_

Description
===========
After the first instance is installed on a VPS, plebnet will run Tribler as an exit-node and earn credits,
which will be used to  acquire new VPS instances for next generation plebnet agents. This should eventually create a
community of exit-nodes for Tribler, thus creating a reliable and sufficiently large capacity for anonymous data
transfer through the Tribler network

Initialization
==============
The first instance can be installed by running the downloading the file create-child.sh in Plebnet/plebnet/clone and call:

.. code-block:: none

    PATH/TO/FILE/create-child.sh VPS_IP_ADDRESS ROOT_PASSWORD

This installs all dependencies (Tribler, Electrum, Cloudomate and ofcourse PlebNet).
After installation the "plebnet setup" is called and a cron job is set up to regularly call "plebnet check".

This check function checks whether the agent instance has acquired sufficient funds to buy a new VPS and spawn a new
child instance. If this is the case, the Plebnet agent will execute the previously mentioned steps on the new server and
the community has welcomed a newborn.

.. |jenkins_build| image:: https://jenkins.tribler.org/job/GH_PlebNet/badge/icon
    :target: https://jenkins.tribler.org/job/GH_PlebNet
    :alt: Build status on Jenkins
