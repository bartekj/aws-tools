#!/usr/bin/env python
import argparse
import os
import re
import gnupg
import logging
import getpass
import boto3

KEY_ID = "aws_access_key_id"
ACCESS_KEY = "aws_secret_access_key"

CREDENTIALS_FILE_TPL = """
[default]
aws_access_key_id = {id}
aws_secret_access_key = {key}
"""

home = os.environ["HOME"]
aws_config_dir = "{}/.aws/".format(home)


def get_current_key(env, file_path, gpg, phrase):
    private_keys = gpg.list_keys(True)
    id, key = [None, None]
    if not private_keys:
        logging.error("No private key(s) found! Please check your GPG config")
        return [None, None]
    try:
        with open(file_path) as file:
            decrypted = gpg.decrypt_file(file, passphrase=phrase)
            if decrypted.status == "decryption failed":
                logging.error("Unable to decrypt {}".format(file_path))
                return [None, None]

            id = re.findall(r"{} = (.*)".format(KEY_ID), str(decrypted))[0]
            key = re.findall(r"{} = (.*)".format(ACCESS_KEY), str(decrypted))[0]
    except IOError:
        logging.warning("File for env {} not found. Skipping.".format(env))

    return [id, key]


def main():
    parser = argparse.ArgumentParser(
        description="Rolls AWS IAM Access Keys for all or specified env(s)",
        epilog="Copyright (C) 2016 Karolis Labrencis <karolis@labrencis.lt>")
    parser.add_argument("-e", "--env", help="environment name", required=True,
                        choices=["test", "qa", "prod", "all"])
    parser.add_argument("-d", "--debug", action="store_true", help="Debug mode")
    parser.add_argument("-v", "--version", help="Print version", action="version",
                        version="%(prog)s 1.0")
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(format=logging.BASIC_FORMAT, level=logging.DEBUG)
        logging.info("Debug output.")

    if args.env == "all":
        args.env = ["test", "qa", "prod"]
    else:
        args.env = [args.env]

    gpg = gnupg.GPG()
    phrase = getpass.getpass("Please enter passphrase for decrypting env files: ")
    for env in args.env:
        file_path = os.path.join(os.sep, aws_config_dir, "env.{0}.conf.asc".format(env))
        key_id, access_key = get_current_key(env, file_path, gpg, phrase)

        if key_id is None:
            logging.warning("Skipping environment '{}'".format(env))
            continue

        client = boto3.client("iam", aws_access_key_id=key_id, aws_secret_access_key=access_key)
        current_key_id = \
            client.list_access_keys()["AccessKeyMetadata"][0]["AccessKeyId"]
        resp = client.create_access_key()
        new_id = resp["AccessKey"]["AccessKeyId"]
        new_key = resp["AccessKey"]["SecretAccessKey"]

        contents = CREDENTIALS_FILE_TPL.format(id=new_id, key=new_key)

        private_key = gpg.list_keys(True)
        encrypted = gpg.encrypt(contents, private_key[0]["uids"][0])
        with open(file_path, "w") as out:
            out.write(str(encrypted))

        client.delete_access_key(AccessKeyId=current_key_id)

        print("Rolled key for env {}: AccessKeyId={}; CreateDate={}".format(
            env, resp["AccessKey"]["AccessKeyId"], resp["AccessKey"]["CreateDate"]
        ))


if __name__ == "__main__":
    main()

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 smarttab
