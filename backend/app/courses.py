"""
课程数据管理模块
从 hello-agents 项目读取完整的课程内容
"""

import os
from typing import Optional, List, Dict
from pathlib import Path

# hello-agents 项目的文档路径
HELLO_AGENTS_DOCS_PATH = "/Users/anker/Desktop/work/mydocuments/project/agent-study/hello-agents/docs"

class CourseManager:
    """课程管理器"""

    def __init__(self):
        self.docs_path = Path(HELLO_AGENTS_DOCS_PATH)
        self._course_structure = self._init_course_structure()

    def _init_course_structure(self) -> Dict:
        """初始化课程结构"""
        return {
            "1": {"title": "初识智能体", "file": "chapter1/第一章 初识智能体.md"},
            "2": {"title": "智能体发展史", "file": "chapter2/第二章 智能体发展史.md"},
            "3": {"title": "大语言模型基础", "file": "chapter3/第三章 大语言模型基础.md"},
            "4.1": {"title": "ReAct 范式", "file": "chapter4/第四章 智能体经典范式构建.md"},
            "4.2": {"title": "Plan-and-Solve", "file": "chapter4/第四章 智能体经典范式构建.md"},
            "4.3": {"title": "Reflection", "file": "chapter4/第四章 智能体经典范式构建.md"},
            "5": {"title": "低代码平台", "file": "chapter5/第五章 基于低代码平台的智能体搭建.md"},
            "6": {"title": "框架开发", "file": "chapter6/第六章 基于主流框架的智能体开发实践.md"},
            "7": {"title": "自建框架", "file": "chapter7/第七章 构建你的Agent框架.md"},
            "8": {"title": "记忆与检索", "file": "chapter8/第八章 Memory 与 Retrieval.md"},
            "9": {"title": "上下文工程", "file": "chapter9/第九章 上下文工程.md"},
            "10": {"title": "通信协议", "file": "chapter10/第十章 智能体通信协议.md"},
            "11": {"title": "Agentic-RL", "file": "chapter11/第十一章 Agentic-RL.md"},
            "12": {"title": "性能评估", "file": "chapter12/第十二章 智能体性能评估.md"},
            "13": {"title": "智能旅行助手", "file": "chapter13/第十三章 智能旅行助手：MCP 与多智能体协作应用.md"},
            "14": {"title": "深度研究Agent", "file": "chapter14/第十四章 自动化深度研究智能体.md"},
            "15": {"title": "赛博小镇", "file": "chapter15/第十五章 构建赛博小镇.md"},
            "16": {"title": "毕业设计", "file": "chapter16/第十六章 毕业设计.md"},
        }

    def get_lesson_content(self, lesson_id: str) -> Optional[str]:
        """
        获取课程内容

        Args:
            lesson_id: 课程ID，如 "1", "2", "4.1" 等

        Returns:
            课程内容的 Markdown 文本，如果课程不存在则返回 None
        """
        if lesson_id not in self._course_structure:
            return None

        lesson_info = self._course_structure[lesson_id]
        file_path = self.docs_path / lesson_info["file"]

        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return content
            else:
                return f"# {lesson_info['title']}\n\n课程内容正在开发中..."
        except Exception as e:
            print(f"读取课程 {lesson_id} 失败: {str(e)}")
            return f"# {lesson_info['title']}\n\n课程内容加载失败"

    def get_all_lessons(self) -> List[Dict]:
        """
        获取所有课程列表

        Returns:
            课程列表
        """
        lessons = []
        for lesson_id, lesson_info in self._course_structure.items():
            lessons.append({
                "id": lesson_id,
                "title": lesson_info["title"],
                "has_content": (self.docs_path / lesson_info["file"]).exists()
            })
        return lessons

    def get_code_template(self, lesson_id: str) -> Optional[str]:
        """
        获取课程的代码模板

        Args:
            lesson_id: 课程ID

        Returns:
            代码模板，如果不存在则返回默认模板
        """
        # 代码模板路径 - hello-agents/code/chapter{N}/
        try:
            chapter_num = lesson_id.split('.')[0]  # "4.1" -> "4"
            code_path = Path(HELLO_AGENTS_DOCS_PATH).parent / "code" / f"chapter{chapter_num}"

            if code_path.exists():
                # 查找 Python 文件
                py_files = list(code_path.glob("*.py"))
                if py_files:
                    with open(py_files[0], 'r', encoding='utf-8') as f:
                        return f.read()

            # 返回默认模板
            return f"""# Hello-Agents - 第{lesson_id}章

# 课程代码模板

# TODO: 完成课程练习
"""
        except Exception as e:
            print(f"读取代码模板 {lesson_id} 失败: {str(e)}")
            return f"# 代码模板加载失败"

# 创建全局实例
course_manager = CourseManager()
