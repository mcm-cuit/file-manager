#!/usr/bin/python 3.12
# -*- coding: utf-8 -*- 
#
# @Time    : 2026/10/7 17:48
# @File    : urls.py
# @Software: PyCharm

from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_page, name='login'),
    path('auth/github/', views.github_login, name='github_login'),
    path('auth/github/callback/', views.github_callback, name='github_callback'),
]
