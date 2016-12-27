#!/usr/bin/env python

import argparse
import os
import re
import sys
import gnupg
import logging
import getpass
import boto3
import smtplib
import datetime
from datetime import timedelta
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


KEY_ID = "aws_access_key_id"
ACCESS_KEY = "aws_secret_access_key"

CREDENTIALS_FILE_TPL = """
[default]
aws_access_key_id = {id}
aws_secret_access_key = {key}
"""

home = os.environ["HOME"]
aws_config_dir = "{}/.aws/".format(home)

today = datetime.date.today()
future = today + datetime.timedelta(days=7)

def get_current_key(env, file_path, gpg, phrase):
    private_keys = gpg.list_keys(True)
    id, key = [None, None]
    if not private_keys:
        logging.error("No private key(s) found! Please check your GPG config")
        return [None, None]
    try:
        with open(file_path, 'rb') as file:
            decrypted = gpg.decrypt_file(file, passphrase=phrase)
            if decrypted.status != "decryption ok":
                logging.error("Unable to decrypt {}".format(file_path))
                return [None, None]

            id = re.findall(r"{} = (.*)".format(KEY_ID), str(decrypted))[0]
            key = re.findall(r"{} = (.*)".format(ACCESS_KEY), str(decrypted))[0]
    except IOError:
        logging.warning("File for env {} not found. Skipping.".format(env))

    return [id, key]

def get_passphrase(use_agent=False):
    if use_agent:
        return None
    else:
        return getpass.getpass("Please enter passphrase for decrypting env files: ")

def get_smtp_conf(smtpconf, gpg, phrase):
    private_keys = gpg.list_keys(True)
    LOGIN, PASS, HOST, PORT, = [None, None, None, None]
    if not private_keys:
        logging.error("No private key(s) found! Please check your GPG config")
        return [None, None, None, None]
    try:
        with open(smtpconf, 'rb') as file:
            decrypted = gpg.decrypt_file(file, passphrase=phrase)
            if decrypted.status != "decryption ok":
                logging.error("Unable to decrypt {}".format(smtpconf))
                return [None, None, None, None, None, None]

            LOGIN = re.findall(r"{} = (.*)".format("smtplogin"), str(decrypted))[0]
            PASS = re.findall(r"{} = (.*)".format("smtppass"), str(decrypted))[0]
            HOST = re.findall(r"{} = (.*)".format("smtphost"), str(decrypted))[0]
            PORT = re.findall(r"{} = (.*)".format("smtpport"), str(decrypted))[0]
    except IOError:
        logging.error("Can't open {0}".format(smtpconf))
        sys.exit(1)

    return [LOGIN, PASS, HOST, PORT]

def send(srv, sendto, data):
    try:
        server = smtplib.SMTP(srv[2], srv[3])
        server.set_debuglevel(False)
        server.ehlo()
        if server.has_extn('STARTTLS'):
            server.starttls()
            server.ehlo()
        server.login(srv[0], srv[1])
        server.sendmail(srv[0], sendto, data)
        server.quit()
        print("Sent to {0}".format(sendto))
    except Exception as exc:
        logging.error("Can't send email: {0}".format(exc))
        sys.exit(1)

def main():
    available_envs = list(
        map(lambda file: re.sub(r"env.(.*).conf.asc", r"\1", file),
            filter(lambda file: file.startswith("env"),
                   os.listdir(aws_config_dir))))
    parser = argparse.ArgumentParser(
        description="Rolls AWS IAM Access Keys for all or specified env(s)",
        epilog="Copyright (C) 2016 Karolis Labrencis <karolis@labrencis.lt>")
    parser.add_argument("-e", "--env", help="environment name", required=True,
                        choices=available_envs + ["all"])
    parser.add_argument("-s", "--send", help="Send an email with new keys to",
                        action="store", dest="sendkeysto")
    parser.add_argument("-i", "--info", help="Send info about rotation to",
                        action="store", dest="sendinfoto")
    parser.add_argument("-a", "--use-agent", action="store_true", help="Use GPG agent")
    parser.add_argument("--gpg-binary", help="GPG binary to use")
    parser.add_argument("-d", "--debug", action="store_true", help="Debug mode")
    parser.add_argument("-v", "--version", help="Print version", action="version",
                        version="%(prog)s 1.0")
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(format=logging.BASIC_FORMAT, level=logging.DEBUG)
        logging.info("Debug output.")

    if args.env == "all":
        args.env = available_envs
    else:
        args.env = [args.env]

    if args.gpg_binary is not None:
        gpg = gnupg.GPG(use_agent=args.use_agent, gpgbinary=args.gpg_binary)
    else:
        gpg = gnupg.GPG(use_agent=args.use_agent)
    phrase = get_passphrase(args.use_agent)

    msgkeys = MIMEMultipart()
    envs = ""
    msgbody = ""

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

        msgbody += "Rolled key for env {}: AccessKeyId={}; CreateDate={}\n".format(
            env, "*" * 16 + resp["AccessKey"]["AccessKeyId"][-5:],
            resp["AccessKey"]["CreateDate"]
        )

        if args.sendkeysto:
            with open(file_path, "rb") as attach:
                part1 = MIMEApplication(attach.read(), Name="env.{0}.conf.asc".format(env))
                part1["Content-Disposition"] = 'attachment; filename={}'.format(
                    "env.{0}.conf.asc".format(env))
                msgkeys.attach(part1)
                envs += " {0}".format(env)

    print(msgbody)
    vars = dict()

    if args.sendkeysto or args.sendinfoto:
        smtpconf = "{}/smtp.cfg.asc".format(aws_config_dir)
        srv = get_smtp_conf(smtpconf, gpg, phrase)

    if args.sendkeysto:
        msgkeys["To"] = args.sendkeysto
        msgkeys["From"] = srv[0]
        msgkeys["Subject"] = "AWS keys: {}".format(envs)

        send(srv, args.sendkeysto, msgkeys.as_string())

    if args.sendinfoto:
        msginfo = MIMEText(msgbody, "plain", "utf-8")
        msginfo["To"] = args.sendinfoto
        msginfo["From"] = srv[0]
        msginfo["Subject"] = "AWS weekly key(s) rotation: {0}-{1}".format(
            today.strftime("%Y%m%d"), future.strftime("%Y%m%d"))

        send(srv, args.sendinfoto, msginfo.as_string())


if __name__ == "__main__":
    main()

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 smarttab
