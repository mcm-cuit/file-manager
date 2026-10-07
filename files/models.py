from django.contrib.auth.models import AbstractUser
from django.db import models
from uuid6 import uuid6


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid6, editable=False)
    github_id = models.BigIntegerField(unique=True, null=True, blank=True)
    github_avatar_url = models.URLField(max_length=500, blank=True)
    is_developer = models.BooleanField('是否是有权限的开发者', default=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return self.username


class File(models.Model):
    id = models.UUIDField('ID', primary_key=True, default=uuid6, editable=False)
    object_key = models.CharField('对象键', max_length=512, unique=True)
    original_name = models.CharField('原始文件名', max_length=255)
    content_type = models.CharField('内容类型', max_length=255, blank=True)
    size = models.BigIntegerField('文件大小')
    uploader_id = models.UUIDField('上传者 ID')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'files'
        verbose_name = '文件'
        verbose_name_plural = '文件'

    def __str__(self):
        return self.original_name
