# MCM-CUIT File Manager

MCM-CUIT File Manager 是为成都信息工程大学学生数学建模协会相关网站开发的文件管理系统，主要用于管理图片、文档及其他静态资源。类似于实现的是一个极其简单的 OSS 功能。

项目基于 Django 开发，使用 Cloudflare R2 存储文件，支持 GitHub OAuth 登录、极其简单的权限管理和文件上传。

## 功能特性

- GitHub OAuth 身份认证
- 基于用户角色的访问权限控制
- 文件上传、浏览与管理
- 多文件上传及进度展示
- 自定义上传路径及目录浏览
- Cloudflare R2 对象存储
- 浏览器直传 R2，减少服务器带宽消耗

## 技术栈

| 类型   | 技术                              |
|------|---------------------------------|
| 后端   | Python、Django 5.2、Django Ninja  |
| 前端   | Django Templates、JavaScript、CSS |
| 数据库  | MySQL                           |
| 缓存   | Redis                           |
| 对象存储 | Cloudflare R2                   |
| 身份认证 | GitHub OAuth                    |
| 部署   | Gunicorn、Nginx、systemd          |

核心服务说明

- **Cloudflare R2**：一种云端文件存储服务，可以理解为免费的文件服务器。R2 提供一定的免费存储和请求额度，且不收取流量出口费用，因此适合托管图片、文档等静态资源。但 R2 不提供完整的文件管理界面，所以本项目通过 Django 实现文件上传、目录浏览和权限管理。
- **GitHub OAuth**：GitHub 提供的第三方登录服务。用户可以直接使用 GitHub 账号登录，无需额外注册。项目通过 GitHub 验证用户身份，再由 Django 管理用户权限。这种方式在简化账号管理的同时，也提高了一定的使用门槛，符合该项目主要是为开发者使用的设计初衷。可通过 [GitHub OAuth App](https://github.com/settings/applications/new) 创建应用并获取认证凭据。

## 本地运行

### 1. 克隆项目

```bash
git clone https://github.com/mcm-cuit/file-manager.git
cd file-manager
```

### 2. 安装依赖

建议使用 Python 3.12。

```bash
python -m venv .venv
```

Windows：

```bash
.venv\Scripts\activate
```

Linux：

```bash
source .venv/bin/activate
```

安装依赖：

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

在项目根目录创建 `.env`，根据 `config/settings.py` 配置 Django、MySQL、Redis、GitHub OAuth 和 Cloudflare R2 所需的环境变量。

注意：GitHub OAuth 相关配置在 [GitHub OAuth App](https://github.com/settings/applications/new) 创建应用后，需将回调地址（Callback URL）设置为：

```text
http://127.0.0.1:8000/auth/github/callback/
```

主页（Homepage URL）设置为：

```text
http://127.0.0.1:8000/
```

### 4. 初始化数据库

确保 MySQL 和 Redis 服务已启动，然后执行：

```bash
python manage.py migrate
```

如需创建管理员：

```bash
python manage.py createsuperuser
```

### 5. 启动服务

```bash
python manage.py runserver
```

访问 http://127.0.0.1:8000/
