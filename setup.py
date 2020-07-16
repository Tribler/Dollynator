
from codecs import open
from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='plebnet',

    version='0.3.0',

    description='Working class botnet',
    long_description=long_description,

    url='https://github.com/GioAc96/Dollynator',

    author='Dollynator',
    author_email='authentic8989@gmail.com',

    license='LGPLv3',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: System :: Installation/Setup',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',

        'Operating System :: POSIX :: Linux',
    ],

    keywords='botnet',

    packages=find_packages(exclude=['docs']) + ['plebnet.twisted.plugins'],

    install_requires=[
        'twisted',
        'requests',
        'names',
        'faker',
        'jsonpickle',
        'rsa',
        'cryptography'
    ],

    extras_require={
        'dev': [],
        'test': ['mock', 'pytest', 'responses'],
    },

    package_data={
        'plebnet': [],
    },

    entry_points={
        'console_scripts': [
            'plebnet=plebnet.cmdline:execute',
        ],
    },
)

