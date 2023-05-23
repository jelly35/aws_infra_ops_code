import csv
import os
import boto3
import configparser
from botocore.exceptions import ProfileNotFound

def get_rds_info_in_account(profile, region):
    try:
        session = boto3.Session(profile_name=profile, region_name=region or 'ap-northeast-2')
        rds = session.client('rds')
        paginator = rds.get_paginator('describe_db_clusters')

        rds_info = []

        for page in paginator.paginate():
            for db_cluster in page['DBClusters']:
                for member in db_cluster['DBClusterMembers']:
                    instance_response = rds.describe_db_instances(
                        DBInstanceIdentifier=member['DBInstanceIdentifier']
                    )
                    instance = instance_response['DBInstances'][0]

                    rds_info.append({
                        'Profile': profile,
                        'Cluster Name': db_cluster['DBClusterIdentifier'],
                        'Cluster Endpoint': db_cluster['Endpoint'],
                        'Cluster Instance Type': instance['DBInstanceClass']
                    })

        return rds_info
    except ProfileNotFound:
        print(f"No profile found for '{profile}'")
        return []

def write_to_csv(data, filename):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Profile', 'Cluster Name', 'Cluster Endpoint', 'Cluster Instance Type']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in data:
            writer.writerow(row)

def get_profiles_from_config():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.getenv('USERPROFILE'), '.aws', 'config'))
    return [(section.replace('profile ', ''), config[section].get('region', 'ap-northeast-2')) for section in config.sections() if 'profile ' in section]

def main():
    profiles = get_profiles_from_config()
    all_rds_info = []

    for profile, region in profiles:
        all_rds_info.extend(get_rds_info_in_account(profile, region))

    write_to_csv(all_rds_info, 'rds_info.csv')

if __name__ == "__main__":
    main()
