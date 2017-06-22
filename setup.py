from codecs import open
from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='plebnet',

    version='0.1.0',

    description='Working class botnet',
    long_description=long_description,

    url='https://github.com/rjwvandenberg/PlebNet',

    author='PlebNet',
    author_email='plebnet@heijligers.me',

    license='LGPLv3',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: System :: Installation/Setup',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',

        'Operating System :: POSIX :: Linux',
    ],

    keywords='botnet',

    packages=find_packages(exclude=['docs']),

    install_requires=['requests', 'names', 'cloudomate', 'faker', 'twython'],

    extras_require={
        'dev': [],
        'test': [],
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
