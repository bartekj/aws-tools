aws-tools
=========

.. image:: https://img.shields.io/pypi/v/aws-tools.svg?maxAge=0
    :target: https://pypi.org/project/aws-tools/
    :alt: PyPI

This package provides tools for AWS platform, such as:

-  switching between multiple accounts
-  renewing API access keys

and others.

Getting started
---------------

..

    Prerequisites:

    aws-tools requires gpg (version >= 2.X) to decrypt/encrypt your AWS credentials.


Install necessary packages, and generate a new key pair:

::

    $ sudo apt-get install gpg gpg-agent
    $ gpg --gen-key

..

    This document covers only gpg commands required to run aws-tools! If
    you need to use other gpg parameters, go to gpg documentation.

Installation
~~~~~~~~~~~~

Simply run:

::

    $ pip install --user aws-tools

Configuration
~~~~~~~~~~~~~

AWS Credentials
^^^^^^^^^^^^^^^

In ``~/.aws`` directory create temporary ``env.<environment>.conf`` file
for each AWS environment.

For example, if you have 3 AWS environments: TEST, STAGE and PROD, there
should be 3 config files in ``~/.aws`` directory:

::

    env.test.conf
    env.stage.conf
    env.prod.conf

Edit each file:

.. code:: cfg

    [default]
    aws_access_key_id = <your_environment_specific_access_key_id>
    aws_secret_access_key = <your_environment_specific_secret_access_key>

Encrypt each file with gpg:

::

    $ gpg --encrypt --armor --output env.<environment>.conf.asc -r <your-gpg-user-id-name> env.<environment>.conf

and remove temporary ``env.*.conf`` files!

..

    Run ``gpg -K`` to find out what is your ``<your-gpg-user-id-name>``

SMTP credentials (optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

This step is helpful if you want to send renewed AWS access keys to an
email.

In ``~/.aws`` directory create temporary ``smtp.cfg`` file.

Edit smtp settings:

.. code:: cfg

    smtplogin = <your_full_smtp_login>
    smtppass = <your_password>
    smtphost = <smtp_host>
    smtpport = <smtp_port>

Encrypt config file with gpg:

::

    $ gpg --encrypt --armor --output smtp.cfg.asc -r <your-gpg-user-id-name> smtp.cfg

and remove temporary ``smtp.cfg`` file!

Shell
^^^^^

aws-tools comes with handy bash functions and command completion
feature. Simply add to your ``~/.bashrc``:

.. code:: cfg

    source $HOME/.local/bin/aws_tools_completion.bash 2>/dev/null

You can also display info which AWS access keys you are using. Add to ``$PS1`` variable (usually in ``~/.bashrc``):

.. code:: cfg

    $(__awsenv_ps1 2>/dev/null)

Usage
-----

Examples
~~~~~~~~

Autocompletion:

::

    $ awsenv<TAB><TAB>
    prod stage test

Use TEST access keys:

::

    $ awsenv test

Rotate PROD access keys:

::

    $ awsroll prod

Rotate access keys for all environments:

::

    $ awsroll

Rotate access keys for all environments using gpg agent, and send them to the email:

::

    $ aws-roll-keys.py -a -e all -s <email@domain.org>

Rotate access keys for TEST environment and send info to the email:

::

    $ aws-roll-keys.py -e test -i <email@domain.org>
