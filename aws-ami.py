import boto3
import datetime, dateutil.parser
import re

good_images2 = set()
good_images3 = set()
region = "eu-west-1"
ec2 = boto3.resource("ec2", region_name=region)

instances = ec2.instances.all()
my_images = ec2.images.filter(Owners=["OWNER_ID"])

#EC2 in use AMI
good_images = set([instance.image_id for instance in ec2.instances.all()])

#LaunchConfig in use AMI
client = boto3.client('autoscaling', region_name=region)
response = client.describe_launch_configurations()
LC_list=[]
for LC in response['LaunchConfigurations']:
    good_images2.add(LC['ImageId'])

#CloudFormation in use AMI
client = boto3.client('cloudformation', region_name=region)
response = client.describe_stacks()
LC_list=[]
for LC in response['Stacks']:
    template = client.get_template(StackName=LC['StackName'])
    m = re.search('((ami-)[0-9a-zA-Z]{8})', str(template))
    if m:
        good_images3.add(m.group(0))

good_images = good_images.union(good_images2)
good_images = good_images.union(good_images3)

my_images_dict = {image.id: image for image in my_images if image.id not in good_images}

for keys,values in my_images_dict.items():
    print keys,
    d = dateutil.parser.parse(values.creation_date)
    print d.strftime('%m/%d/%Y'),
    print values.name
print(str(len(my_images_dict)) + " Unused AMI's")
