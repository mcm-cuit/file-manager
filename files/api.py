#!/usr/bin/python 3.12
# -*- coding: utf-8 -*- 
#
# @Time    : 2026/10/7 18:08
# @File    : api.py
# @Software: PyCharm

from botocore.exceptions import ClientError
from django.core.cache import cache
from ninja import NinjaAPI
from ninja.errors import HttpError
from ninja.security import django_auth
from uuid6 import uuid6

from files.models import File
from files.schemas import UserOut, PresignUploadOut, PresignUploadIn, CompleteUploadIn, ObjectsOut, FileOut
from files.services.r2 import generate_upload_url, head_object

from loguru import logger

api = NinjaAPI(auth=django_auth)


@api.get('/me', response=UserOut)
def me(request):
    return request.user


# 申请 R2 直传地址，并原子占用 object_key 防止重复上传。
@api.post('/files/presign', response=PresignUploadOut)
def presign_upload(request, payload: PresignUploadIn):
    if not request.user.is_developer:
        raise HttpError(403, '没有文件上传权限')

    object_key = payload.object_key.strip().lstrip('/')
    if not object_key or payload.size <= 0:
        raise HttpError(400, '文件参数无效')

    if File.objects.filter(object_key=object_key).exists():
        raise HttpError(409, '文件已存在')

    upload_id = uuid6()
    lock_key = f'file_upload_lock:{object_key}'
    if not cache.add(lock_key, str(upload_id), timeout=600):
        raise HttpError(409, '该文件正在上传')

    cache.set(
        f'file_upload:{upload_id}',
        {
            'user_id': str(request.user.id),
            'object_key': object_key,
            'original_name': payload.original_name,
            'size': payload.size,
            'content_type': payload.content_type,
        },
        timeout=600,
    )

    upload_url = generate_upload_url(object_key, payload.content_type, expires_in=600)
    logger.info(f'生成上传地址 | user_id={request.user.id} upload_id={upload_id} object_key={object_key}')
    return {'upload_id': upload_id, 'object_key': object_key, 'upload_url': upload_url}


@api.post('/files/complete', response=FileOut)
def complete_upload(request, payload: CompleteUploadIn):
    upload_id = payload.upload_id
    cache_key = f'file_upload:{upload_id}'
    upload = cache.get(cache_key)

    if not upload:
        raise HttpError(400, '上传任务不存在或已过期')

    if upload['user_id'] != str(request.user.id):
        raise HttpError(403, '无权完成该上传任务')

    try:
        metadata = head_object(upload['object_key'])
    except ClientError as e:
        if e.response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 404:
            raise HttpError(400, 'R2 中未找到该文件')
        raise

    if metadata['ContentLength'] != upload['size']:
        raise HttpError(400, '文件大小与申请上传时不一致')

    file = File.objects.create(
        object_key=upload['object_key'],
        original_name=upload['original_name'],
        content_type=metadata.get('ContentType', upload['content_type']),
        size=metadata['ContentLength'],
        uploader_id=request.user.id,
    )

    cache.delete(cache_key)
    cache.delete(f'file_upload_lock:{upload["object_key"]}')
    logger.info(f'完成文件上传 | user_id={request.user.id} upload_id={upload_id} '
                f'file_id={file.id} object_key={file.object_key} size={file.size}')
    return file


@api.get('/objects', response=ObjectsOut)
def list_objects(request):
    if request.user.is_superuser or request.user.is_staff:
        files = File.objects.all().order_by('-created_at')
    elif request.user.is_developer:
        files = File.objects.filter(uploader_id=request.user.id).order_by('-created_at')
    else:
        raise HttpError(403, '没有文件查看权限')
    directories = set()
    for object_key in File.objects.values_list('object_key', flat=True):
        parts = object_key.split('/')
        for i in range(1, len(parts)):
            directories.add('/'.join(parts[:i]) + '/')
    return {'directories': sorted(directories), 'files': files}
