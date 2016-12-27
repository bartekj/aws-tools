aws-tools
=========

.. image:: https://img.shields.io/pypi/v/aws-tools.svg?maxAge=0
    :target: https://pypi.python.org/pypi/aws-tools/
    :alt: PyPI

This package provides scripts for:

* switching between multiple AWS accounts
* renewing AWS API access keys

------------
Installation
------------

The easiest way to install aws-tools is to use `pip`:

in your home directory::

    pip install --user aws-tools

inside a ``virtualenv``::

    pip install aws-tools

or system-wide::

    sudo pip install aws-tools

This will install aws-tools package as well as all dependencies

---------------
Getting started
---------------

^^^^^^^^^^^^^^^^^
AWS configuration
^^^^^^^^^^^^^^^^^

Before using aws-tools you have to configure your AWS environments and credentials::

    $ cat .aws/env.test.conf
    [default]
    aws_access_key_id = <your_access_key>
    aws_secret_access_key = <your_secret_access_key_id>

The same goes for the other environments, for example: stage and production.

Encrypt all of the files with gpg::

    gpg --encrypt --armor --output env.test.conf.asc -r <your-gpg-user-id-name> env.test.conf
    gpg --encrypt --armor --output env.stage.conf.asc -r <your-gpg-user-id-name> env.stage.conf
    gpg --encrypt --armor --output env.production.conf.asc -r <your-gpg-user-id-name> env.production.conf

and remove temporary files (env*conf).

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
SMTP configuration (-s and -i) (optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In the ``.aws`` directory:

smtp.cfg (temporary file)::

    smtplogin = <full_smtp_login>
    smtppass = <password>
    smtphost = <smtp_host>
    smtpport = <smtp_port>

Ecrypt it::

    gpg --encrypt --armor --output smtp.cfg.asc -r <your-gpg-user-id-name> smtp.cfg

And remove temporary file (smtp.cfg)

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Shell configuration (optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Add to ``.bashrc``.

* Command Completion

The aws-tools comes with a very useful bash command completion feature.
This feature isn't automatically installed, so you need to enable it yourself.
Simply add to your ``.bashrc``:

if you have installed aws-tools in home directory::

    source $HOME/.local/bin/aws_tools_completion.bash

if you have installed aws-tools system-wide::

    source /usr/local/bin/aws_tools_completion.bash

* Functions

It is also handy to add some bash functions::

    function awsenv() {
        __aws_env_update -x -a -e $1
    }

    function awsroll() {
        __aws_roll_keys -a -s <youremail@domain.com> -i <groupemail@domain.com> -e "${1:-all}"
    }

* Displaying current account in your shell

add to $PS1 variable::

    $(__awsenv_ps1)

-----
Usage
-----

^^^^^^^^
Examples
^^^^^^^^

Switch to ``test`` account and write credentials to ``.aws/credentials`` file::

    $ aws-env-update.py -a -e test

Switch to ``test`` account using shell variables::

    $ eval $(aws-env-update.py -a -e test -x)

The same, but after sourcing ``aws_tools_completion.bash``::

    $ awsenv test

Rotating AWS API keys for ``stage`` account::

    $ aws-roll-keys.py -a -e stage

Rotating AWS API keys for ``production`` account and sending the new keys to you::

    $ aws-roll-keys.py -a -e production -s <youremail@domain.com>

Rotating AWS API keys for all of environments and sending confirmation to the group::

    $ aws-roll-keys.py -a -e all -i <groupemail@domain.com>
