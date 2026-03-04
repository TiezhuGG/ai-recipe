# 部署指南

本文档提供 AI智能菜谱生成平台的部署说明。

---

## 部署方式

支持以下部署方式：
1. **Docker Compose 部署** (推荐)
2. **手动部署**
3. **云平台部署**

---

## 方式一: Docker Compose 部署 (推荐)

### 前置要求
- Docker 20.10+
- Docker Compose 2.0+

### 部署步骤

#### 1. 配置环境变量

创建 `.env` 文件:

```bash
# 数据库配置
DB_PASSWORD=your_secure_password_here

# 豆包 API 配置
DOUBAO_API_KEY=your_doubao_api_key
DOUBAO_API_URL=https://ark.cn-beijing.volces.com/api/v3

# 安全配置
SECRET_KEY=your_secret_key_here

# 前端配置
VITE_API_BASE_URL=http://your-domain.com:8000
```

#### 2. 运行部署脚本

```bash
# 给脚本添加执行权限
chmod +x scripts/*.sh

# 执行部署
./scripts/deploy-docker.sh
```

#### 3. 验证部署

```bash
# 检查服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 健康检查
./scripts/health-check.sh
```

#### 4. 访问应用

- 前端: http://localhost
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

### Docker Compose 管理命令

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f [service_name]

# 进入容器
docker-compose exec backend bash
docker-compose exec frontend sh

# 重新构建
docker-compose build --no-cache
```

---

## 方式二: 手动部署

### 后端部署

#### 1. 安装依赖

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

#### 2. 配置环境

复制并编辑生产环境配置:

```bash
cp .env.example .env.production
# 编辑 .env.production 填入生产配置
```

#### 3. 初始化数据库

```bash
# 运行数据库迁移
./scripts/db-migrate.sh
```

#### 4. 启动后端

```bash
# 使用启动脚本
./scripts/start-backend.sh

# 或手动启动
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 前端部署

#### 1. 构建前端

```bash
cd frontend

# 安装依赖
npm ci

# 构建生产版本
npm run build

# 或使用脚本
../scripts/build-frontend.sh
```

#### 2. 部署静态文件

将 `frontend/dist` 目录部署到 Web 服务器:

**使用 Nginx:**

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    root /var/www/recipe-app/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**使用 Apache:**

```apache
<VirtualHost *:80>
    ServerName yourdomain.com
    DocumentRoot /var/www/recipe-app/dist

    <Directory /var/www/recipe-app/dist>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
        
        RewriteEngine On
        RewriteBase /
        RewriteRule ^index\.html$ - [L]
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteCond %{REQUEST_FILENAME} !-d
        RewriteRule . /index.html [L]
    </Directory>

    ProxyPass /api http://localhost:8000/api
    ProxyPassReverse /api http://localhost:8000/api
</VirtualHost>
```

---

## 方式三: 云平台部署

### AWS 部署

#### 使用 AWS Elastic Beanstalk

1. 安装 EB CLI
2. 初始化 EB 应用
3. 部署

```bash
eb init
eb create production
eb deploy
```

#### 使用 AWS ECS

1. 构建 Docker 镜像
2. 推送到 ECR
3. 创建 ECS 任务定义
4. 部署到 ECS 集群

### 阿里云部署

#### 使用容器服务 ACK

1. 创建 Kubernetes 集群
2. 配置 kubectl
3. 部署应用

```bash
kubectl apply -f k8s/
```

### 其他云平台

- **Heroku**: 使用 Procfile
- **DigitalOcean**: 使用 App Platform
- **Vercel**: 前端部署
- **Railway**: 全栈部署

---

## 数据库配置

### PostgreSQL 安装

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**CentOS/RHEL:**

```bash
sudo yum install postgresql-server postgresql-contrib
sudo postgresql-setup initdb
sudo systemctl start postgresql
```

### 创建数据库

```sql
CREATE DATABASE recipe_db;
CREATE USER recipe_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE recipe_db TO recipe_user;
```

### 数据库连接字符串

```
postgresql://recipe_user:password@localhost:5432/recipe_db
```

---

## SSL/HTTPS 配置

### 使用 Let's Encrypt

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d yourdomain.com

# 自动续期
sudo certbot renew --dry-run
```

### Nginx SSL 配置

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL 配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # 其他配置...
}

# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

---

## 监控和日志

### 日志位置

- 后端日志: `/var/log/recipe-app/app.log`
- Nginx 日志: `/var/log/nginx/`
- Docker 日志: `docker-compose logs`

### 监控工具

推荐使用:
- **Prometheus + Grafana**: 性能监控
- **ELK Stack**: 日志分析
- **Sentry**: 错误追踪
- **Uptime Robot**: 可用性监控

---

## 备份和恢复

### 数据库备份

```bash
# 自动备份
./scripts/backup-db.sh

# 手动备份
pg_dump -U recipe_user recipe_db > backup.sql
```

### 数据库恢复

```bash
# 恢复数据库
psql -U recipe_user recipe_db < backup.sql
```

### 文件备份

```bash
# 备份上传文件
tar -czf uploads_backup.tar.gz backend/uploads/

# 恢复上传文件
tar -xzf uploads_backup.tar.gz
```

---

## 性能优化

### 后端优化

1. **使用 Gunicorn + Uvicorn Workers**

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

2. **启用数据库连接池**

在 `config/production.py` 中配置:

```python
DB_POOL_SIZE = 20
DB_MAX_OVERFLOW = 10
```

3. **使用 Redis 缓存**

```python
# 安装 Redis
pip install redis

# 配置缓存
REDIS_URL = "redis://localhost:6379"
```

### 前端优化

1. **启用 Gzip 压缩** (已在 nginx.conf 中配置)
2. **使用 CDN** 加速静态资源
3. **代码分割** (Vite 自动处理)
4. **图片优化** (使用 WebP 格式)

---

## 安全建议

1. **更改默认密码**
   - 数据库密码
   - SECRET_KEY
   - API 密钥

2. **配置防火墙**

```bash
# UFW (Ubuntu)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

3. **限制 API 访问**
   - 配置 CORS
   - 实施速率限制
   - 使用 API 密钥

4. **定期更新**
   - 系统包
   - Python 依赖
   - Node.js 依赖

---

## 故障排查

### 常见问题

#### 1. 数据库连接失败

```bash
# 检查 PostgreSQL 状态
sudo systemctl status postgresql

# 检查连接字符串
echo $DATABASE_URL
```

#### 2. 端口被占用

```bash
# 查找占用端口的进程
lsof -i :8000
lsof -i :80

# 终止进程
kill -9 <PID>
```

#### 3. Docker 容器无法启动

```bash
# 查看详细日志
docker-compose logs backend
docker-compose logs frontend

# 重新构建
docker-compose build --no-cache
```

#### 4. 前端无法连接后端

- 检查 CORS 配置
- 检查 API 基础 URL
- 检查网络连接

---

## 维护任务

### 日常维护

- 监控服务状态
- 检查日志错误
- 监控磁盘空间
- 检查数据库性能

### 定期维护

- 数据库备份 (每天)
- 清理旧日志 (每周)
- 更新依赖 (每月)
- 安全审计 (每季度)

---

## 支持和帮助

如遇到部署问题:

1. 查看日志文件
2. 检查配置文件
3. 参考故障排查部分
4. 查看项目文档

---

## 附录

### 环境变量完整列表

参考 `backend/.env.production` 和 `frontend/.env.production`

### 端口使用

- 80: 前端 (HTTP)
- 443: 前端 (HTTPS)
- 8000: 后端 API
- 5432: PostgreSQL

### 系统要求

- CPU: 2核+
- 内存: 4GB+
- 磁盘: 20GB+
- 操作系统: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
