#!/usr/bin/env python
import argparse
import getpass
import glob
import logging as log
import os
import sys
import re

import gnupg

debug = 0
home = os.environ['HOME']
aws_config_dir = '{}/.aws/'.format(home)
credential_file = '{0}/credentials'.format(aws_config_dir)

def get_args():
    '''This function parses and return arguments passed in'''
    parser = argparse.ArgumentParser(__file__, formatter_class=argparse.RawDescriptionHelpFormatter,
                                    description=('''\
Simple script that will pick up gpg encrypted files from ~/.aws
and save them in the ${HOME}/.aws/credentials file\
Example usage:\n\n\tx1:~$ awsenv test \n'''),
                                    epilog="Copyright (C) 2016 Bart Jakubowski <bartekj@gmail.com>")
    parser.add_argument("-e", "--env", help="environment name", choices=['test', 'qa', 'prod'], required=True)
    parser.add_argument("-x", "--export", action="store_true", help="Print eval-friendly output")
    parser.add_argument("-d", "--debug", action='store_true', help="Debug mode")
    parser.add_argument('-v', "--version", help="Print version", action='version', version='%(prog)s 1.0')
    args = parser.parse_args()
    env = args.env
    debug = args.debug
    export = args.export
    return env, debug, export

def main():
    env, debug, export = get_args()

    if debug:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
        log.info("Debug output.")
    else:
        log.basicConfig(format="%(levelname)s: %(message)s")

    encrypted_credentials_file = os.path.join(os.sep, aws_config_dir, 'env.{0}.conf.asc'.format(env))

    log.info('''Variables dump:\n\tenv : {0}\n\thome : {1}\n\taws_config_dir : {2}\n\tencrypted_credentials_file : {3}
    \tcredential_file : {4}'''.format(env, home, aws_config_dir, encrypted_credentials_file, credential_file))

    if not encrypted_credentials_file:
        log.error('''File with encrypted credentials for environment: {0} dont exists!.\n
                 Please encrypt your aws keys to file: \n{1}env.{0}.conf.asc'''.format(env, aws_config_dir))

    gpg = gnupg.GPG(gnupghome='{}/.gnupg/'.format(home))
    private_keys = gpg.list_keys(True)
    if not private_keys:
        log.error('No private key(s) found! Please check your GPG config')
    stream = open(encrypted_credentials_file, "rb")
    phrase = getpass.getpass("Enter the passphrase to decrypt the env file: ")
    output = gpg.decrypt_file(stream, passphrase=phrase)
    aws_credentials_patterns = ("aws_access_key_id", "aws_secret_access_key")
    if output.status == 'decryption failed':
        log.error('Decryption failed, check your password')
    elif output.status == 'decryption ok':
        if any(x in str(output) for x in aws_credentials_patterns):
            try:
                os.remove(credential_file)
            except OSError:
                pass
            with open(credential_file, 'w') as outfile:
                outfile.write(str(output))
        else:
            log.error('No AWS credentials in the decrypted file!')
    else:
        log.error('Unknown error, use --debug to troubleshoot')
    stream.close()

    if export and output.status == "decryption ok":
        id = re.findall(r"{} = (.*)".format(aws_credentials_patterns[0]), str(output))[0]
        key = re.findall(r"{} = (.*)".format(aws_credentials_patterns[1]), str(output))[0]
        print("export AWS_ACCESS_KEY_ID='{}'".format(id))
        print("export AWS_SECRET_ACCESS_KEY='{}'".format(key))


if __name__ == "__main__":
    main()

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 smarttab
