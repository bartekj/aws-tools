#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='aws-tools',
    version='1.0',
    description='Switching between multiple AWS accounts and rolling keys',
    url='https://github.com/bartekj/aws-tools',
    scripts=[
        'bin/aws-env-update.py',
        'bin/aws-roll-keys.py',
        'bin/aws_tools_completion.bash',
    ],
    include_package_data=True,
    packages=find_packages('.', exclude=['tests*', 'docs*']),
    install_requires=[
        'argparse',
        'boto3',
        'python-gnupg>=0.3.9',
    ],
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
)
