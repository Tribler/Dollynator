from VPSBuyer import VPSBuyer
import os
import shutil
from subprocess import call, check_output

class LocalhostBuyer(VPSBuyer):

    def __init__(self):
        """
        Instantiate a new local server by copying the Vagrantfile to a newly created subdirectory
        and starting the server with vagrant.
        """
        self.projectdir = '../'
        self.basedir = os.path.dirname(self.projectdir + '.machines/')
        self.machineprefix = 'machine'

        # Create machines directory
        if not os.path.exists(self.basedir):
            os.mkdir(self.basedir)

        self.counter = 0

    def place_order(self):
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

        # Start server
        returncode = call(['vagrant', 'up'], cwd=machinedir)

        return LocalServer(machinedir)

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
         self.private_key) = self._parse_output(check_output(['vagrant', 'ssh-config'], cwd=machinedir))
        print(self.ip)
        print(self.user)
        print(self.port)
        print(self.private_key)

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

        return (details['HostName'], details['User'], details['Port'], details['IdentityFile'])

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
    provider = LocalhostBuyer()
    server = provider.place_order()

    server.destroy()

