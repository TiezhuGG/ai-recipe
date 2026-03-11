# 后端功能验证清单

## 任务8 - 后端功能验证

### 基础设施验证

- [ ] **依赖安装**: 所有Python包成功安装
  ```bash
  pip install -r requirements.txt
  ```

- [ ] **环境配置**: .env文件已创建并配置
  - [ ] LLM_API_KEY已设置
  - [ ] DATABASE_URL已配置
  - [ ] UPLOAD_DIR已配置
  - [ ] CORS_ORIGINS已配置

- [ ] **服务器启动**: 应用成功启动，无错误
  ```bash
  python main.py
  ```
  预期输出：
  ```
  INFO:     Started server process
  INFO:     Waiting for application startup.
  INFO:     初始化数据库...
  INFO:     数据库初始化完成
  INFO:     Application startup complete.
  ```

- [ ] **数据库初始化**: 数据库表自动创建
  - [ ] users表创建成功
  - [ ] recipes表创建成功
  - [ ] 上传目录创建成功

### API端点验证

#### 1. 健康检查端点

- [ ] **GET /**: 返回200状态码
  ```bash
  curl http://localhost:8000/
  ```
  预期响应：
  ```json
  {
    "status": "ok",
    "message": "AI智能菜谱生成平台API",
    "version": "1.0.0"
  }
  ```

- [ ] **GET /health**: 返回健康状态
  ```bash
  curl http://localhost:8000/health
  ```

#### 2. 菜谱生成端点

- [ ] **POST /api/recipes/generate**: 成功生成菜谱
  - [ ] 接受有效的请求参数
  - [ ] 返回完整的菜谱数据
  - [ ] 设置session_id Cookie
  - [ ] 参数验证正常（空食材返回400）
  - [ ] AI服务调用正常

测试命令：
```bash
curl -X POST http://localhost:8000/api/recipes/generate \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"ingredients": ["鸡胸肉", "西兰花"], "flavor_tags": ["健康"], "cuisine_types": ["中餐"], "special_groups": []}'
```

#### 3. 菜谱保存端点

- [ ] **POST /api/recipes/save**: 成功保存菜谱
  - [ ] 验证session_id
  - [ ] 保存到数据库
  - [ ] 返回菜谱ID
  - [ ] 无session_id返回400

测试命令：
```bash
curl -X POST http://localhost:8000/api/recipes/save \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"name": "测试菜谱", "ingredients": {...}, "steps": [...], "difficulty": "easy", "cooking_time": 30, "servings": 2}'
```

#### 4. 历史记录端点

- [ ] **GET /api/recipes/history**: 成功查询历史
  - [ ] 返回用户的菜谱列表
  - [ ] 支持分页参数
  - [ ] 无session_id返回空列表

测试命令：
```bash
curl http://localhost:8000/api/recipes/history?limit=10&offset=0 \
  -b cookies.txt
```

#### 5. 菜谱详情端点

- [ ] **GET /api/recipes/{recipe_id}**: 成功查询详情
  - [ ] 返回完整菜谱信息
  - [ ] 验证用户权限
  - [ ] 不存在的ID返回404
  - [ ] 无权限返回403

测试命令：
```bash
curl http://localhost:8000/api/recipes/RECIPE_ID \
  -b cookies.txt
```

#### 6. 图片识别端点

- [ ] **POST /api/images/recognize**: 接受图片上传
  - [ ] 验证文件格式（JPEG/PNG/WebP）
  - [ ] 验证文件大小（<10MB）
  - [ ] 保存图片到文件系统
  - [ ] 调用AI识别服务
  - [ ] 不支持的格式返回400

测试命令：
```bash
curl -X POST http://localhost:8000/api/images/recognize \
  -F "file=@test_image.jpg"
```

### 功能验证

#### 会话管理

- [ ] 首次访问自动创建用户和会话
- [ ] session_id存储在HttpOnly Cookie中
- [ ] 会话验证正常工作
- [ ] 无效会话自动创建新会话

#### 数据持久化

- [ ] 用户数据正确保存到数据库
- [ ] 菜谱数据正确保存到数据库
- [ ] 用户与菜谱关联正确
- [ ] 查询操作返回正确数据

#### 错误处理

- [ ] 参数验证错误返回400
- [ ] 资源不存在返回404
- [ ] 权限错误返回403
- [ ] 服务器错误返回500
- [ ] 错误信息友好且有意义
- [ ] 所有错误都有日志记录

#### 安全性

- [ ] Cookie设置为HttpOnly
- [ ] Cookie设置为SameSite=lax
- [ ] CORS配置正确
- [ ] 用户只能访问自己的菜谱
- [ ] 文件上传有大小限制
- [ ] 文件上传有格式限制

### API文档

- [ ] **Swagger UI**: http://localhost:8000/docs 可访问
- [ ] **ReDoc**: http://localhost:8000/redoc 可访问
- [ ] 所有端点都有文档
- [ ] 请求/响应模型正确显示

### 日志系统

- [ ] 应用启动日志正常
- [ ] 请求日志正常记录
- [ ] 错误日志正常记录
- [ ] 日志级别配置正确

## 自动化测试

运行测试脚本验证所有功能：

```bash
python test_api.py
```

预期输出：
```
==================================================
开始测试后端API
==================================================

=== 测试健康检查 ===
状态码: 200
✓ 健康检查通过

=== 测试菜谱生成 ===
状态码: 200
菜谱名称: XXX
✓ 菜谱生成成功

=== 测试菜谱保存 ===
状态码: 200
✓ 菜谱保存成功

=== 测试历史记录 ===
状态码: 200
✓ 历史记录查询成功

=== 测试菜谱详情 ===
状态码: 200
✓ 菜谱详情查询成功

==================================================
所有测试完成！
==================================================
```

## 问题排查

如果验证失败，请检查：

1. **服务器未启动**: 确保 `python main.py` 正在运行
2. **端口冲突**: 检查8000端口是否被占用
3. **数据库错误**: 删除dev.db重新创建
4. **API密钥错误**: 检查.env中的LLM_API_KEY
5. **依赖缺失**: 重新运行 `pip install -r requirements.txt`
6. **导入错误**: 确保在backend目录下运行

## 验证完成标准

所有以下条件都满足时，后端验证通过：

✅ 服务器成功启动，无错误
✅ 所有API端点返回正确状态码
✅ 数据库操作正常
✅ 会话管理正常
✅ 错误处理正确
✅ API文档可访问
✅ 自动化测试全部通过

## 下一步

验证通过后，继续任务9：搭建前端项目基础架构。
