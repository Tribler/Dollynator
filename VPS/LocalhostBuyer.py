from VPSBuyer import VPSBuyer
import os
import shutil
from subprocess import call, check_output
import socket
from threading import Thread
import time

"""

Split into two functional parts:
1. VPSHOST (localmachine) that returns VM info upon request on port 80 and starts a vm
2. LocalhostBuyer that requests the VMinfo by get request on port 80 and does something with that info.

Code below currently is part of 2, but should be moved to 1.

"""

class LocalHoster(object):

    def __init__(self, port = 80, maxservers = 1):
        """
        LocalHoster is a hosting provider for localhost servers.
        """
        self.projectdir = '../'
        self.basedir = os.path.dirname(self.projectdir + '.machines/')
        self.machineprefix = 'machine'

        # Create machines directory
        if not os.path.exists(self.basedir):
            os.mkdir(self.basedir)

        self.counter = 0

        self.servers = []
        self.port = port

        self.stopped = False

        self.maxservers = maxservers


    def create_server(self):
        """
        Create a localserver directory and start the server. 
        :return: Server object containing details for access
        """
        self.counter = self.counter + 1

        # Make machine directory
        machinedir = ''.join((self.basedir, '/', self.machineprefix, str(self.counter)))

        if not os.path.exists(machinedir):
            os.mkdir(machinedir)
        else:
            print('ERROR: localserver should be automatically shut down and remove. If directory still exists, check code or if error occured in vm.')
            raise Exception('Localserver directory was not deleted.')

        # Copy vagrantfile
        shutil.copy(self.projectdir + 'Vagrantfile', machinedir)

        server = LocalServer(machinedir)
        self.servers.append(server)

        return server

    def destroy_all(self):
        '''
        Destroy all created servers.
        '''
        for server in self.servers:
            server.destroy()

    class LocalHosterHandler:
        def handle(self):
            pass

    def start(self):
        '''
        Start the localhosting provider, keep making hosts until maxservers is reached
        '''
        # make socket
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind(('127.0.0.1', self.port))
        serversocket.listen(5)

        # listen to socket and return new socket if request is made.
        while len(self.servers) < self.maxservers:
            # accept connection
            (client, address) = serversocket.accept()

            localserver = self.create_server()

            # asynchroniously start server and reply to request
            handler = AsyncRequestHandler(client, localserver)
            handler.start()

        serversocket.close()

class AsyncRequestHandler(Thread):
    def __init__(self, client, localserver):
        self.client = client
        self.localserver = localserver
        super(AsyncRequestHandler, self).__init__()

    def run(self):
        self.localserver.start()

        with open(self.localserver.private_key, 'r') as f:
            private_key = f.read()

        self.client.sendall('{0}\n{1}\n{2}\n{3}'.format(self.localserver.ip, self.localserver.user, self.localserver.port, private_key).encode())
        self.client.close()


class LocalhostBuyer(VPSBuyer):
    def place_order(self):
        # request server from localhoster
        pass


class LocalServer(object):
    """
    Localserver contains the details to access and destroy a localserver with vagrant.
    """
    def __init__(self, machinedir):
        """
        Initialize a server object
        :param machinedir: Root directory of server files
        """
        self.machinedir = machinedir

        (self.ip,
         self.user,
         self.port,
         self.private_key) = (None, None, None, None)

    def _parse_output(self, output):
        """
        Parse SSH details
        :return: ip, port and private key location
        """
        lines = output.decode('utf-8').split('\n')
        details = dict()
        for line in lines:
            kv = line.split()
            if len(kv) > 1:
                details[kv[0].strip()] = kv[1].strip()

        return (details['HostName'], details['User'], details['Port'], details['IdentityFile'].replace('"',''))

    def start(self):
        '''
        Start server
        '''
        returncode = call(['vagrant', 'up'], cwd=self.machinedir)
        (self.ip,
         self.user,
         self.port,
         self.private_key) = self._parse_output(check_output(['vagrant', 'ssh-config'], cwd=self.machinedir))

    def destroy(self):
        """
        Halt the server and remove server files 
        """

        # Halt machine
        call(['vagrant', 'halt'], cwd=self.machinedir)

        # Destroy machine
        call(['vagrant', 'destroy', '-f'], cwd=self.machinedir)

        # Remove machine directory
        shutil.rmtree(self.machinedir)

if __name__ == '__main__':
    # Example for running localhostingprovider

    # Make a localhoster
    provider = LocalHoster(port=6140, maxservers=1)

    # Start hoster, it will run until all maxservers var is reached
    provider.start()

    # Normally run tests here
    # So it does not start deleting before finished starting
    time.sleep(120)

    # remove all instances made by the hoster after done testing
    provider.destroy_all()






