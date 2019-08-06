#!/usr/bin/python

import sys
import getopt
import boto3
import json
import collections


ec2 = boto3.resource('ec2')
instances = ec2.instances.filter(InstanceIds=[])
ec2id = False
# https://pyformat.info/
position = '{!s:<22} {!s:<12} {!s:<14} {!s:<18} {!s:<18} {!s:<22} {!s:<22} {!s:<30} {!s:<42}'


def usage():
    print("Usage: {0} [-h|--help] [-i|--instance <instance_id>]".format(sys.argv[0]))

try:
    opts, args = getopt.getopt(sys.argv[1:], 'hi:', ['help', 'instance='])
except getopt.GetoptError as msg:
    print(msg)
    usage()
    sys.exit(1)

for opt, arg in opts:
    if opt in ('-h', '--help'):
        print("List or describe EC2 instance details")
        print("")
        usage()
        print("")
        print("Options:")
        print(" -h, --help                      Print this help screen")
        print(" -i, --instance <instance_id>    Print instance details")
        sys.exit(1)
    elif opt in ('-i', '--instance'):
        ec2id = True
        instances = ec2.instances.filter(InstanceIds=[arg])
    else:
        usage()
        sys.exit(1)

def legend():
    if not ec2id:
        print('-' * 200)
        print(position.format(
            'Instance Id',
            'State',
            'Type',
            'Private IP',
            'Public IP',
            'VPC Id',
            'AMI Id',
            'Launch Time',
            'Name'
        ))
        print('-' * 200)

def get_ec2():
    for instance in instances:

        if ec2id:
            sg = {i['GroupId']: i['GroupName'] for i in instance.security_groups}
            tag = {i['Key']: i['Value'] for i in instance.tags}

            ec2info = collections.OrderedDict([
                ('Instance Id', instance.id),
                ('State', instance.state['Name']),
                ('AMI Id', instance.image_id),
                ('Type', instance.instance_type),
                ('Private IP', instance.private_ip_address),
                ('Public IP', instance.public_ip_address),
                ('Availability zone', instance.placement['AvailabilityZone']),
                ('VPC Id', instance.vpc_id),
                ('Subnet Id', instance.subnet_id),
                ('Launch time', str(instance.launch_time)),
                ('Virtualization', instance.virtualization_type),
                ('Root device type', instance.root_device_type),
                ('Root device name', instance.root_device_name),
                ('EBS optimized', instance.ebs_optimized),
                ('Key pair name', instance.key_name),
                ('ARN profile', instance.iam_instance_profile['Arn']),
                ('Security groups', sg),
                ('Tags', tag)
            ])

            print(json.dumps(ec2info, indent=2))

        else:
            ec2info = [
                instance.id,
                instance.state['Name'],
                instance.instance_type,
                instance.private_ip_address,
                instance.public_ip_address,
                instance.vpc_id,
                instance.image_id,
                str(instance.launch_time)
            ]

            keyfound = False

            if instance.tags is not None:
                for tag in instance.tags:
                    if tag['Key'] == 'Name':
                        ec2info.append(tag['Value'])
                        keyfound = True
                        break
                if not keyfound:
                    ec2info.append('')
            else:
                ec2info.append('')

            print(position.format(*ec2info))

def main():
    legend()
    get_ec2()
    legend()

if __name__ == '__main__':
    main()
