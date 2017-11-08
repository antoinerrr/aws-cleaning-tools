#!/usr/local/bin/python3
import boto3

ec2 = boto3.client("ec2")
IP_POOL = {}

all_sg = ec2.describe_security_groups()
for sg in all_sg['SecurityGroups']:
	print(sg['GroupName'] + "  -  " + sg['GroupId'])
	for ip in sg['IpPermissions']:
		if 'FromPort' in ip:
			print("     " + str(ip['FromPort']) + " " + str(ip['ToPort']) + " " + ip['IpProtocol'])
			for cidr in ip['IpRanges']:
				if str(cidr["CidrIp"]) not in IP_POOL:
					desc = input("Description de la regle pour " + cidr["CidrIp"] +": ")
					IP_POOL[str(cidr["CidrIp"])] = desc
				response = ec2.update_security_group_rule_descriptions_ingress(
				    GroupId=sg['GroupId'],
				    IpPermissions=[
				        {
				            'FromPort': ip['FromPort'],
				            'IpProtocol': ip['IpProtocol'],
				            'IpRanges': [
				                {
				                    'CidrIp': cidr["CidrIp"],
				                    'Description': IP_POOL[cidr["CidrIp"]]
				                },
				            ],
				            'ToPort': ip['ToPort'],
				        },
				    ]
				)
				print("         " + str(cidr["CidrIp"]))
