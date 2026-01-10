# HelloAgents Platform 用户使用指南

**AI Agent 互动学习平台** - 从零开始学习 Agent 开发

欢迎来到 HelloAgents Platform！本指南将帮助你快速上手，充分利用平台的所有功能。

**在线访问**: [https://helloagents-platform.pages.dev](https://helloagents-platform.pages.dev)

---

## 目录

- [快速入门](#快速入门)
- [平台功能](#平台功能)
  - [课程学习](#课程学习)
  - [代码编辑](#代码编辑)
  - [AI 助手](#ai-助手)
  - [学习进度](#学习进度)
- [学习路径](#学习路径)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)
- [技巧与提示](#技巧与提示)

---

## 快速入门

### 第一步：访问平台

打开浏览器访问：[https://helloagents-platform.pages.dev](https://helloagents-platform.pages.dev)

无需注册或登录，即可立即开始学习！

---

### 第二步：选择课程

在首页，你会看到完整的课程列表，按章节组织：

```
第一章 初识智能体
第二章 智能体发展史
第三章 大语言模型基础
第四章 智能体经典范式构建
  └─ 4.1 ReAct Agent
  └─ 4.2 Plan-and-Solve Agent
  └─ 4.3 Reflection Agent
...
```

**建议**: 如果你是初学者，从第一章开始按顺序学习。

---

### 第三步：开始学习

点击任意课程进入学习页面，页面分为三个区域：

```
┌─────────────────────────────────────────┬──────────────────────┐
│                                         │                      │
│         课程内容 (Markdown)               │    代码编辑器         │
│                                         │                      │
│  - 概念讲解                               │  编写你的代码         │
│  - 代码示例                               │                      │
│  - 练习任务                               │  [运行代码] 按钮      │
│                                         │                      │
│                                         │    执行结果          │
│                                         │                      │
├─────────────────────────────────────────┴──────────────────────┤
│                                                                │
│                   AI 助手（底部）                                │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

### 第四步：动手实践

1. **阅读课程内容**：理解核心概念
2. **查看代码示例**：学习实现方式
3. **编写代码**：在右侧编辑器中完成练习
4. **运行测试**：点击"运行代码"按钮
5. **查看结果**：检查输出是否符合预期

---

### 第五步：获取帮助

遇到困难？点击底部的 AI 助手，输入你的问题：

```
你: 什么是 ReAct Agent？
AI: ReAct Agent 是一种结合推理（Reasoning）和行动（Acting）的智能体范式...

你: 我的代码为什么报错？
AI: 让我看看你的代码...（AI 会根据你的代码提供建议）
```

---

## 平台功能

### 课程学习

#### 课程结构

每个课程包含：
- **学习目标**：本课要掌握的知识点
- **概念讲解**：理论知识和背景
- **代码示例**：带注释的完整示例
- **动手练习**：实践任务
- **测试验证**：检验学习成果
- **总结回顾**：关键要点梳理

#### 课程导航

```
← 上一课  |  课程目录  |  下一课 →
```

- 使用顶部导航栏快速切换课程
- 侧边栏显示课程大纲
- 完成当前课程后自动解锁下一课

---

### 代码编辑

#### 编辑器功能

HelloAgents 使用 **Monaco Editor**（VS Code 同款编辑器），提供：

**基础功能**:
- 语法高亮
- 自动补全
- 括号匹配
- 代码折叠
- 行号显示

**快捷键** (与 VS Code 相同):
- `Ctrl/Cmd + S`: 保存代码
- `Ctrl/Cmd + Z`: 撤销
- `Ctrl/Cmd + Shift + Z`: 重做
- `Ctrl/Cmd + /`: 注释/取消注释
- `Ctrl/Cmd + F`: 查找
- `Ctrl/Cmd + H`: 替换

---

#### 代码模板

每个课程都提供初始代码模板，帮助你快速开始：

```python
class ReActAgent:
    def __init__(self, llm_client, tool_executor):
        # TODO: 实现初始化逻辑
        pass

    def run(self, question: str) -> str:
        # TODO: 实现 ReAct 循环
        pass
```

**提示**: 按照注释提示完成代码，不要删除已有的结构。

---

#### 运行代码

点击"运行代码"按钮，你的代码将在**安全沙箱**中执行：

**执行流程**:
```
你的代码 → 安全检查 → Docker 容器 → 执行 → 返回结果
```

**执行时间**: 通常在 0.1-0.5 秒内完成

**限制**:
- 最大执行时间: 30 秒
- 最大内存: 128 MB
- 不支持网络访问
- 不支持文件系统操作（除了 `/tmp`）

---

#### 查看结果

代码执行后，会显示两种结果：

**成功**:
```
✅ 执行成功 (0.12s)

输出:
Hello, Agent!
ReAct循环开始...
步骤 1: Thought...
步骤 2: Action...
最终答案: ...
```

**错误**:
```
❌ 执行失败 (0.05s)

错误:
Traceback (most recent call last):
  File "<string>", line 5, in <module>
NameError: name 'undefined_var' is not defined
```

**提示**: 根据错误信息调试代码，或向 AI 助手求助。

---

### AI 助手

#### 如何使用

1. **点击底部的"AI 助手"按钮**
2. **输入你的问题**
3. **等待 AI 回复**（通常 2-5 秒）
4. **继续对话**（AI 会记住上下文）

---

#### AI 助手功能

**概念解释**:
```
你: 什么是 Thought-Action-Observation 循环？
AI: 这是 ReAct Agent 的核心机制...
```

**代码辅导**:
```
你: 我不知道如何实现 run() 方法
AI: 让我给你一些提示：
1. 首先，使用 for 循环控制最大步数
2. 然后，在每一步中...
```

**错误诊断**:
```
你: 我的代码报 AttributeError
AI: 看起来你的对象没有这个属性，检查一下...
```

**最佳实践**:
```
你: 如何优化我的 Agent？
AI: 有几个优化建议：
1. 添加结果缓存
2. 优化 Prompt
3. 实现早停机制
```

---

#### AI 助手上下文

AI 助手会自动感知：
- **当前课程**：了解你在学什么
- **你的代码**：可以分析你的实现
- **对话历史**：记住之前的讨论

**示例**:
```
你: 解释一下 ReAct
AI: ReAct 是...（基于当前课程 4.1）

你: 我的代码有问题
AI: 让我看看你的代码...（自动读取编辑器内容）

你: 那第二个问题呢？
AI: 刚才你问的是...（记住对话历史）
```

---

### 学习进度

#### 进度跟踪

平台会自动记录你的学习进度：

```
你的学习进度: 8/50 (16%)

已完成课程:
✅ 第一章 初识智能体
✅ 第二章 智能体发展史
✅ 4.1 ReAct Agent
...

当前课程:
🚧 4.2 Plan-and-Solve Agent
```

---

#### 代码提交历史

每次运行代码都会保存记录：

```
提交历史:
2026-01-09 14:30  4.1 ReAct Agent    ✅ 成功  0.12s
2026-01-09 14:25  4.1 ReAct Agent    ❌ 失败  0.05s
2026-01-09 14:20  3.3 LLM 集成       ✅ 成功  0.18s
```

**功能**:
- 查看历史代码
- 对比不同版本
- 回滚到之前的版本

---

## 学习路径

### 初学者路径 (0 基础)

**目标**: 理解 Agent 基本概念，实现简单 Agent

```
第一章 初识智能体（1 课时）
  ↓
第二章 智能体发展史（1 课时）
  ↓
第三章 大语言模型基础（2 课时）
  ↓
第四章 智能体经典范式构建（5 课时）
  ├─ 4.1 ReAct Agent ⭐ 重点
  ├─ 4.2 Plan-and-Solve Agent
  └─ 4.3 Reflection Agent
  ↓
第五章 低代码平台搭建（3 课时）
```

**预计时间**: 2-3 周（每周 5-10 小时）

---

### 进阶路径 (有基础)

**目标**: 掌握高级技术，构建生产级 Agent

```
第六章 框架开发实践（4 课时）
  ├─ 6.1 LangChain 实践 ⭐ 重点
  ├─ 6.2 AutoGPT 实践
  └─ 6.3 AgentGPT 实践
  ↓
第七章 构建你的 Agent 框架（5 课时）
  ├─ 7.1 设计模式
  ├─ 7.2 工具系统
  └─ 7.3 Memory 管理
  ↓
第八章 记忆与检索（4 课时）
  ↓
第九章 上下文工程（3 课时）
```

**预计时间**: 3-4 周（每周 10-15 小时）

---

### 实战路径 (项目实战)

**目标**: 完成端到端的 Agent 应用

```
第十三章 智能旅行助手（项目）
  ├─ 需求分析
  ├─ 系统设计
  ├─ 功能实现
  └─ 测试部署
  ↓
第十四章 自动化深度研究智能体（项目）
  ↓
第十五章 构建赛博小镇（高级项目）
  ↓
第十六章 毕业设计（自定义项目）
```

**预计时间**: 4-6 周（每周 15-20 小时）

---

## 最佳实践

### 高效学习方法

#### 1. 主动学习

**不要**:
- ❌ 只看课程内容，不动手实践
- ❌ 直接复制粘贴示例代码
- ❌ 遇到错误就放弃

**应该**:
- ✅ 先理解概念，再看代码
- ✅ 自己实现，再对比示例
- ✅ 遇到错误时尝试调试

---

#### 2. 循序渐进

```
理解概念 → 阅读示例 → 动手实践 → 测试验证 → 总结反思
```

**每个步骤都不要跳过！**

---

#### 3. 及时求助

遇到困难超过 15 分钟？向 AI 助手求助！

**好的提问**:
```
我在实现 ReAct Agent 的 run() 方法时遇到问题。
我的代码在第 10 行报 AttributeError: 'NoneType' object has no attribute 'think'。
我的思路是...
```

**不好的提问**:
```
代码报错了，怎么办？
```

---

#### 4. 总结归纳

每完成一个课程，花 5 分钟总结：
- 学到了什么？
- 核心要点是什么？
- 如何应用到实际项目？

**示例总结**:
```
4.1 ReAct Agent 总结:

核心概念:
- Thought-Action-Observation 循环
- 结合推理和行动
- 循环控制和终止条件

实现要点:
1. 初始化 LLM 和工具执行器
2. 实现循环逻辑（最大步数控制）
3. 解析 LLM 输出的 Action
4. 执行工具并收集 Observation
5. 检查终止条件

下一步:
学习 Plan-and-Solve，对比两种范式的差异
```

---

### 代码编写技巧

#### 1. 使用有意义的变量名

**不好**:
```python
def run(self, q):
    for i in range(self.m):
        t = self.llm.think(q, self.h)
        a = self.parse(t)
        o = self.tool.exec(a)
        self.h.append((t, a, o))
```

**好**:
```python
def run(self, question):
    for step in range(self.max_steps):
        thought = self.llm.think(question, self.history)
        action = self.parse_action(thought)
        observation = self.tool.execute(action)
        self.history.append((thought, action, observation))
```

---

#### 2. 添加必要的注释

```python
def run(self, question: str) -> str:
    """
    执行 ReAct 循环

    Args:
        question: 用户问题

    Returns:
        最终答案
    """
    for step in range(self.max_steps):
        # 1. Thought: LLM 推理思考
        thought = self.llm.think(question, self.history)

        # 2. Action: 解析并执行工具
        action = self.parse_action(thought)
        observation = self.tool.execute(action)

        # 3. 记录历史
        self.history.append((thought, action, observation))

        # 4. 检查终止条件
        if self.is_final_answer(thought):
            return thought

    return "达到最大步数限制"
```

---

#### 3. 处理边界情况

```python
def parse_action(self, thought: str) -> dict:
    """解析 LLM 输出的 Action"""

    # 边界情况: thought 为空
    if not thought:
        return {"tool": "none", "input": ""}

    # 边界情况: 无法解析
    if "Action:" not in thought:
        return {"tool": "none", "input": thought}

    # 正常解析
    action_part = thought.split("Action:")[1].strip()
    ...
```

---

## 常见问题

### 代码执行相关

#### Q: 代码执行超时怎么办？

**A**: 检查代码是否有死循环或耗时操作。执行时间限制为 30 秒。

```python
# 错误: 死循环
while True:
    pass

# 正确: 使用循环控制
for step in range(max_steps):
    ...
```

---

#### Q: 为什么不能使用 `open()` 读写文件？

**A**: 为了安全，代码沙箱禁止文件操作。如果需要临时存储，使用内存数据结构（如列表、字典）。

```python
# 错误: 禁止文件操作
with open('data.txt', 'w') as f:
    f.write('hello')

# 正确: 使用内存存储
data = []
data.append('hello')
```

---

#### Q: 可以使用第三方库吗？

**A**: 目前仅支持 Python 标准库。常用的第三方库（如 `requests`, `numpy`）暂不支持。

**可用**:
- `json`, `re`, `time`, `datetime`, `collections`, etc.

**不可用**:
- `requests`, `numpy`, `pandas`, `torch`, etc.

---

### AI 助手相关

#### Q: AI 助手回复很慢？

**A**: AI 推理需要时间，通常 2-5 秒。如果超过 10 秒，请刷新页面重试。

---

#### Q: AI 助手给出错误答案？

**A**: AI 助手基于 DeepSeek 模型，虽然准确率高，但不是 100% 准确。建议：
1. 多问几个问题，从不同角度理解
2. 对比课程内容和示例代码
3. 在社区讨论区求助

---

#### Q: 如何清除 AI 对话历史？

**A**: 刷新页面即可清除对话历史，重新开始对话。

---

### 学习相关

#### Q: 我是零基础，能学会吗？

**A**: 可以！课程从零开始，循序渐进。但需要：
- 基本的 Python 语法知识
- 逻辑思维能力
- 耐心和毅力

**建议**: 如果完全没有编程基础，先学习 Python 基础（1-2 周），再来学习 Agent 开发。

---

#### Q: 需要多久才能学完？

**A**: 取决于你的基础和投入时间：
- **初学者**: 2-3 个月（每周 5-10 小时）
- **有基础**: 1-2 个月（每周 10-15 小时）
- **快速通关**: 3-4 周（每周 20+ 小时）

---

#### Q: 学完后能做什么？

**A**: 你将能够：
- 理解 AI Agent 的核心原理
- 使用主流框架（LangChain, AutoGPT）
- 设计和实现自己的 Agent 系统
- 构建实际应用（聊天机器人、自动化助手等）

---

## 技巧与提示

### 键盘快捷键

**编辑器**:
- `Ctrl/Cmd + Enter`: 运行代码
- `Ctrl/Cmd + S`: 保存代码
- `Ctrl/Cmd + /`: 注释行
- `Alt + 上/下`: 移动行
- `Ctrl/Cmd + D`: 选择下一个匹配

**页面导航**:
- `Ctrl/Cmd + ← →`: 切换课程
- `Esc`: 关闭 AI 助手

---

### 浏览器建议

**推荐浏览器**:
- Chrome 120+
- Firefox 120+
- Edge 120+
- Safari 17+

**不推荐**:
- IE（不支持）
- 旧版浏览器

---

### 学习资源

**官方文档**:
- [API 文档](./API.md)
- [架构文档](./ARCHITECTURE.md)
- [贡献指南](./CONTRIBUTING.md)

**社区**:
- [GitHub Discussions](https://github.com/ai520510xyf-del/helloagents-platform/discussions)
- [GitHub Issues](https://github.com/ai520510xyf-del/helloagents-platform/issues)

**相关资源**:
- [LangChain 官方文档](https://python.langchain.com/)
- [OpenAI API 文档](https://platform.openai.com/docs)
- [DeepSeek 平台](https://platform.deepseek.com/)

---

## 获取帮助

遇到问题？按以下顺序获取帮助：

1. **查看 [FAQ](./FAQ.md)**
2. **向 AI 助手提问**
3. **搜索 [GitHub Issues](https://github.com/ai520510xyf-del/helloagents-platform/issues)**
4. **在 [Discussions](https://github.com/ai520510xyf-del/helloagents-platform/discussions) 提问**
5. **提交新的 [Issue](https://github.com/ai520510xyf-del/helloagents-platform/issues/new)**

---

## 结语

HelloAgents Platform 是一个持续进化的学习平台。我们会根据用户反馈不断改进课程内容和功能。

**祝你学习愉快，成为 Agent 开发高手！** 🚀

---

**文档版本**: v1.0.0
**最后更新**: 2026-01-09

有任何建议或反馈？欢迎在 [GitHub](https://github.com/ai520510xyf-del/helloagents-platform) 告诉我们！
