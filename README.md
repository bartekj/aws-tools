aws-tools
=========
Some aws related scripts

aws-env-update
--------------
Script that helps you switch between multiple AWS accounts in a secure way.

### About
The AWS CLI uses a provider chain to look for AWS credentials in a number of different places, including system or user environment variables and local AWS configuration files.

Exporting variables running python is not that simple, so this script is decrypting AWS credentials to :
```bash
 ~/.aws/credentials
 ```

### Script requirements
* Python libs
  - argparse==1.2.1
  - python-gnupg==0.3.9



* GnuPG trusted key

At the moment script will work when only one key is added to gpg.
```bash
[0.23] 12:23!desktop:~$ gpg --list-secret-keys
/home/user/.gnupg/secring.gpg
------------------------------
pub   4096R/68ED51D1 2016-03-30
uid                  Bartlomiej Jakubowski (natur) <bart@jakubowski.in>
sub   4096R/CEB0FE21 2016-03-30
```
* Encrypted credentials

Put or create files with access credentials and encrypt them with gpg.
```bash
[0.23] 12:23!desktop:~/.aws $ gpg --encrypt --armor --output env.prod.conf.asc -r 'bart@jakubowski.in' env.prod.conf
...
[0.23] 12:23!desktop:~$ tree .aws
     ~/.aws/
       ├── credentials
       ├── env.prod.conf.asc
       ├── env.qa.conf.asc
       └── env.test.conf.asc
```
Put or create files with access credentials and encrypt them with gpg.

* Bash alias

This alias is passing all arguments using a combination of function alias and eval

```bash
function __aws-env-update() {
    eval "$(python ~/bin/aws-env-update.py -e $@)"
}
alias awsenv='__aws-env-update'
```

* Displaying current environment in the console

```bash
function __awsenv_ps1() {
    ps=$(cat $HOME/.aws/.env 2>/dev/null)
    test -n "$ps" && echo "<$ps>"
}
export PS1='\[\e[1;38;5;39m\]$(__git_ps1 "(%s) " 2>/dev/null)$(__awsenv_ps1)\[\e[1;38;5;40m\][ \t ] \[\e[1;38;5;099m\]\H:\[\e[1;38;5;40m\]\w\[\e[1;38;5;099m\]\$ \[\e[0m\]'
```

### Usage

```bash
[0.23] 12:23!desktop:~$ awsenv qa
Enter the passphrase to decrypt the env file:
[0.23] 12:23!desktop:~$
```

aws-roll-keys
-------------
Script that can renew AWS API access keys.

### About

This script can renew API keys for three different environments: test,
qa and prod, or all of them.

It expects encrypted credentials in `$HOME/.aws/env.$ENV.conf.asc` to be
in "AWS credentials" format:
```
[default]
aws_access_key_id = <ID>
aws_secret_access_key = <KEY>
```
### Script requirements
* Python libs
  - boto3==1.4.0

### SMTP options (-s and -i)
##### Create smtp configuration file
In the same directory as `aws-roll.keys.py`.

smtp.cfg (temporary file):

    smtplogin = full_smtp_login
    smtppass = password
    smtphost = smtp_host
    smtpport = smtp_port

Ecrypt it:

    gpg --encrypt --armor --output smtp.cfg.asc -r <your-gpg-user-id-name> smtp.cfg

And remove temporary file

##### Sending email with rolled keys (-s)
In case you need to use rolled keys on the other computer, you can send them via email, as attachments. Just add `-s youremail@domain.com`.

    aws-roll-keys.py -e all -s youremail@domain.com

##### Sending confirmation that keys have been changed (-i)
In case you need to send confirmation (without keys) about rotating to the others, add `-i email@domain.com`.

    aws-roll-keys.py -e all -i email@domain.com


### Usage

```bash
$ ./aws-roll-keys.py -e test
Enter the passphrase to decrypt the env file:
Rolled key for env test: AccessKeyId=****************SWOUQ; CreateDate=2016-09-12 07:42:59.135000+00:00
```

or create alias:

    alias awsroll='aws-roll-keys.py -a -e all -s youremail@domain.com -i email@domain.com'

If you want to keep rotation fully automated, you may be tempted to add it into cron;)
