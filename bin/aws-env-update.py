#!/usr/bin/env python
import argparse
import getpass
import logging as log
import os
import re
import sys
import gnupg

debug = 0
home = os.environ['HOME']
aws_config_dir = '{}/.aws/'.format(home)
credential_file = '{0}/credentials'.format(aws_config_dir)
env_file = '{0}/.env'.format(aws_config_dir)

def get_args():
    '''This function parses and return arguments passed in'''
    available_envs = list(
        map(lambda file: re.sub(r"env.(.*).conf.asc", r"\1", file),
            filter(lambda file: file.startswith("env"),
                   os.listdir(aws_config_dir))))

    parser = argparse.ArgumentParser(__file__, formatter_class=argparse.RawDescriptionHelpFormatter,
                                    description=('''\
Simple script that will pick up gpg encrypted files from ~/.aws
and save them in the ${HOME}/.aws/credentials file\
Example usage:\n\n\tx1:~$ awsenv test \n'''),
                                    epilog="Copyright (C) 2016 Bart Jakubowski <bartekj@gmail.com>")
    parser.add_argument("-e", "--env", help="environment name", choices=available_envs, required=True)
    parser.add_argument("-a", "--use-agent", action="store_true", help="Use GPG agent")
    parser.add_argument("-x", "--export", action="store_true", help="Print eval-friendly output")
    parser.add_argument("--gpg-binary", help="GPG binary to use")
    parser.add_argument("-d", "--debug", action='store_true', help="Debug mode")
    parser.add_argument('-v', "--version", help="Print version", action='version', version='%(prog)s 1.0')
    args = parser.parse_args()
    return args.env, args.use_agent, args.export, args.gpg_binary, args.debug

def get_passphrase(use_agent=False):
    if use_agent:
        return None
    else:
        return getpass.getpass("Enter the passphrase to decrypt the env file: ")

def main():
    env, use_agent, export, gpg_binary, debug = get_args()

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

    if gpg_binary is not None:
        gpg = gnupg.GPG(use_agent=use_agent, gpgbinary=gpg_binary)
    else:
        gpg = gnupg.GPG(use_agent=use_agent)

    private_keys = gpg.list_keys(True)

    if not private_keys:
        log.error('No private key(s) found! Please check your GPG config')

    stream = open(encrypted_credentials_file, "rb")
    output = gpg.decrypt_file(stream, passphrase=get_passphrase(use_agent))

    if use_agent and output.status != 'decryption ok':
        log.error('Decryption failed, please try again')
        sys.exit(1)
    else:
        while output.status != 'decryption ok':
            log.error('Decryption failed, check your password')
            stream.seek(0)
            output = gpg.decrypt_file(stream, passphrase=get_passphrase(use_agent))

    aws_credentials_patterns = ("aws_access_key_id", "aws_secret_access_key")

    if any(x in str(output) for x in aws_credentials_patterns):
        if not export:
            with open(credential_file, 'w') as credential_out:
                credential_out.write(str(output))
            with open(env_file, 'w') as env_out:
                env_out.write(env)

    else:
        log.error('No AWS credentials in the decrypted file!')

    stream.close()

    if export and output.status == "decryption ok":
        id = re.findall(r"{} = (.*)".format(aws_credentials_patterns[0]), str(output))[0]
        key = re.findall(r"{} = (.*)".format(aws_credentials_patterns[1]), str(output))[0]

        print("export AWS_ENV='{}'".format(env))
        print("export AWS_ACCESS_KEY_ID='{}'".format(id))
        print("export AWS_SECRET_ACCESS_KEY='{}'".format(key))

if __name__ == "__main__":
    main()

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 smarttab
