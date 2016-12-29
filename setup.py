#!/usr/bin/env python

import subprocess
from setuptools import setup, find_packages

try:
    version_git = subprocess.check_output(['git', 'describe', '--abbrev=0']).strip()
    if type(version_git) is bytes:
        version_git = version_git.decode('ascii')
except:
    with open('version.py', 'r') as fh:
        version_git = open('version.py').read().split('=')[-1].strip()
        if type(version_git) is bytes:
            version_git = version_git.decode('ascii')

with open('version.py', 'w') as fh:
    fh.write("# This file is managed by git\n" + "__version__ = " + version_git)

with open('requirements.txt', 'r') as fh:
    required = fh.read().splitlines()

setup(
    name='aws-tools',
    version=version_git,
    description='Switching between multiple AWS accounts & renewing API access keys',
    long_description=open('README.rst').read(),
    license='MIT',
    url='https://github.com/bartekj/aws-tools',
    keywords='aws key keys',
    packages=find_packages(),
    scripts=[
        'bin/aws-env-update.py',
        'bin/aws-roll-keys.py',
        'bin/aws_tools_completion.bash',
    ],
    install_requires=required,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
)
