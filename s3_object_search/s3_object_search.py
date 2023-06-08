# S3 에 원하는 문자열이 포함된 객체를 찾는 스크립트
# 작성일 : 2023. 06. 08
# 작성자 : 문지성
# 파일명 : s3_object_search.py

import boto3
import asyncio

async def search_objects_in_bucket(bucket_name, search_string):
    s3 = boto3.client('s3')

    response = await s3.list_objects_v2(Bucket=bucket_name)
    keys = [obj['Key'] for obj in response['Contents']]

    matched_keys = []

    for key in keys:
        if search_string in key:
            matched_keys.append(key)

    return matched_keys

async def search_objects_in_all_buckets(search_string):
    s3 = boto3.client('s3')

    response = await s3.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]

    matched_keys = []

    # 비동기로 각 버킷에서 객체 검색 작업을 실행합니다.
    tasks = [search_objects_in_bucket(bucket, search_string) for bucket in buckets]
    results = await asyncio.gather(*tasks)

    # 검색 결과를 합칩니다.
    for result in results:
        matched_keys.extend(result)

    return matched_keys

# 사용자로부터 조회 방식을 입력 받습니다.
search_option = input("모든 버킷을 대상으로 검색하시겠습니까? (yes/no): ")

if search_option.lower() == "yes":
    # 조회하는 계정의 모든 버킷을 대상으로 검색합니다.
    search_string = input("검색할 문자열을 입력하세요: ")

    loop = asyncio.get_event_loop()
    matched_keys = loop.run_until_complete(search_objects_in_all_buckets(search_string))
    loop.close()
else:
    # 특정 버킷을 대상으로 검색합니다.
    bucket_name = input("검색할 버킷 이름을 입력하세요: ")
    search_string = input("검색할 문자열을 입력하세요: ")

    loop = asyncio.get_event_loop()
    matched_keys = loop.run_until_complete(search_objects_in_bucket(bucket_name, search_string))
    loop.close()

# 검색 결과를 출력합니다.
for key in matched_keys:
    print(key)

