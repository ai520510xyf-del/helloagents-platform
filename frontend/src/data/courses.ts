/**
 * Hello-Agents 真实课程数据
 * 基于 Datawhale Hello-Agents 项目
 * 链接：https://github.com/datawhalechina/hello-agents
 */

export interface Lesson {
  id: string;
  chapter: number;
  title: string;
  status: 'completed' | 'current' | 'available';
  codeTemplate: string;
  description: string;
  content: string; // 课程理论知识内容（Markdown 格式）
}

export interface Chapter {
  id: number;
  title: string;
  part: string; // 所属部分
  lessons: Lesson[];
}

// 真实的 Hello-Agents 16章课程
export const allChapters: Chapter[] = [
  // ===== 第一部分：智能体与语言模型基础 =====
  {
    id: 1,
    title: '初识智能体',
    part: '第一部分：智能体与语言模型基础',
    lessons: [
      {
        id: '1',
        chapter: 1,
        title: '第一章 初识智能体',
        status: 'completed',
        description: '智能体定义、类型、范式与应用',
        content: `# 第一章 初识智能体

欢迎来到智能体的世界！在人工智能浪潮席卷全球的今天，**智能体（Agent）**已成为驱动技术变革与应用创新的核心概念之一。

## 📚 本章学习目标

- 理解智能体的基本定义和核心要素
- 掌握智能体的分类方式和类型特征
- 了解智能体的运行机制和交互协议
- 动手实现第一个简单的智能体

## 1.1 什么是智能体？

在人工智能领域，智能体被定义为任何能够通过**传感器（Sensors）**感知其所处**环境（Environment）**，并**自主**地通过**执行器（Actuators）**采取**行动（Action）**以达成特定目标的实体。

### 智能体的四个基本要素：

1. **环境（Environment）**：智能体所处的外部世界
2. **传感器（Sensors）**：感知环境状态的能力
3. **执行器（Actuators）**：改变环境状态的工具
4. **自主性（Autonomy）**：独立决策的能力

### 1.1.1 传统视角下的智能体

智能体的演进路径展现了从简单到复杂的发展轨迹：

**1. 反射智能体（Simple Reflex Agent）**
- 决策核心：条件-动作规则
- 特点：快速响应，但缺乏记忆
- 例子：自动恒温器

**2. 基于模型的反射智能体（Model-Based Reflex Agent）**
- 核心能力：拥有世界模型，可追踪环境状态
- 特点：具备初级"记忆"
- 例子：隧道中的自动驾驶汽车

**3. 基于目标的智能体（Goal-Based Agent）**
- 核心能力：主动规划达成目标的路径
- 特点：具有预见性
- 例子：GPS导航系统

**4. 基于效用的智能体（Utility-Based Agent）**
- 核心能力：权衡多个目标，最大化效用
- 特点：处理复杂决策
- 例子：多目标路径规划

**5. 学习型智能体（Learning Agent）**
- 核心能力：通过经验自我改进
- 特点：不依赖预设知识
- 例子：AlphaGo Zero

### 1.1.2 大语言模型驱动的新范式

以 **GPT** 为代表的大语言模型的出现，正在显著改变智能体的构建方法与能力边界：

| 维度 | 传统智能体 | LLM 智能体 |
|------|-----------|-----------|
| 核心引擎 | 规则引擎/符号推理 | 大语言模型 |
| 知识来源 | 显式编程 | 海量数据预训练 |
| 交互方式 | 结构化指令 | 自然语言 |
| 规划能力 | 预设算法 | 涌现能力 |

**LLM 智能体的核心能力：**

1. **规划与推理**：将高层级目标分解为子任务
2. **工具使用**：主动调用外部工具补全信息
3. **动态修正**：根据反馈调整行为

## 1.2 智能体的运行机制

### 核心循环：Perception → Thought → Action → Observation

\`\`\`
感知（Perception）→ 思考（Thought）→ 行动（Action）→ 观察（Observation）
      ↑                                                            ↓
      └────────────────────────────────────────────────────────────┘
\`\`\`

**1. 感知（Perception）**
- 通过传感器接收环境输入
- 获取观察信息（Observation）

**2. 思考（Thought）**
- **规划（Planning）**：制定行动计划
- **工具选择（Tool Selection）**：选择合适的工具

**3. 行动（Action）**
- 调用工具或执行操作
- 对环境施加影响

**4. 观察（Observation）**
- 获取行动结果反馈
- 作为下一轮循环的输入

### 交互协议示例

\`\`\`
Thought: 用户想知道北京的天气。我需要调用天气查询工具。
Action: get_weather("北京")
Observation: 北京当前天气为晴，气温25摄氏度，微风。
\`\`\`

## 1.3 动手体验：第一个智能体

让我们构建一个**智能旅行助手**，它能够：
1. 查询天气
2. 根据天气推荐景点

### 核心步骤：

**1. 准备工具函数**
\`\`\`python
def get_weather(city: str) -> str:
    # 调用天气 API
    return f"{city}当前天气: 晴，气温25°C"

def get_attraction(city: str, weather: str) -> str:
    # 搜索推荐景点
    return "推荐：颐和园（适合晴天游览）"
\`\`\`

**2. 设计 Prompt 模板**
\`\`\`python
AGENT_SYSTEM_PROMPT = """
你是智能旅行助手。格式要求：

Thought: [思考过程]
Action: [function_name(arg="value")]

完成时使用：finish(answer="最终答案")
"""
\`\`\`

**3. 运行 Agent 循环**
\`\`\`python
for i in range(5):  # 最多5轮
    # 1. 调用 LLM 思考
    llm_output = llm.generate(prompt, system_prompt)

    # 2. 解析 Action
    action = parse_action(llm_output)

    # 3. 执行工具
    observation = execute_tool(action)

    # 4. 添加到历史
    prompt_history.append(f"Observation: {observation}")
\`\`\`

## 🎯 重点概念总结

### Workflow vs Agent

| 特征 | Workflow | Agent |
|------|---------|--------|
| 核心 | 预设流程 | 目标导向 |
| 决策 | 确定性规则 | 自主推理 |
| 灵活性 | 固定路径 | 动态调整 |
| 适用场景 | 规范化任务 | 开放式问题 |

### 关键要点

✅ **智能体 = 感知 + 推理 + 行动 + 自主性**
✅ **LLM 是智能体的"大脑"，负责规划和决策**
✅ **Thought-Action-Observation 是核心交互范式**
✅ **工具使用能力让智能体连接真实世界**

## 📖 延伸阅读

- 《Artificial Intelligence: A Modern Approach》 - Russell & Norvig
- 《Thinking, Fast and Slow》 - Daniel Kahneman
- Datawhale Hello-Agents 完整教程：https://github.com/datawhalechina/hello-agents

---

**🎓 学习建议**

1. 先理解概念，再动手实践
2. 尝试修改代码，观察结果变化
3. 思考如何改进智能体的性能
4. 记录学习过程中的问题和想法

准备好了吗？让我们开始编写第一个智能体吧！👇
`,
        codeTemplate: `# Hello-Agents - 第一章：初识智能体

"""
第一个简单的 Agent 实现
代码位置：hello-agents/code/chapter1/FirstAgentTest.py
"""

from anthropic import Anthropic
import os

# 初始化 LLM 客户端
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def simple_agent(user_message: str):
    """
    最简单的 Agent 实现

    Args:
        user_message: 用户输入

    Returns:
        Agent 的响应
    """
    print(f"用户: {user_message}")

    # 调用 LLM
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": user_message}
        ]
    )

    answer = response.content[0].text
    print(f"Agent: {answer}")

    return answer

# 测试代码
if __name__ == "__main__":
    print("=== Hello-Agents 第一章：初识智能体 ===")
    print("这是你的第一个 Agent！\\n")

    simple_agent("你好，请介绍一下什么是AI Agent？")
`
      }
    ]
  },
  {
    id: 2,
    title: '智能体发展史',
    part: '第一部分：智能体与语言模型基础',
    lessons: [
      {
        id: '2',
        chapter: 2,
        title: '第二章 智能体发展史',
        status: 'available',
        description: '从符号主义到 LLM 驱动的智能体演进',
        content: '# 第二章 智能体发展史\n\n从符号主义到 LLM 驱动的智能体演进历程。',
        codeTemplate: '# 第二章内容\n# 完整课程内容开发中...'
      }
    ]
  },
  {
    id: 3,
    title: '大语言模型基础',
    part: '第一部分：智能体与语言模型基础',
    lessons: [
      {
        id: '3',
        chapter: 3,
        title: '第三章 大语言模型基础',
        status: 'available',
        description: 'Transformer、提示、主流 LLM 及其局限',
        content: '# 第三章 大语言模型基础\n\nTransformer、提示工程、主流 LLM 及其局限性探讨。',
        codeTemplate: '# 第三章内容\n# 完整课程内容开发中...'
      }
    ]
  },

  // ===== 第二部分：构建你的大语言模型智能体 =====
  {
    id: 4,
    title: '智能体经典范式构建',
    part: '第二部分：构建你的大语言模型智能体',
    lessons: [
      {
        id: '4.1',
        chapter: 4,
        title: '4.1 ReAct 范式',
        status: 'current',
        description: 'Reasoning + Acting - 边思考边行动',
        content: `# 第四章：ReAct 范式

在准备好 LLM 客户端后，我们将构建第一个，也是最经典的一个智能体范式 **ReAct (Reason + Act)**。

## 📚 本节学习目标

- 理解 ReAct 的核心思想和工作流程
- 掌握 Thought-Action-Observation 循环机制
- 学会设计 ReAct 的 Prompt 模板
- 动手实现一个完整的 ReAct Agent

## 4.1 ReAct 是什么？

ReAct 由 Shunyu Yao 于 2022 年提出，其核心思想是模仿人类解决问题的方式，将**推理（Reasoning）**与**行动（Acting）**显式地结合起来，形成一个"思考-行动-观察"的循环。

### 4.1.1 ReAct 的诞生背景

在 ReAct 诞生之前，主流方法分为两类：

**1. 纯思考型（Chain-of-Thought）**
- ✅ 优点：能引导模型进行复杂逻辑推理
- ❌ 缺点：无法与外部世界交互，容易产生幻觉

**2. 纯行动型（Action-Only）**
- ✅ 优点：可以调用工具和 API
- ❌ 缺点：缺乏规划和纠错能力

**ReAct 的巧妙之处**：思考与行动相辅相成
- **思考指导行动** - 明确下一步要做什么
- **行动修正思考** - 基于结果调整策略

## 4.2 ReAct 的工作流程

ReAct 通过特殊的 Prompt 工程引导模型，使其每一步的输出都遵循固定轨迹：

\`\`\`
Thought (思考) → Action (行动) → Observation (观察) → 循环
\`\`\`

### 三个核心环节：

**1. Thought（思考）**
- 这是智能体的"内心独白"
- 分析当前情况
- 分解任务
- 制定下一步计划
- 反思上一步的结果

**示例**：
\`\`\`
Thought: 用户想知道华为最新手机的信息。我需要先搜索华为最新款手机型号。
\`\`\`

**2. Action（行动）**
- 智能体决定采取的具体动作
- 通常是调用外部工具
- 格式：\`tool_name[tool_input]\`

**示例**：
\`\`\`
Action: Search["华为最新款手机"]
\`\`\`

**3. Observation（观察）**
- 执行 Action 后从外部工具返回的结果
- 作为下一轮 Thought 的输入

**示例**：
\`\`\`
Observation: 华为最新款手机是 Mate 60 Pro，搭载麒麟 9000S 芯片...
\`\`\`

## 4.3 ReAct 循环示例

让我们看一个完整的 ReAct 执行流程：

**任务**：华为最新的手机是哪一款？它的主要卖点是什么？

### 第 1 轮循环：

\`\`\`
Thought: 我需要先确定华为最新的手机型号
Action: Search["华为最新款手机 2024"]
Observation: 华为最新款手机是 Mate 60 Pro
\`\`\`

### 第 2 轮循环：

\`\`\`
Thought: 现在我知道了最新型号，需要了解它的主要卖点
Action: Search["华为 Mate 60 Pro 主要特点"]
Observation: 主要卖点包括：麒麟 9000S 芯片、卫星通话功能、XMAGE 影像系统
\`\`\`

### 第 3 轮循环：

\`\`\`
Thought: 我已经获得了足够的信息可以回答用户的问题
Action: Finish["华为最新款手机是 Mate 60 Pro，主要卖点是麒麟 9000S 芯片、卫星通话和 XMAGE 影像系统"]
\`\`\`

## 4.4 ReAct 的核心优势

### 1. 推理使行动更具目的性

通过 Thought 环节，智能体能够：
- 明确当前状态
- 分解复杂任务
- 规划下一步行动

### 2. 行动为推理提供事实依据

通过 Observation 环节，智能体能够：
- 获取真实信息
- 避免幻觉问题
- 动态调整策略

### 3. 可解释性强

每一步的 Thought 都是可见的，可以清楚地看到：
- 智能体的思考过程
- 为什么做出某个决策
- 如何从问题到达答案

## 4.5 ReAct Prompt 设计要点

一个好的 ReAct Prompt 应该包括：

### 1. 角色定义
\`\`\`python
你是一个有能力调用外部工具的智能助手。
\`\`\`

### 2. 工具说明
\`\`\`python
可用工具如下：
- Search[query]: 搜索引擎
- Calculator[expression]: 计算器
- Finish[answer]: 输出最终答案
\`\`\`

### 3. 格式要求
\`\`\`python
请严格按照以下格式进行回应：
Thought: [你的思考过程]
Action: [tool_name[tool_input]]
\`\`\`

### 4. 示例演示（Few-shot）
\`\`\`python
示例：
Question: 2的8次方是多少？
Thought: 我需要计算2的8次方
Action: Calculator[2**8]
Observation: 256
Thought: 我已经得到了答案
Action: Finish[256]
\`\`\`

## 4.6 实现 ReAct Agent 的关键步骤

### 步骤 1：设计 Prompt 模板
\`\`\`python
REACT_PROMPT_TEMPLATE = """
你是智能助手，可以调用工具。

可用工具：{tools}

格式要求：
Thought: [思考过程]
Action: [tool_name[input]]

问题：{question}
历史：{history}
"""
\`\`\`

### 步骤 2：实现 Agent 循环
\`\`\`python
class ReActAgent:
    def run(self, question: str):
        for step in range(max_steps):
            # 1. 构建 prompt
            prompt = build_prompt(question, history)

            # 2. 调用 LLM 思考
            response = llm.generate(prompt)

            # 3. 解析 Thought 和 Action
            thought, action = parse_output(response)

            # 4. 执行 Action
            observation = execute_tool(action)

            # 5. 记录到历史
            history.append((thought, action, observation))

            # 6. 判断是否完成
            if action.startswith("Finish"):
                return extract_answer(action)
\`\`\`

### 步骤 3：实现工具调用
\`\`\`python
def execute_tool(action: str):
    tool_name = extract_tool_name(action)
    tool_input = extract_tool_input(action)

    if tool_name == "Search":
        return search_engine(tool_input)
    elif tool_name == "Calculator":
        return calculate(tool_input)
    elif tool_name == "Finish":
        return tool_input
\`\`\`

## 4.7 ReAct 的局限性与改进

### 当前局限：

1. **循环次数限制**
   - 必须设置 max_steps 防止死循环
   - 复杂任务可能需要很多轮

2. **格式解析脆弱**
   - LLM 可能不严格按格式输出
   - 需要鲁棒的解析逻辑

3. **工具调用失败处理**
   - 工具可能返回错误
   - 需要重试和降级机制

### 改进方向：

- **ReAct + Self-Reflection**：添加反思环节
- **ReAct + Planning**：先制定完整计划
- **ReAct + Memory**：记住长期信息

## 🎯 重点概念总结

### ReAct 核心公式

\`\`\`
ReAct = Reasoning（推理）+ Acting（行动）
循环 = Thought → Action → Observation → Thought → ...
\`\`\`

### 关键要点

✅ **ReAct 将思考和行动显式分离并循环**
✅ **Thought 指导 Action，Action 修正 Thought**
✅ **通过 Prompt 工程引导 LLM 遵循固定格式**
✅ **每一步都是可解释的，便于调试**

## 📝 实践建议

1. **先理解流程，再看代码**
   - 画出 Thought-Action-Observation 循环图
   - 手动模拟一次完整流程

2. **从简单任务开始**
   - 先实现单工具调用
   - 再扩展到多工具

3. **关注 Prompt 设计**
   - 格式要求要清晰明确
   - 提供足够的示例

4. **处理异常情况**
   - 工具调用失败
   - 格式解析错误
   - 陷入死循环

---

**准备好了吗？** 让我们开始编写 ReAct Agent 的代码吧！👉

在右侧代码编辑器中，你将看到一个 ReAct Agent 的代码模板。尝试完成 TODO 部分，实现完整的 ReAct 循环！
`,
        codeTemplate: `# Hello-Agents - 第四章：ReAct 范式

import re
from anthropic import Anthropic
import os

REACT_PROMPT_TEMPLATE = """
请注意，你是一个有能力调用外部工具的智能助手。

可用工具如下：
{tools}

请严格按照以下格式进行回应：

Thought: 你的思考过程，用于分析问题、拆解任务和规划下一步行动。
Action: 你决定采取的行动，必须是以下格式之一：
- \`{{tool_name}}[{{tool_input}}]\`：调用一个可用工具。
- \`Finish[最终答案]\`：当你认为已经获得最终答案时。

现在，请开始解决以下问题：
Question: {question}
History: {history}
"""

class ReActAgent:
    """
    ReAct (Reasoning + Acting) Agent 实现
    核心思想：Thought → Action → Observation 循环
    """

    def __init__(self, max_steps: int = 5):
        self.max_steps = max_steps
        self.history = []
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    def run(self, question: str):
        """运行 ReAct 循环"""
        self.history = []
        current_step = 0

        while current_step < self.max_steps:
            current_step += 1
            print(f"\\n--- 第 {current_step} 步 ---")

            # TODO: 实现 ReAct 循环
            # 1. 构建 prompt
            # 2. 调用 LLM 思考
            # 3. 解析 Thought 和 Action
            # 4. 执行 Action
            # 5. 记录 Observation
            # 6. 判断是否结束

            pass

        print("已达到最大步数，流程终止。")
        return None

    def _parse_output(self, text: str):
        """解析 LLM 输出"""
        thought_match = re.search(r"Thought: (.*)", text)
        action_match = re.search(r"Action: (.*)", text)

        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None

        return thought, action

# 测试代码
if __name__ == '__main__':
    print("=== Hello-Agents 第四章：ReAct 范式 ===")
    agent = ReActAgent()
    question = "华为最新的手机是哪一款？它的主要卖点是什么？"
    agent.run(question)
`
      },
      {
        id: '4.2',
        chapter: 4,
        title: '4.2 Plan-and-Solve',
        status: 'available',
        content: '# 4.2 Plan-and-Solve\n\n内容开发中...',
        description: '先规划后执行的智能体范式',
        codeTemplate: `# Hello-Agents - 第四章：Plan-and-Solve 范式

"""
Plan-and-Solve 范式实现
核心思想：Planning（制定计划） → Execution（执行计划）
"""

class PlanAndSolveAgent:
    def __init__(self):
        pass

    def plan(self, question: str):
        """制定执行计划"""
        # TODO: 实现规划逻辑
        pass

    def solve(self, plan: list):
        """按计划执行"""
        # TODO: 实现执行逻辑
        pass

    def run(self, question: str):
        """完整流程"""
        print("=== Plan-and-Solve 范式 ===")

        # 1. Planning 阶段
        plan = self.plan(question)
        print(f"📋 计划: {plan}")

        # 2. Execution 阶段
        result = self.solve(plan)
        print(f"✅ 结果: {result}")

        return result

if __name__ == '__main__':
    agent = PlanAndSolveAgent()
    agent.run("规划一次从北京到上海的旅行")
`
      },
      {
        id: '4.3',
        chapter: 4,
        title: '4.3 Reflection',
        status: 'available',
        content: '# 4.3 Reflection\n\n内容开发中...',
        description: '反思与自我改进的智能体',
        codeTemplate: `# Hello-Agents - 第四章：Reflection 范式

"""
Reflection 范式实现
核心思想：Action → Reflection → Improvement
"""

class ReflectionAgent:
    def __init__(self, max_iterations: int = 3):
        self.max_iterations = max_iterations

    def generate(self, question: str) -> str:
        """生成初步答案"""
        # TODO: 实现答案生成
        pass

    def reflect(self, question: str, answer: str) -> dict:
        """反思答案质量"""
        # TODO: 实现反思逻辑
        # 返回 {'score': 分数, 'issues': 问题列表, 'suggestions': 改进建议}
        pass

    def improve(self, question: str, answer: str, reflection: dict) -> str:
        """根据反思改进答案"""
        # TODO: 实现改进逻辑
        pass

    def run(self, question: str) -> str:
        """完整的反思循环"""
        print("=== Reflection 范式 ===")

        answer = self.generate(question)
        print(f"初始答案: {answer}")

        for i in range(self.max_iterations):
            reflection = self.reflect(question, answer)
            print(f"\\n🤔 反思 {i+1}: {reflection}")

            if reflection['score'] >= 0.8:
                break

            answer = self.improve(question, answer, reflection)
            print(f"改进后: {answer}")

        return answer

if __name__ == '__main__':
    agent = ReflectionAgent()
    agent.run("解释量子计算的基本原理")
`
      }
    ]
  },
  {
    id: 5,
    title: '基于低代码平台的智能体搭建',
    part: '第二部分：构建你的大语言模型智能体',
    lessons: [
      {
        id: '5',
        chapter: 5,
        title: '第五章 低代码平台',
        status: 'available',
        content: '# 第五章 低代码平台\n\n完整课程内容开发中...',
        description: 'Coze、Dify、n8n 等平台使用',
        codeTemplate: '# 第五章内容\n# 完整课程内容开发中...'
      }
    ]
  },
  {
    id: 6,
    title: '框架开发实践',
    part: '第二部分：构建你的大语言模型智能体',
    lessons: [
      {
        id: '6',
        chapter: 6,
        title: '第六章 框架开发',
        status: 'available',
        content: '# 第六章 框架开发\n\n完整课程内容开发中...',
        description: 'AutoGen、AgentScope、LangGraph 等框架',
        codeTemplate: '# 第六章内容\n# 完整课程内容开发中...'
      }
    ]
  },
  {
    id: 7,
    title: '构建你的Agent框架',
    part: '第二部分：构建你的大语言模型智能体',
    lessons: [
      {
        id: '7',
        chapter: 7,
        title: '第七章 自建框架',
        status: 'available',
        content: '# 第七章 自建框架\n\n完整课程内容开发中...',
        description: '从 0 开始构建智能体框架',
        codeTemplate: '# 第七章内容\n# 完整课程内容开发中...'
      }
    ]
  },

  // ===== 第三部分：高级知识扩展 =====
  {
    id: 8,
    title: '记忆与检索',
    part: '第三部分：高级知识扩展',
    lessons: [
      {
        id: '8',
        chapter: 8,
        title: '第八章 记忆与检索',
        status: 'available',
        content: '# 第八章 记忆与检索\n\n完整课程内容开发中...',
        description: '记忆系统、RAG、存储',
        codeTemplate: '# 第八章内容\n# 完整课程内容开发中...'
      }
    ]
  },
  {
    id: 9,
    title: '上下文工程',
    part: '第三部分：高级知识扩展',
    lessons: [
      {
        id: '9',
        chapter: 9,
        title: '第九章 上下文工程',
        status: 'available',
        content: '# 第九章 上下文工程\n\n完整课程内容开发中...',
        description: '持续交互的"情境理解"',
        codeTemplate: '# 第九章内容\n# 完整课程内容开发中...'
      }
    ]
  },
  {
    id: 10,
    title: '智能体通信协议',
    part: '第三部分：高级知识扩展',
    lessons: [
      {
        id: '10',
        chapter: 10,
        title: '第十章 通信协议',
        status: 'available',
        content: '# 第十章 通信协议\n\n完整课程内容开发中...',
        description: 'MCP、A2A、ANP 等协议',
        codeTemplate: '# 第十章内容\n# 完整课程内容开发中...'
      }
    ]
  },
  {
    id: 11,
    title: 'Agentic-RL',
    part: '第三部分：高级知识扩展',
    lessons: [
      {
        id: '11',
        chapter: 11,
        title: '第十一章 Agentic-RL',
        status: 'available',
        content: '# 第十一章 Agentic-RL\n\n完整课程内容开发中...',
        description: '从 SFT 到 GRPO 的 LLM 训练',
        codeTemplate: '# 第十一章内容\n# 完整课程内容开发中...'
      }
    ]
  },
  {
    id: 12,
    title: '智能体性能评估',
    part: '第三部分：高级知识扩展',
    lessons: [
      {
        id: '12',
        chapter: 12,
        title: '第十二章 性能评估',
        status: 'available',
        content: '# 第十二章 性能评估\n\n完整课程内容开发中...',
        description: '指标、基准测试与评估框架',
        codeTemplate: '# 第十二章内容\n# 完整课程内容开发中...'
      }
    ]
  },

  // ===== 第四部分：综合案例进阶 =====
  {
    id: 13,
    title: '智能旅行助手',
    part: '第四部分：综合案例进阶',
    lessons: [
      {
        id: '13',
        chapter: 13,
        title: '第十三章 智能旅行助手',
        status: 'available',
        content: '# 第十三章 智能旅行助手\n\n完整课程内容开发中...',
        description: 'MCP 与多智能体协作应用',
        codeTemplate: '# 第十三章内容\n# 完整课程内容开发中...'
      }
    ]
  },
  {
    id: 14,
    title: '自动化深度研究智能体',
    part: '第四部分：综合案例进阶',
    lessons: [
      {
        id: '14',
        chapter: 14,
        title: '第十四章 深度研究Agent',
        status: 'available',
        content: '# 第十四章 深度研究Agent\n\n完整课程内容开发中...',
        description: 'DeepResearch Agent 复现',
        codeTemplate: '# 第十四章内容\n# 完整课程内容开发中...'
      }
    ]
  },
  {
    id: 15,
    title: '构建赛博小镇',
    part: '第四部分：综合案例进阶',
    lessons: [
      {
        id: '15',
        chapter: 15,
        title: '第十五章 赛博小镇',
        status: 'available',
        content: '# 第十五章 赛博小镇\n\n完整课程内容开发中...',
        description: 'Agent 与游戏结合',
        codeTemplate: '# 第十五章内容\n# 完整课程内容开发中...'
      }
    ]
  },

  // ===== 第五部分：毕业设计及未来展望 =====
  {
    id: 16,
    title: '毕业设计',
    part: '第五部分：毕业设计及未来展望',
    lessons: [
      {
        id: '16',
        chapter: 16,
        title: '第十六章 毕业设计',
        status: 'available',
        content: '# 第十六章 毕业设计\n\n完整课程内容开发中...',
        description: '构建完整的多智能体应用',
        codeTemplate: '# 第十六章内容\n# 完整课程内容开发中...'
      }
    ]
  },
];

/**
 * 根据课程 ID 查找课程
 */
export function findLessonById(lessonId: string): Lesson | undefined {
  for (const chapter of allChapters) {
    const lesson = chapter.lessons.find(l => l.id === lessonId);
    if (lesson) return lesson;
  }
  return undefined;
}

/**
 * 计算学习进度
 */
export function calculateProgress(): number {
  let completed = 0;
  let total = 0;

  for (const chapter of allChapters) {
    for (const lesson of chapter.lessons) {
      total++;
      if (lesson.status === 'completed') {
        completed++;
      }
    }
  }

  return Math.round((completed / total) * 100);
}

/**
 * 获取当前学习的课程
 */
export function getCurrentLesson(): Lesson | undefined {
  for (const chapter of allChapters) {
    const currentLesson = chapter.lessons.find(l => l.status === 'current');
    if (currentLesson) return currentLesson;
  }
  return undefined;
}
