#!/usr/bin/env python
import argparse
import getpass
import glob
import logging as log
import os
import sys

import gnupg


def main():
    parser = argparse.ArgumentParser(__file__, formatter_class=argparse.RawDescriptionHelpFormatter,
                                    description=('''\
Simple script that will pick up gpg encrypted files from ~/.aws
and save them in the /home/{$username}/.aws/credentials file\
Example usage:\n\n\tx1:~$ awsenv test \n'''),
                                    epilog="Copyright (C) 2016 Bart Jakubowski <bartekj@gmail.com>")
    parser.add_argument("-e", "--env", help="environment name", choices=['test', 'qa', 'prod'], required=True)
    parser.add_argument("-d", "--debug", action='store_true', help="Debug mode")
    parser.add_argument('-v', "--version", help="Print version", action='version', version='%(prog)s 1.0')
    args = parser.parse_args()

    if args.debug:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
        log.info("Debug output.")
    else:
        log.basicConfig(format="%(levelname)s: %(message)s")

    ENV = args.env
    USER = os.environ['USER']
    AWS_CONFIG_DIR = '/home/{0}/.aws/'.format(USER)
    ENCRYPTED_CREDENTIALS = glob.glob(AWS_CONFIG_DIR + "env." + ENV + ".conf.asc")
    CREDENTIALS = '{0}/credentials'.format(AWS_CONFIG_DIR)

    log.info('''Variables dump:\n\tENV : {0}\n\tUSER : {1}\n\tAWS_CONFIG_DIR : {2}\n\tENCRYPTED_CREDENTIALS : {3}
    \tCREDENTIALS : {4}'''.format(ENV, USER, AWS_CONFIG_DIR, ENCRYPTED_CREDENTIALS, CREDENTIALS))

    if not ENCRYPTED_CREDENTIALS:
        log.error('''File with encrypted credentials for environment: {0} dont exists!.\n
                 Please encrypt your aws keys to file: \n{1}env.{0}.conf.asc'''.format(ENV, AWS_CONFIG_DIR))

    gpg = gnupg.GPG(gnupghome='/home/{0}/.gnupg/'.format(USER))
    private_keys = gpg.list_keys(True)
    if not private_keys:
        log.error('No private key(s) found! Please check your GPG config')
    phrase = getpass.getpass("Enter the passphrase to decrypt the env file: ")
    stream = open(ENCRYPTED_CREDENTIALS[0], "rb")
    output = gpg.decrypt_file(stream, passphrase=phrase)
    aws_credentials_patterns = ("aws_access_key_id", "aws_secret_access_key")
    if output.status == 'decryption failed':
        log.error('Decryption failed, check your password')
    elif output.status == 'decryption ok':
        if any(x in str(output) for x in aws_credentials_patterns):
            try:
                os.remove(CREDENTIALS)
            except OSError:
                pass
            credentials_file = open(CREDENTIALS, 'w')
            credentials_file.write(str(output))
            credentials_file.close()
        else:
            log.error('No AWS credentials in the decrypted file!')
    else:
        log.error('Unknown error, use --debug to troubleshoot')
    stream.close()

if __name__ == "__main__":
    main()

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 smarttab
