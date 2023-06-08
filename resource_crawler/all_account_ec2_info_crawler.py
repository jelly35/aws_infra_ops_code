import csv
import os
import boto3
import configparser
from botocore.exceptions import ProfileNotFound, NoCredentialsError, BotoCoreError

def get_profiles_from_config():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.getenv('USERPROFILE'), '.aws', 'config'))
    return [(section.replace('profile ', ''), config[section].get('region', 'ap-northeast-2')) for section in config.sections() if 'profile ' in section]

def get_ec2_info_in_account(profile, region):
    try:
        session = boto3.Session(profile_name=profile, region_name=region)
        ec2_resource = session.resource('ec2')

        ec2_info = []

        for instance in ec2_resource.instances.all():
            tags = {t['Key']: t['Value'] for t in instance.tags or []}
            name = tags.get('Name', '')
            platform = instance.platform or ''
            platform_details = instance.platform_details or ''
            ami_id = instance.image_id
            ami_name = ''

            # Get the AMI name
            if ami_id:
                try:
                    image = ec2_resource.Image(ami_id)
                    ami_name = image.name if image.meta.data else ''
                except (NoCredentialsError, BotoCoreError) as e:
                    print(f"Failed to get AMI name for {ami_id} due to: {str(e)}")

            ec2_info.append({
                'Profile': profile,
                'Name': name,
                'Instance ID': instance.id,
                'Instance Type': instance.instance_type,
                'Internal IP': instance.private_ip_address,
                'Public IP': instance.public_ip_address,
                'Elastic IP': instance.public_ip_address,
                'VPC ID': instance.vpc_id,
                'Subnet ID': instance.subnet_id,
                'OS Platform': platform,
                'OS Platform Details': platform_details,
                'AMI ID': ami_id,
                'AMI Name': ami_name,
            })

        return ec2_info
    except ProfileNotFound:
        print(f"No profile found for '{profile}'")
        return []

def write_to_csv(data, filename):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Profile', 'Name', 'Instance ID', 'Instance Type', 'Internal IP', 'Public IP', 
                      'Elastic IP', 'VPC ID', 'Subnet ID', 'OS Platform', 'OS Platform Details', 
                      'AMI ID', 'AMI Name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in data:
            writer.writerow(row)

def main():
    profiles = get_profiles_from_config()
    all_ec2_info = []

    for profile, region in profiles:
        all_ec2_info.extend(get_ec2_info_in_account(profile, region))

    write_to_csv(all_ec2_info, 'ec2_info.csv')

if __name__ == "__main__":
    main()
 