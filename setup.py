#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='aws-tools',
    version='1.0.2',
    description='Switching between multiple AWS accounts & renewing API access keys',
    license='MIT',
    url='https://github.com/bartekj/aws-tools',
    keywords='aws key keys',
    packages=find_packages(),
    scripts=[
        'bin/aws-env-update.py',
        'bin/aws-roll-keys.py',
        'bin/aws_tools_completion.bash',
    ],
    install_requires=[
        'argparse',
        'boto3',
        'python-gnupg>=0.3.9',
    ],
    classifiers=(
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
)
