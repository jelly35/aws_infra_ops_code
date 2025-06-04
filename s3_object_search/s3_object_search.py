# S3 에 원하는 문자열이 포함된 객체를 찾는 스크립트
# 작성일 : 2023. 06. 08
# 작성자 : 문지성
# 파일명 : s3_object_search.py

import boto3


def search_objects_in_bucket(bucket_name, search_string):
    """Search for objects that contain the search string in a single bucket."""
    s3 = boto3.client("s3")

    paginator = s3.get_paginator("list_objects_v2")
    matched_keys = []

    for page in paginator.paginate(Bucket=bucket_name):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if search_string in key:
                matched_keys.append(key)

    return matched_keys


def search_objects_in_all_buckets(search_string):
    """Search for objects containing the search string across all buckets."""
    s3 = boto3.client("s3")

    response = s3.list_buckets()
    buckets = [bucket["Name"] for bucket in response.get("Buckets", [])]

    matched_keys = []

    for bucket in buckets:
        matched_keys.extend(search_objects_in_bucket(bucket, search_string))

    return matched_keys

def main():
    """Run the search script based on user input."""
    search_option = input("모든 버킷을 대상으로 검색하시겠습니까? (yes/no): ")

    if search_option.lower() == "yes":
        # 조회하는 계정의 모든 버킷을 대상으로 검색합니다.
        search_string = input("검색할 문자열을 입력하세요: ")
        matched_keys = search_objects_in_all_buckets(search_string)
    else:
        # 특정 버킷을 대상으로 검색합니다.
        bucket_name = input("검색할 버킷 이름을 입력하세요: ")
        search_string = input("검색할 문자열을 입력하세요: ")
        matched_keys = search_objects_in_bucket(bucket_name, search_string)

    # 검색 결과를 출력합니다.
    for key in matched_keys:
        print(key)


if __name__ == "__main__":
    main()

