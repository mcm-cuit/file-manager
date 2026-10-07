#!/usr/bin/python 3.12
# -*- coding: utf-8 -*- 
#
# @Time    : 2026/10/7 18:09
# @File    : schemas.py
# @Software: PyCharm

from datetime import datetime
from uuid import UUID

from django.conf import settings
from ninja import Schema


class UserOut(Schema):
    id: UUID
    username: str
    github_avatar_url: str
    is_developer: bool
    is_staff: bool
    is_superuser: bool


class PresignUploadIn(Schema):
    object_key: str
    original_name: str
    size: int
    content_type: str = 'application/octet-stream'


class PresignUploadOut(Schema):
    upload_id: UUID
    object_key: str
    upload_url: str


class CompleteUploadIn(Schema):
    upload_id: UUID


class FileOut(Schema):
    id: UUID
    object_key: str
    original_name: str
    content_type: str
    size: int
    uploader_id: UUID
    created_at: datetime
    url: str

    @staticmethod
    def resolve_url(obj):
        return f'{settings.R2_PUBLIC_URL}/{obj.object_key}'


class ObjectFileOut(Schema):
    object_key: str
    original_name: str
    size: int
    content_type: str
    uploader_id: UUID
    created_at: datetime
    url: str

    @staticmethod
    def resolve_url(obj):
        return f'{settings.R2_PUBLIC_URL}/{obj.object_key}'


class ObjectsOut(Schema):
    directories: list[str]
    files: list[ObjectFileOut]
