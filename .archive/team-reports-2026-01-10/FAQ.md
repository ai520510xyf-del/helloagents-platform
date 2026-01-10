# HelloAgents Platform 常见问题解答 (FAQ)

本文档收集了用户最常遇到的问题及解决方案。找不到答案？查看[用户指南](./USER_GUIDE.md)或在 [GitHub Discussions](https://github.com/ai520510xyf-del/helloagents-platform/discussions) 提问。

---

## 目录

- [平台使用](#平台使用)
- [代码执行](#代码执行)
- [AI 助手](#ai-助手)
- [学习相关](#学习相关)
- [技术问题](#技术问题)
- [账号与数据](#账号与数据)
- [部署与配置](#部署与配置)

---

## 平台使用

### 需要注册账号吗？

**不需要**。HelloAgents Platform 完全免费，无需注册或登录即可使用所有功能。

**注意**: 当前版本不保存用户数据，刷新页面后学习进度和代码会丢失。未来版本将支持账号系统。

---

### 支持哪些浏览器？

**推荐浏览器**:
- Chrome 120+
- Firefox 120+
- Edge 120+
- Safari 17+

**不支持**:
- Internet Explorer（任何版本）
- 低于推荐版本的旧浏览器

---

### 为什么页面加载很慢？

**可能原因**:
1. **网络问题**: 前端托管在 Cloudflare CDN，后端在 Render
2. **首次访问**: Render 免费实例会在无流量 15 分钟后休眠，首次访问需要 30-60 秒唤醒
3. **地区限制**: 某些地区访问 Cloudflare 或 Render 可能较慢

**解决方案**:
- 首次访问后，后端会保持活跃
- 使用稳定的网络连接
- 考虑本地部署（见[部署指南](./CLOUDFLARE_DEPLOY.md)）

---

### 如何切换课程？

**方法 1**: 点击顶部导航栏的"课程列表"，选择其他课程

**方法 2**: 使用键盘快捷键 `Ctrl/Cmd + ← →` 切换上一课/下一课

**方法 3**: 侧边栏点击课程大纲中的任意课程

---

### 如何保存代码？

**临时保存** (浏览器关闭前):
- 代码自动保存在浏览器本地存储 (localStorage)
- 刷新页面不会丢失

**永久保存** (计划中):
- 未来版本将支持账号系统，自动同步代码到云端

**当前解决方案**:
- 复制代码到本地文本编辑器
- 或使用 `Ctrl/Cmd + S` 触发浏览器下载

---

## 代码执行

### 为什么代码执行失败？

**常见原因与解决方案**:

#### 1. 语法错误
```python
# 错误示例
def run(question):
    return "result"  # 缩进错误

# 正确示例
def run(self, question):
    return "result"
```

**解决**: 检查语法，使用编辑器的语法高亮提示

---

#### 2. 使用禁止的函数
```python
# 错误: 禁止使用 os.system
import os
os.system("ls")

# 错误: 禁止使用 open
with open('file.txt', 'w') as f:
    f.write('data')
```

**解决**: 查看[安全限制](#代码有哪些安全限制)，使用允许的功能

---

#### 3. 超出资源限制
```python
# 错误: 内存溢出
data = [0] * (10 ** 9)  # 需要 8GB 内存，超出限制

# 错误: 执行超时
import time
time.sleep(100)  # 超过 30 秒限制
```

**解决**: 优化算法，避免过度消耗资源

---

### 代码有哪些安全限制？

为了安全，代码沙箱有以下限制：

**禁止的操作**:
- ❌ 系统命令: `os.system`, `subprocess`
- ❌ 动态执行: `eval`, `exec`, `compile`
- ❌ 文件操作: `open`, `file`（除了 `/tmp`）
- ❌ 网络访问: `requests`, `urllib`
- ❌ 用户输入: `input`, `raw_input`

**资源限制**:
- 最大内存: 128 MB
- 最大 CPU: 50% (半核)
- 最大进程数: 64
- 执行超时: 30 秒
- 输出大小: 10 KB

**允许的操作**:
- ✅ Python 标准库（大部分）
- ✅ 数学计算
- ✅ 数据结构操作
- ✅ 字符串处理
- ✅ JSON 解析
- ✅ 打印输出

---

### 可以使用第三方库吗？

**当前版本**: 仅支持 Python 标准库

**可用库**:
```python
import json
import re
import time
import datetime
import collections
import itertools
import functools
import math
import random
```

**不可用库**:
```python
import requests      # ❌ 网络库
import numpy         # ❌ 科学计算
import pandas        # ❌ 数据分析
import torch         # ❌ 深度学习
import openai        # ❌ 第三方 API
```

**未来计划**: 支持常用第三方库的安全子集

---

### 为什么代码执行这么慢？

**正常情况**: 代码执行通常在 0.05-0.5 秒内完成

**如果慢 (> 5 秒)**:
1. **首次执行**: 容器池预热需要 1-2 秒
2. **复杂计算**: 算法时间复杂度高
3. **后端休眠**: Render 免费实例 15 分钟无活动会休眠，首次唤醒需要 30-60 秒

**优化建议**:
- 优化算法复杂度
- 减少循环次数
- 使用更高效的数据结构

---

### 代码输出被截断怎么办？

输出限制为 **10 KB**（约 10000 字符）。

**解决方案**:
```python
# 错误: 输出过多
for i in range(10000):
    print(f"Step {i}: ...")

# 正确: 只打印关键信息
print("开始执行...")
# ... 中间过程不打印
print("执行完成，结果:", result)
```

---

## AI 助手

### AI 助手不工作怎么办？

**可能原因与解决方案**:

#### 1. DeepSeek API 问题
- **症状**: 显示 "AI 助手暂时无法回复"
- **原因**: DeepSeek API 故障或密钥失效
- **解决**: 等待几分钟后重试，或联系管理员

#### 2. 网络问题
- **症状**: 加载图标一直转圈
- **原因**: 网络连接不稳定
- **解决**: 检查网络，刷新页面重试

#### 3. 请求超时
- **症状**: 等待超过 30 秒无响应
- **原因**: AI 推理超时
- **解决**: 刷新页面，缩短问题描述后重试

---

### AI 助手回复不准确？

AI 助手基于 **DeepSeek** 大语言模型，虽然准确率高，但不是 100% 准确。

**提高准确率的方法**:

#### 1. 提供充分上下文
```
❌ 不好: "这是什么？"
✅ 好: "ReAct Agent 的 Thought-Action-Observation 循环是什么？"
```

#### 2. 明确你的问题
```
❌ 不好: "我的代码有问题"
✅ 好: "我在实现 run() 方法时遇到 AttributeError，错误在第 10 行"
```

#### 3. 分步骤提问
```
❌ 不好: "教我从零实现一个完整的 Agent 系统"
✅ 好:
  - "ReAct Agent 的基本结构是什么？"
  - "如何实现 Thought-Action 解析？"
  - "如何处理终止条件？"
```

---

### AI 助手能看到我的代码吗？

**是的**。当你提问时，系统会自动将你的代码发送给 AI 助手作为上下文，帮助 AI 更好地回答问题。

**隐私说明**:
- 代码仅用于 AI 推理，不会被保存或分享
- AI 对话记录保存在本地浏览器，服务器不持久化

---

### 如何清除 AI 对话历史？

**方法 1**: 刷新页面（`F5` 或 `Ctrl/Cmd + R`）

**方法 2**: 清除浏览器缓存

**注意**: 清除后无法恢复对话历史

---

## 学习相关

### 零基础能学会吗？

**可以，但需要具备**:
- Python 基础语法（变量、函数、类、循环）
- 基本的编程思维
- 耐心和毅力

**如果完全零基础**:
1. 先学习 Python 基础（推荐 1-2 周）
   - 推荐资源: [Python 官方教程](https://docs.python.org/zh-cn/3/tutorial/)
2. 再开始学习 Agent 开发

---

### 需要多长时间学完？

**取决于你的基础和投入**:

| 基础水平 | 每周时间 | 预计完成 |
|---------|---------|---------|
| 零基础 | 5-10 小时 | 2-3 个月 |
| Python 基础 | 10-15 小时 | 1-2 个月 |
| 有开发经验 | 15-20 小时 | 3-4 周 |

---

### 课程顺序可以跳跃吗？

**不推荐**。课程设计是循序渐进的，后续课程依赖前面的知识。

**例外情况**:
- 如果你已经熟悉某些概念，可以快速浏览
- 实战项目（第 13-16 章）可以根据兴趣选择

---

### 学完后能找到工作吗？

HelloAgents Platform 提供**基础到中级**的 Agent 开发知识，学完后你将：

**能力**:
- ✅ 理解 AI Agent 核心原理
- ✅ 使用主流框架（LangChain, AutoGPT）
- ✅ 设计和实现 Agent 系统
- ✅ 构建实际应用

**求职建议**:
1. 完成所有实战项目
2. 在 GitHub 展示你的项目
3. 继续深入学习（RAG、Multi-Agent、Fine-tuning）
4. 关注 AI Agent 相关职位

---

## 技术问题

### CORS 错误怎么办？

**错误示例**:
```
Access to fetch at 'https://helloagents-platform.onrender.com/api/...'
from origin 'http://localhost:5173' has been blocked by CORS policy
```

**原因**: 后端 CORS 配置不包含你的前端域名

**解决方案**:

**生产环境**: 不应该遇到此问题（已配置）

**本地开发**:
1. 检查后端 `main.py` 中的 CORS 配置
2. 确保 `allow_origins` 包含 `http://localhost:5173`
3. 重启后端服务

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # 确保包含这一行
        "https://helloagents-platform.pages.dev",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Docker 错误怎么办？

**错误 1**: "Cannot connect to the Docker daemon"

**原因**: Docker 未运行或未安装

**解决**:
```bash
# macOS/Windows: 启动 Docker Desktop
# Linux: 启动 Docker 服务
sudo systemctl start docker
```

---

**错误 2**: "Image not found: python:3.11-slim"

**原因**: Docker 镜像未下载

**解决**:
```bash
docker pull python:3.11-slim
```

---

**错误 3**: "Permission denied"

**原因**: 当前用户无 Docker 权限

**解决** (Linux):
```bash
sudo usermod -aG docker $USER
# 注销后重新登录
```

---

### 如何查看后端日志？

**本地开发**:
```bash
cd backend
python3 run.py
# 日志会直接输出到终端
```

**生产环境**:
- 登录 [Render Dashboard](https://dashboard.render.com/)
- 选择你的服务
- 点击 "Logs" 标签

---

## 账号与数据

### 数据会丢失吗？

**当前版本**: 是的，数据保存在浏览器本地存储 (localStorage)

**数据丢失情况**:
- 清除浏览器缓存
- 使用无痕模式
- 切换浏览器或设备

**备份建议**:
- 定期复制代码到本地文件
- 使用 Git 管理你的代码

**未来版本**: 将支持账号系统，自动同步数据到云端

---

### 如何导出学习记录？

**当前版本**: 暂不支持导出功能

**临时方案**:
1. 复制代码到本地文本文件
2. 截图保存学习进度
3. 使用浏览器开发者工具导出 localStorage

**未来版本**: 将提供一键导出功能

---

### 是否支持多设备同步？

**当前版本**: 不支持

**未来版本**: 将支持账号登录和多设备同步

---

## 部署与配置

### 如何本地部署？

详见 [README.md](./README.md) 的"快速开始 - 方式 2：本地运行"

**简要步骤**:
```bash
# 1. 后端
cd backend
pip install -r requirements.txt
python3 init_db.py
python3 run.py

# 2. 前端
cd frontend
npm install
npm run dev
```

---

### 如何配置 DeepSeek API Key？

**本地开发**:
```bash
cd backend
cp .env.example .env
# 编辑 .env 文件
echo "DEEPSEEK_API_KEY=sk-xxxxx" >> .env
```

**生产环境** (Render):
1. 登录 [Render Dashboard](https://dashboard.render.com/)
2. 选择你的服务
3. 进入 "Environment" 标签
4. 添加环境变量: `DEEPSEEK_API_KEY=sk-xxxxx`

**获取 API Key**:
1. 访问 [DeepSeek Platform](https://platform.deepseek.com/)
2. 注册/登录
3. 进入 [API Keys 页面](https://platform.deepseek.com/api_keys)
4. 创建新密钥

---

### 如何部署到 Cloudflare Pages？

详见 [CLOUDFLARE_DEPLOY.md](./CLOUDFLARE_DEPLOY.md)

**简要步骤**:
1. Fork 仓库到你的 GitHub
2. 登录 [Cloudflare Pages](https://pages.cloudflare.com/)
3. 连接 GitHub 仓库
4. 配置构建设置:
   - 构建命令: `npm run build`
   - 输出目录: `dist`
5. 部署

---

### 如何部署到 Render？

**简要步骤**:
1. 登录 [Render](https://render.com/)
2. 创建新的 Web Service
3. 连接 GitHub 仓库
4. 配置:
   - 构建命令: `pip install -r requirements.txt`
   - 启动命令: `python3 run.py`
5. 添加环境变量（`DEEPSEEK_API_KEY` 等）
6. 部署

---

## 还有其他问题？

### 获取帮助的途径

1. **查看文档**:
   - [用户指南](./USER_GUIDE.md)
   - [API 文档](./API.md)
   - [架构文档](./ARCHITECTURE.md)
   - [贡献指南](./CONTRIBUTING.md)

2. **社区支持**:
   - [GitHub Discussions](https://github.com/ai520510xyf-del/helloagents-platform/discussions) - 提问和讨论
   - [GitHub Issues](https://github.com/ai520510xyf-del/helloagents-platform/issues) - 报告 bug

3. **向 AI 助手提问**:
   - 平台内置的 AI 助手可以回答大部分问题

---

### 如何报告 Bug？

1. 访问 [GitHub Issues](https://github.com/ai520510xyf-del/helloagents-platform/issues)
2. 点击 "New Issue"
3. 选择 "Bug Report"
4. 填写详细信息（见 [CONTRIBUTING.md](./CONTRIBUTING.md)）

---

### 如何提出功能建议？

1. 访问 [GitHub Issues](https://github.com/ai520510xyf-del/helloagents-platform/issues)
2. 点击 "New Issue"
3. 选择 "Feature Request"
4. 描述你的想法

---

## 更新记录

### v1.0.0 (2026-01-09)
- 初始版本发布
- 50+ 课程内容
- 代码沙箱执行
- AI 助手集成
- 容器池性能优化

---

**文档版本**: v1.0.0
**最后更新**: 2026-01-09

找不到答案？在 [GitHub Discussions](https://github.com/ai520510xyf-del/helloagents-platform/discussions) 提问！
