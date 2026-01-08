"""
课程内容导入脚本

从 hello-agents 文档目录读取 Markdown 文件，导入到 lessons 表
"""

import sys
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal, init_db
from app.models.lesson import Lesson
from app.courses import CourseManager


def parse_lesson_id(lesson_id: str) -> tuple:
    """
    解析 lesson_id 为 (chapter_number, lesson_number)

    Examples:
        "1" → (1, 1)
        "2" → (2, 1)
        "4.1" → (4, 1)
        "4.2" → (4, 2)
    """
    parts = lesson_id.split('.')
    if len(parts) == 1:
        # "1", "2" 等 → (1, 1), (2, 1)
        chapter = int(parts[0])
        return (chapter, 1)
    else:
        # "4.1", "4.2" 等 → (4, 1), (4, 2)
        chapter = int(parts[0])
        lesson = int(parts[1])
        return (chapter, lesson)


def import_lessons():
    """导入所有课程内容"""
    print("=" * 60)
    print("开始导入课程内容...")
    print("=" * 60)

    # 初始化数据库
    init_db()

    # 创建会话
    db = SessionLocal()

    try:
        # 创建课程管理器
        course_manager = CourseManager()

        imported = 0
        skipped = 0

        # 遍历所有课程
        for lesson_id, lesson_info in course_manager._course_structure.items():
            title = lesson_info['title']
            chapter, lesson_num = parse_lesson_id(lesson_id)

            print(f"\n处理课程: {lesson_id} - {title}")
            print(f"  章节: {chapter}, 课时: {lesson_num}")

            # 检查是否已存在
            existing = db.query(Lesson).filter(
                Lesson.chapter_number == chapter,
                Lesson.lesson_number == lesson_num
            ).first()

            if existing:
                print(f"  ⏭️  已存在，跳过")
                skipped += 1
                continue

            # 获取课程内容
            content = course_manager.get_lesson_content(lesson_id)
            if not content:
                print(f"  ⚠️  无法读取内容，跳过")
                skipped += 1
                continue

            # 获取代码模板
            code_template = course_manager.get_code_template(lesson_id)

            # 创建课程记录
            lesson = Lesson(
                chapter_number=chapter,
                lesson_number=lesson_num,
                title=title,
                content=content,
                starter_code=code_template or "# 开始编写代码...",
                extra_data='{"difficulty": "medium", "estimated_time": 30}'
            )

            db.add(lesson)
            db.commit()

            print(f"  ✅ 导入成功 (ID: {lesson.id})")
            print(f"     内容长度: {len(content)} 字符")
            print(f"     代码模板: {'有' if code_template else '无'}")

            imported += 1

        print("\n" + "=" * 60)
        print(f"导入完成!")
        print(f"  ✅ 成功导入: {imported} 个课程")
        print(f"  ⏭️  已存在跳过: {skipped} 个课程")
        print(f"  📊 总计: {imported + skipped} 个课程")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 导入失败: {str(e)}")
        db.rollback()
        raise

    finally:
        db.close()


def list_lessons():
    """列出数据库中的所有课程"""
    db = SessionLocal()

    try:
        lessons = db.query(Lesson).order_by(
            Lesson.chapter_number,
            Lesson.lesson_number
        ).all()

        print("\n" + "=" * 60)
        print(f"数据库中的课程列表 (共 {len(lessons)} 个)")
        print("=" * 60)

        for lesson in lessons:
            print(f"ID: {lesson.id:3d} | "
                  f"Chapter {lesson.chapter_number}.{lesson.lesson_number} | "
                  f"{lesson.title}")

        print("=" * 60)

    finally:
        db.close()


def clear_lessons():
    """清空所有课程数据"""
    db = SessionLocal()

    try:
        count = db.query(Lesson).count()
        if count == 0:
            print("没有课程数据需要清空")
            return

        print(f"⚠️  警告：将删除 {count} 个课程记录")
        confirm = input("确认删除？(yes/no): ")

        if confirm.lower() == 'yes':
            db.query(Lesson).delete()
            db.commit()
            print(f"✅ 已删除 {count} 个课程记录")
        else:
            print("取消删除")

    finally:
        db.close()


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'import':
            import_lessons()
        elif command == 'list':
            list_lessons()
        elif command == 'clear':
            clear_lessons()
        else:
            print(f"未知命令: {command}")
            print("可用命令:")
            print("  import - 导入课程内容")
            print("  list   - 列出所有课程")
            print("  clear  - 清空所有课程")
    else:
        # 默认执行导入
        import_lessons()
        list_lessons()
