aws-tools
=========
Some aws related scripts

aws-env-update
--------------
Script that helps you switch between multiple AWS accounts in a secure way.

##### About
The AWS CLI uses a provider chain to look for AWS credentials in a number of different places, including system or user environment variables and local AWS configuration files.

Exporting variables running python is not that simple, so this script is decrypting AWS credentials to :
```bash
 ~/.aws/credentials
 ```

##### Script requirements
* Python libs
  - argparse==1.2.1
  - python-gnupg==0.3.8



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
...
function __aws-env-update() {
    eval "$(python ~/bin/aws-env-update.py -e $@)"
}
alias awsenv='__aws-env-update'
...
```
##### Usage

```bash
[0.23] 12:23!desktop:~$ awsenv qa
Enter the passphrase to decrypt the env file: 
[0.23] 12:23!desktop:~$
```
