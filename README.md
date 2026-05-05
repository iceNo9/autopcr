# autopcr

[![License](https://img.shields.io/github/license/cc004/autopcr)](LICENSE)

自动清日常
bug反馈/意见/交流群: 885228564

请先运行一次`python3 _download_web.py`下载前端资源。

如果网络不好，可自行[下载压缩包](https://github.com/Lanly109/AutoPCR_Web/releases/latest)，然后`python3 _download_web.py /path/to/zip`安装。

可再运行`python3 _download_data.py`下载数据库和图片资源。

## HTTP 服务器模式

```bash
python3 _httpserver_test.py
```

访问`/daily/login`

## Hoshino插件模式

使用前请更新Hoshino到最新版，并**更新Hoshino的配置文件`__bot__.py`**

## 渠道服支持

渠道服需要自抓`uid`和`access_key`，作为用户名和密码。

## Docker 部署

```bash
# 1. 复制环境变量模板并按需修改
cp .env.example .env

# 2. 一键启动
docker compose up -d

# 查看日志
docker compose logs -f

# 停止服务（数据不会丢失）
docker compose down
```

数据持久化通过 Docker named volumes 实现，以下目录会被持久化保存：

| 卷名 | 容器路径 | 说明 |
|------|---------|------|
| `autopcr_cache` | `/app/cache` | 用户账号配置、游戏数据库、session |
| `autopcr_result` | `/app/result` | 任务执行结果 |
| `autopcr_log` | `/app/log` | 应用日志 |

## 配置

所有配置均可通过环境变量控制，Docker 部署时在 `.env` 文件中设置即可，参见 `.env.example`。

| 环境变量 | 描述 | 默认值 |
|---------|------|--------|
| AUTOPCR_SERVER_HOST | 服务器绑定地址 | 0.0.0.0 |
| AUTOPCR_SERVER_PORT | 服务器启动端口 | 13200 |
| AUTOPCR_SERVER_DEBUG_LOG | 是否输出 Debug 日志 | False |
| AUTOPCR_SERVER_ALLOW_REGISTER | 是否允许注册 | True |
| AUTOPCR_SERVER_SUPERUSER | 设置无条件拥有管理员的用户 | （可选，设置为登录使用的 QQ） |
| AUTOPCR_PUBLIC_ADDRESS | QQ bot 发送的公网访问地址 | （可选，留空自动检测） |
| AUTOPCR_USE_HTTPS | 公网访问链接是否使用 HTTPS | False |

以下为 Docker 部署专属变量（仅在 `docker-compose.yml` 中使用）：

| 环境变量 | 描述 | 默认值 |
|---------|------|--------|
| HOST_PORT | 宿主机映射端口 | 13200 |
| TZ | 容器时区 | Asia/Shanghai |
| RESTART_POLICY | 容器重启策略 | unless-stopped |

## Credits
- aiorequests 来自 [HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot)
- 图片绘制改自 [convert2img](https://github.com/SonderXiaoming/convert2img)
- 前端html来自 [AutoPCR_Web](https://github.com/Lanly109/AutoPCR_Web)
- 角色OCR来自 [arena](https://github.com/watermellye/arena)
- ~~前端html来自 [autopcr_web](https://github.com/cca2878/autopcr_web)~~
- ~~前端html来自 [AutoPCR_Archived](https://github.com/watermellye/AutoPCR_Archived)~~
- ~~模型生成来自 [PcrotoGen](https://github.com/cc004/PcrotoGen)~~

## Github Action（打包镜像仅适用于HTTP服务器模式）
打包镜像默认推送到[ghcr](https://ghcr.io),如需推送到[dockerhub](https://hub.docker.com)需要执行以下步骤
- 添加变量`DOKCKERHUB_IMAGE_NAME`用于推送到dockerhub镜像名称,例如autopcr/autopcr
- 添加机密`DOCKERHUB_USERNAME`和`DOCKERHUB_TOKEN`用于推送到dockerhub的身份验证

## 使用 pixi

创建环境：`pixi install`
下载前端资源：`pixi run download_web`
启动服务器：`pixi run server`
