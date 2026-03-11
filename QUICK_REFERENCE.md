# 去学厨房 - 快速参考卡

## 🚀 快速启动

```bash
# 终端1: 后端
cd backend && python main.py

# 终端2: 前端
cd frontend && npm run dev

# 浏览器
http://localhost:5173
```

## 📊 功能概览

| 模式 | 功能 | 状态 |
|------|------|------|
| 🤖 AI对话 | 实时问答 | ✅ 完成 |
| 📚 技巧知识库 | 52个课程 | ✅ 完成 |
| 🎯 实时指导 | 步骤导航 | ✅ 完成 |
| 🔍 问题诊断 | AI诊断 | ✅ 完成 |

## 🧪 快速测试

```bash
# 测试AI功能
cd backend
python test_cooking_ai.py
```

## 📁 关键文件

### 前端
- `CookingSchoolView.vue` - 主视图
- `SkillDetailModal.vue` - 技巧详情

### 后端
- `cooking.py` - 路由
- `ai_service.py` - AI服务

### API
- `POST /api/cooking/ask` - 问答
- `POST /api/cooking/diagnose` - 诊断

## 🎓 课程内容

- 🔪 刀工基础: 8课程
- 🔥 火候掌握: 6课程
- 🧂 调味技巧: 10课程
- 🥘 烹饪方法: 12课程
- 🥩 食材处理: 9课程
- 🍜 汤品制作: 7课程

**总计: 52个详细课程**

## ⚠️ 故障排除

### AI返回备用答案？
1. 运行 `python test_cooking_ai.py`
2. 检查 `backend/.env` 配置
3. 查看后端日志
4. 验证API Key

### 技巧知识库无反应？
- 确保使用最新代码
- 检查浏览器控制台

### 前端连接失败？
- 确认后端运行在 8000 端口
- 检查CORS配置

## 📖 完整文档

1. `完成报告.md` - 中文总结 ⭐
2. `COOKING_SCHOOL_SUMMARY.md` - 功能说明
3. `TESTING_GUIDE.md` - 测试指南
4. `COOKING_SCHOOL_COMPLETE.md` - 技术文档

## ✅ 测试清单

- [ ] AI对话工作正常
- [ ] 技巧知识库可以打开
- [ ] 实时指导可以导航
- [ ] 问题诊断可以使用
- [ ] 所有52个课程可访问

## 🎯 成功标志

✅ AI回答详细且相关（不是备用答案）  
✅ 技巧模态框正常打开和关闭  
✅ 步骤导航流畅  
✅ 诊断结果详细  

## 💡 提示

- 先测试AI功能脚本
- 查看后端日志了解API状态
- 使用测试指南进行全面测试
- 遇到问题查看完整文档

---

**状态**: 🟢 所有功能完成，可以使用

**建议**: 阅读 `完成报告.md` 了解详情
