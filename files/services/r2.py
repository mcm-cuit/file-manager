#!/usr/bin/python 3.12
# -*- coding: utf-8 -*- 
#
# @Time    : 2026/10/7 18:27
# @File    : r2.py
# @Software: PyCharm

import boto3
from django.conf import settings

r2 = boto3.client(
    's3',
    endpoint_url=f'https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
    aws_access_key_id=settings.R2_ACCESS_KEY_ID,
    aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
    region_name='auto',
)


def generate_upload_url(object_key: str, content_type: str, expires_in: int = 600) -> str:
    return r2.generate_presigned_url(
        'put_object',
        Params={'Bucket': settings.R2_BUCKET_NAME, 'Key': object_key, 'ContentType': content_type},
        ExpiresIn=expires_in,
    )


def head_object(object_key: str):
    return r2.head_object(Bucket=settings.R2_BUCKET_NAME, Key=object_key)
