aws-tools
=========

.. image:: https://img.shields.io/pypi/v/aws-tools.svg?maxAge=0
    :target: https://pypi.org/project/aws-tools/
    :alt: PyPI

This package provides tools for AWS platform, such as:

-  switching between multiple accounts
-  renewing API access keys

and others.

The main reason why aws-tools came to be, was using `awscli`_ with different access keys in the secure and easy way.

How it works
------------

Switching between AWS accounts:

::

    $ awsenv test
    <test> $ aws s3 ls
    ...list of S3 objects on TEST environment...

    ### Explanation:
    ### <test> $ env | grep AWS
    ### AWS_SECRET_ACCESS_KEY=w0bM0rucARITPOUpcyAaX3iI9lGjJo7g8UUCUxIv
    ### AWS_ACCESS_KEY_ID=AKIAJPVK7VGH6CBZT5EQ
    ### AWS_ENV=test

    <test> $ awsenv prod
    <prod> $ aws s3 ls
    ...list of S3 objects on PROD environment...

    ### Explanation:
    ### <prod> $ env | grep AWS
    ### AWS_SECRET_ACCESS_KEY=P8crbSIvQ/Au0jfnW8XER9eJKxpQdYqpRVz5QxKo
    ### AWS_ACCESS_KEY_ID=AKIAJ4F26CMBPI1HF7MQ
    ### AWS_ENV=prod

Renewing AWS API access keys:

::

    $ awsenv prod

    ### Explanation:
    ### <prod> $ env | grep AWS
    ### AWS_SECRET_ACCESS_KEY=P8crbSIvQ/Au0jfnW8XER9eJKxpQdYqpRVz5QxKo
    ### AWS_ACCESS_KEY_ID=AKIAJ4F26CMBPI1HF7MQ
    ### AWS_ENV=prod

    <prod> $ awsroll prod
    Rolled key for env prod: AccessKeyId=****************ZKQFQ; CreateDate=2018-11-14 13:10:04+00:00
    <prod> $ awsenv prod

    ### Explanation:
    ### <prod> $ env | grep AWS
    ### AWS_SECRET_ACCESS_KEY=napb9J2RKzsSiTIjLRavN09qIfFzrMo7846zr2ou
    ### AWS_ACCESS_KEY_ID=AKIAJTGB6EFV7F4ZKQFQ
    ### AWS_ENV=prod

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

Configure your region using `awscli`_ if you haven't done that yet:

::

    $ aws configure
    AWS Access Key ID [None]:
    AWS Secret Access Key [None]:
    Default region name [None]: eu-west-1
    Default output format [None]:

..

    Do not provide any keys here!

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

Shell
^^^^^

aws-tools comes with handy command completion and bash prompt features.
Simply add to your ``~/.bashrc``:

.. code:: cfg

    source $HOME/.local/bin/aws_tools_completion.bash 2>/dev/null
    export PS1="\$(__awsenv_ps1 2>/dev/null)${PS1}"

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

Unset AWS access keys for current shell:

::

    $ awsenv unset

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




.. _awscli: https://pypi.org/project/awscli/
