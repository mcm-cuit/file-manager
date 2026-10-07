import secrets

import requests
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.urls import reverse

from .models import User


def login_page(request):
    if request.user.is_authenticated:
        return redirect('/')
    return render(request, 'files/login.html')


def github_login(request):
    state = secrets.token_urlsafe(32)
    request.session['github_oauth_state'] = state

    callback_url = request.build_absolute_uri(reverse('github_callback'))
    params = {
        'client_id': settings.GITHUB_CLIENT_ID,
        'redirect_uri': callback_url,
        'scope': 'read:user user:email',
        'state': state,
    }

    response = requests.Request('GET', 'https://github.com/login/oauth/authorize', params=params).prepare()
    return redirect(response.url)


def github_callback(request):
    code = request.GET.get('code')
    state = request.GET.get('state')

    if not code or not state or state != request.session.pop('github_oauth_state', None):
        return HttpResponse('GitHub OAuth 验证失败', status=400)

    callback_url = request.build_absolute_uri(reverse('github_callback'))
    token_response = requests.post(
        'https://github.com/login/oauth/access_token',
        data={
            'client_id': settings.GITHUB_CLIENT_ID,
            'client_secret': settings.GITHUB_CLIENT_SECRET,
            'code': code,
            'redirect_uri': callback_url,
        },
        headers={'Accept': 'application/json'},
        timeout=10,
    )
    token_response.raise_for_status()
    access_token = token_response.json().get('access_token')

    if not access_token:
        return HttpResponse('获取 GitHub Access Token 失败', status=400)

    user_response = requests.get(
        'https://api.github.com/user',
        headers={
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/vnd.github+json',
        },
        timeout=10,
    )
    user_response.raise_for_status()
    github_user = user_response.json()
    print(github_user)
    user, created = User.objects.get_or_create(
        github_id=github_user['id'],
        defaults={
            'username': github_user['login'],
            'github_avatar_url': github_user.get('avatar_url', ''),
        },
    )

    if not created:
        user.username = github_user['login']
        user.github_avatar_url = github_user.get('avatar_url', '')
        user.save(update_fields=['username', 'github_avatar_url', 'updated_at'])

    if not user.is_active or not user.is_developer:
        return HttpResponseForbidden('当前账号没有开发者权限')

    login(request, user)
    return redirect('/')


@login_required
def index(request):
    return render(request, 'files/index.html')
