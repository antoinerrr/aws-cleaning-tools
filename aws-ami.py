import boto3
import datetime, dateutil.parser

good_images2 = set()
region = "eu-west-1"
ec2 = boto3.resource("ec2", region_name=region)

instances = ec2.instances.all()
my_images = ec2.images.filter(Owners=["OWNER_ID"])

#Ami's used on EC2 instances 
good_images = set([instance.image_id for instance in ec2.instances.all()])

#Ami's used on autoscaling gps
client = boto3.client('autoscaling', region_name=region)
response = client.describe_launch_configurations()
LC_list=[]
for LC in response['LaunchConfigurations']:
    good_images2.add(LC['ImageId'])

good_images = good_images.union(good_images2)

my_images_dict = {image.id: image for image in my_images if image.id not in good_images}

for keys,values in my_images_dict.items():
    print keys,
    d = dateutil.parser.parse(values.creation_date)
    print (d.strftime('%m/%d/%Y'))
print(str(len(my_images_dict)) + " Unused AMI's")
