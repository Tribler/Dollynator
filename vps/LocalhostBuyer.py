from VPSBuyer import VPSBuyer
import os
import shutil
from subprocess import call, check_output
import socket
from threading import Thread
import time

IP = '127.0.0.1'
PORT = 6140

class LocalhostBuyer(VPSBuyer):
    def register(self):
        return True

    def place_order(self):
        # request server from localhoster
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.connect((IP, PORT))

        details = connection.receive().decode('utf-8').split('\n')
        ip = details[0]
        user = details[1]
        port = details[2]
        private_key = '\n'.join(details[3:])

        print(ip)
        print(user)
        print(port)
        print(private_key)

        connection.close()


class LocalHoster(object):
    '''
    LocalHoster opens a socket and provides fresh VM details to a maximum of maxservers.
    '''

    def __init__(self, port = PORT, maxservers = 1, provider = 'virtualbox'):
        """
        Initialize a LocalHoster object. Port refers the the port it accepts connections on
        and maxservers is the maximum number of virtual machines it is allowed to start.
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
        self.provider = provider


    def create_server(self):
        """
        Create a localserver directory and return the server object. 
        :return: Server object containing details for access
        """
        self.counter = self.counter + 1

        # Make machine directory
        machinedir = ''.join((self.basedir, '/', self.machineprefix, str(self.counter)))

        if not os.path.exists(machinedir):
            os.mkdir(machinedir)
        else:
            print('ERROR: localserver should be automatically shut down and removed. If directory still exists, check code or if error occured in vm.')
            raise Exception('Localserver directory was not deleted.')

        # Copy vagrantfile
        if self.provider == 'virtualbox':
            shutil.copy(self.projectdir + 'Vagrantfile', machinedir)
        elif self.provider == 'docker':
            shutil.copy(self.projectdir + 'Vagrantfile_docker', machinedir + '/Vagrantfile')

        server = LocalServer(machinedir)
        self.servers.append(server)

        return server

    def destroy_all(self):
        '''
        Destroy all created servers.
        '''
        for server in self.servers:
            server.destroy()

    def start(self):
        '''
        Start the localhosting provider, keep making hosts until maxservers is reached
        '''
        # make socket
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind((IP, self.port))
        serversocket.listen(5)
        try:
            # listen to socket and return new socket if request is made.
            while len(self.servers) < self.maxservers:
                # accept connection
                (client, address) = serversocket.accept()

                localserver = self.create_server()

                # asynchroniously start server and reply to request
                handler = AsyncRequestHandler(client, localserver)
                handler.start()
        except:
            pass
        finally:
            serversocket.close()

class AsyncRequestHandler(Thread):
    '''
    Handle server start request asynchronously, since it takes some time to start a new VM.
    '''
    def __init__(self, client, localserver):
        self.client = client
        self.localserver = localserver
        super(AsyncRequestHandler, self).__init__()

    def run(self):
        '''
        Start the server, pass details to connected client and close connection.
        '''
        self.localserver.start()

        with open(self.localserver.private_key, 'r') as f:
            private_key = f.read()

        self.client.sendall('{0}\n{1}\n{2}\n{3}'.format(self.localserver.ip, self.localserver.user, self.localserver.port, private_key).encode())
        self.client.close()


class LocalServer(object):
    """
    Localserver contains the details to access, start and destroy a localserver with vagrant.
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
        Start server and save access details.
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
    provider = LocalHoster(maxservers=1, provider='virtualbox')

    # Start hoster, it will run until all maxservers var is reached
    provider.start()

    # Normally run tests here
    # So it does not start deleting before finished starting
    time.sleep(120)

    # remove all instances made by the hoster after done testing
    provider.destroy_all()






