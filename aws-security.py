import boto3
import datetime, dateutil.parser
import re

region = 'eu-west-1'

client = boto3.client('ec2', region_name=region)

#Security Groups
response = client.describe_security_groups()
all_sec_groups = []
nbGp = 0
for SecGrp in response['SecurityGroups']:
    all_sec_groups.append(SecGrp['GroupId'])
    nbGp += 1
sec_groups_in_use = set()
response = client.describe_instances()
for r in response['Reservations']:
    for inst in r['Instances']:
        for m in re.finditer('((sg-)[0-9a-zA-Z]{8})', str(inst['SecurityGroups'])):
            if m.group(0) not in sec_groups_in_use:
                sec_groups_in_use.add(m.group(0))

#Cloudformation
cf = boto3.client('cloudformation', region_name=region)
response = cf.describe_stacks()
LC_list=[]
for LC in response['Stacks']:
    template = cf.get_template(StackName=LC['StackName'])
    for m in re.finditer('((sg-)[0-9a-zA-Z]{8})', str(template)):
        if m.group(0) not in sec_groups_in_use:
            sec_groups_in_use.add(m.group(0))

#LaunchConfig
client = boto3.client('autoscaling', region_name=region)
response = client.describe_launch_configurations()
LC_list=[]
for LC in response['LaunchConfigurations']:
    for sec in LC['SecurityGroups']:
        if sec not in sec_groups_in_use:
            sec_groups_in_use.add(sec)

#LoadBalancer
lb = boto3.client('elb', region_name=region)
response = lb.describe_load_balancers()
for loadbalancer in response['LoadBalancerDescriptions']:
    for lbs in loadbalancer['SecurityGroups']:
        if lbs not in sec_groups_in_use:
            sec_groups_in_use.add(lbs)

#RDS
rds = boto3.client('rds', region_name=region)
response = rds.describe_db_instances()
for db in response['DBInstances']:
    for m in re.finditer('((sg-)[0-9a-zA-Z]{8})', str(db)):
        if m.group(0) not in sec_groups_in_use:
            sec_groups_in_use.add(m.group(0))

#ElasticCache
ecache = boto3.client('elasticache', region_name=region)
response = ecache.describe_cache_clusters()
for ec in response['CacheClusters']:
    for m in re.finditer('((sg-)[0-9a-zA-Z]{8})', str(ec)):
        if m.group(0) not in sec_groups_in_use:
            sec_groups_in_use.add(m.group(0))

#Redshift
redshift = boto3.client('redshift', region_name=region)
response = redshift.describe_clusters()
for ec in response['Clusters']:
    for m in re.finditer('((sg-)[0-9a-zA-Z]{8})', str(ec)):
        if m.group(0) not in sec_groups_in_use:
            sec_groups_in_use.add(m.group(0))

#Unused
unused_sec_groups = set()
nbGpUnused = 0
for groups in all_sec_groups:
    if groups not in sec_groups_in_use:
        unused_sec_groups.add(groups)
        nbGpUnused += 1

ec2 = boto3.resource('ec2', region_name=region)
for group in unused_sec_groups:
    security_group = ec2.SecurityGroup(group)
    print group,
    print security_group.group_name

print(str(nbGp) + " Security groups, "+ str(nbGpUnused) + " unused")
