import urllib3
import boto3
import json
import re

aws_access_key_id='REPLACE_ME'
aws_secret_access_key='REPLACE_ME'
http = urllib3.PoolManager()
url = "https://download.geofabrik.de/index-v1.json"

bucket_name = 'ib-dot-roadway-safety'
prefix = 'input_data/usa/osm/states/'
CLIENT = boto3.client('s3', region_name='us-east-1', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)


http = urllib3.PoolManager()
response = http.request('GET', url)

file_name = url.split('/')[-1]
print(file_name)

# uncomment if you want to refresh the json
#CLIENT.put_object(Body=response.data, Bucket=bucket_name, Key=prefix + file_name)
areas = json.loads(response.data.decode('utf8'))

for x in areas['features']:
    if re.search('us/.*', x['properties']['name']) is not None:
        print(x['properties']['name'])
        print(x['properties']['urls']['pbf'])
        state_data = http.request('GET', x['properties']['urls']['pbf']).data
        file_name = x['properties']['urls']['pbf'].split('/')[-1]
        CLIENT.put_object(Body=state_data, Bucket=bucket_name, Key=prefix + file_name)