#!/usr/bin/env python

import argparse
import sys
import logging
import boto3

client = boto3.client("elasticbeanstalk")

# Fix Python 2.x.
try: input = raw_input
except NameError: pass

# get list of currently deployed versions for each app
def get_deployed_versions():
    res = {}
    environments = client.describe_environments()
    for env in environments["Environments"]:
        try:
            if env["ApplicationName"] in res:
                res[env["ApplicationName"]].append(env["VersionLabel"])
            else:
                res[env["ApplicationName"]] = [env["VersionLabel"]]
        except KeyError:
            pass
    return res

# get list of app versions per app
def get_versions_per_app():
    res = {}
    versions = client.describe_application_versions()
    # sort by date
    versions = sorted(versions["ApplicationVersions"], key=lambda x: x["DateCreated"], reverse=True)
    for v in versions:
        try:
            if v["ApplicationName"] in res:
                res[v["ApplicationName"]].append( v["VersionLabel"] )
            else:
                res[v["ApplicationName"]] = [v["VersionLabel"]]
        except KeyError:
            pass
    return res

def get_deleted_versions(deployed_versions, app_versions, keep_versions):
    res = app_versions[:]
    res = list( set(res) - set(deployed_versions) )
    return res[keep_versions - 1 :]

def get_kept_versions(deployed_versions, app_versions, keep_versions):
    res = app_versions[:]
    res = res[0:keep_versions]
    res = list( set(res) | set(deployed_versions) )
    return res

def delete_version(version, app):
    client.delete_application_version(
        ApplicationName=app,
        VersionLabel=version,
        DeleteSourceBundle=True
    )

def main():

    parser = argparse.ArgumentParser(
        description="Delete old EB application versions",
        epilog="Copyright (C) 2017 Kamil Zegier <kamilzegier@gmail.com>")
    parser.add_argument("-k", "--keep-versions", action="store", default=10, type=int, help="How many versions should we keep for each environment")
    parser.add_argument("-f", "--force", action="store_true", help="Force delete, dont ask for each application")
    parser.add_argument("-v", "--version", help="Print version", action="version", version="%(prog)s 1.0")
    args = parser.parse_args()

    deployed_versions = get_deployed_versions()
    app_versions = get_versions_per_app()

    for app in app_versions:
        versions_to_keep = get_kept_versions(deployed_versions[app], app_versions[app], args.keep_versions)
        versions_to_delete = get_deleted_versions(deployed_versions[app], app_versions[app], args.keep_versions)
        if len(versions_to_delete) == 0:
            print("%s - Nothing to delete" % app)
            continue
        print("%s - %s versions will remain. %s versions will be deleted" % ( app, len(versions_to_keep), len(versions_to_delete) ) )
        if args.force:
            userInput = "y"
        else:
            print("Are you sure you want to delete? (Y/N)")
            userInput = input(':')
        if userInput.lower() == "y":
            for version in versions_to_delete:
                delete_version(version, app)
                print ("Deleted version %s", (version) )

if __name__ == "__main__":
    main()

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 smarttab
