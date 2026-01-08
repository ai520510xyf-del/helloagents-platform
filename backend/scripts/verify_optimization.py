#!/usr/bin/env python3
"""
数据库优化验证脚本

验证所有优化措施是否正确部署和生效
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import engine, SessionLocal
from app.db_migration import check_index_status
from sqlalchemy import inspect, text


def print_section(title: str, emoji: str = "📋"):
    """打印章节标题"""
    print(f'\n{emoji} {title}')
    print('=' * 70)


def verify_imports():
    """验证模块导入"""
    print_section("验证模块导入", "📦")

    try:
        from app import db_utils
        from app import db_monitoring
        from app import db_migration
        print("✅ app.db_utils - 导入成功")
        print("✅ app.db_monitoring - 导入成功")
        print("✅ app.db_migration - 导入成功")
        return True
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False


def verify_models():
    """验证模型定义"""
    print_section("验证模型定义", "🗃️")

    try:
        from app.models.code_submission import CodeSubmission
        from app.models.chat_message import ChatMessage
        from app.models.user_progress import UserProgress

        # 检查模型是否有 __table_args__
        models = [
            ('CodeSubmission', CodeSubmission),
            ('ChatMessage', ChatMessage),
            ('UserProgress', UserProgress),
        ]

        for name, model in models:
            if hasattr(model, '__table_args__') and model.__table_args__:
                print(f"✅ {name} - 索引定义已添加")
            else:
                print(f"⚠️  {name} - 未找到索引定义")
                return False

        return True
    except Exception as e:
        print(f"❌ 模型验证失败: {e}")
        return False


def verify_database_config():
    """验证数据库配置"""
    print_section("验证数据库配置", "⚙️")

    try:
        # 检查连接池配置
        pool = engine.pool
        print(f"✅ 连接池类型: {pool.__class__.__name__}")

        # 检查 echo 配置
        print(f"✅ SQL 日志: {'启用' if engine.echo else '禁用'}")

        # 尝试连接
        with engine.connect() as conn:
            # 检查 SQLite PRAGMA
            result = conn.execute(text("PRAGMA journal_mode"))
            journal_mode = result.scalar()
            print(f"✅ Journal 模式: {journal_mode}")

            result = conn.execute(text("PRAGMA synchronous"))
            sync_mode = result.scalar()
            print(f"✅ 同步模式: {sync_mode}")

            result = conn.execute(text("PRAGMA cache_size"))
            cache_size = result.scalar()
            print(f"✅ 缓存大小: {cache_size} pages")

        return True
    except Exception as e:
        print(f"❌ 数据库配置验证失败: {e}")
        return False


def verify_indexes():
    """验证索引状态"""
    print_section("验证索引状态", "📊")

    try:
        status = check_index_status()

        print(f"总索引数: {status['total_indexes']}")

        # 检查推荐索引
        if status['missing_recommended_indexes']:
            print(f"\n⚠️  缺少 {len(status['missing_recommended_indexes'])} 个推荐索引:")
            for missing in status['missing_recommended_indexes']:
                print(f"   - {missing['table']}.{missing['index']}")
            return False
        else:
            print("✅ 所有推荐索引都已创建")

        # 显示各表索引
        print("\n各表索引情况:")
        for table_name, table_info in status['tables'].items():
            print(f"  {table_name}: {table_info['index_count']} 个索引")

        return True
    except Exception as e:
        print(f"❌ 索引验证失败: {e}")
        return False


def verify_query_functions():
    """验证查询优化函数"""
    print_section("验证查询优化函数", "🔍")

    try:
        from app import db_utils

        # 检查关键函数
        functions = [
            'get_user_submissions_with_lesson',
            'get_lesson_submissions_with_users',
            'get_user_submission_stats',
            'get_user_chat_history',
            'get_user_progress_with_lessons',
            'get_user_dashboard_data',
            'get_lesson_stats',
            'bulk_create_submissions',
            'bulk_update_progress',
        ]

        missing = []
        for func_name in functions:
            if hasattr(db_utils, func_name):
                print(f"✅ {func_name}")
            else:
                print(f"❌ {func_name}")
                missing.append(func_name)

        if missing:
            print(f"\n⚠️  缺少 {len(missing)} 个函数")
            return False

        return True
    except Exception as e:
        print(f"❌ 查询函数验证失败: {e}")
        return False


def verify_monitoring():
    """验证监控功能"""
    print_section("验证监控功能", "📈")

    try:
        from app import db_monitoring

        # 检查关键组件
        components = [
            'QueryPerformanceStats',
            'query_stats',
            'track_query_performance',
            'query_performance_context',
            'explain_query',
            'analyze_table_stats',
            'get_database_performance_report',
            'suggest_optimizations',
        ]

        missing = []
        for component in components:
            if hasattr(db_monitoring, component):
                print(f"✅ {component}")
            else:
                print(f"❌ {component}")
                missing.append(component)

        if missing:
            print(f"\n⚠️  缺少 {len(missing)} 个组件")
            return False

        # 测试统计功能
        stats = db_monitoring.query_stats.get_stats()
        print(f"\n当前查询统计: {stats}")

        return True
    except Exception as e:
        print(f"❌ 监控功能验证失败: {e}")
        return False


def verify_migration_tools():
    """验证迁移工具"""
    print_section("验证迁移工具", "🔧")

    try:
        from app import db_migration

        # 检查关键函数
        functions = [
            'create_performance_indexes',
            'drop_performance_indexes',
            'analyze_database',
            'vacuum_database',
            'check_index_status',
            'benchmark_query_performance',
        ]

        missing = []
        for func_name in functions:
            if hasattr(db_migration, func_name):
                print(f"✅ {func_name}")
            else:
                print(f"❌ {func_name}")
                missing.append(func_name)

        if missing:
            print(f"\n⚠️  缺少 {len(missing)} 个函数")
            return False

        return True
    except Exception as e:
        print(f"❌ 迁移工具验证失败: {e}")
        return False


def verify_documentation():
    """验证文档"""
    print_section("验证文档", "📚")

    docs_dir = Path(__file__).parent.parent / 'docs'
    required_docs = [
        'DATABASE_OPTIMIZATION.md',
        'DATABASE_OPTIMIZATION_QUICK_START.md',
        'OPTIMIZATION_SUMMARY.md',
    ]

    all_exist = True
    for doc in required_docs:
        doc_path = docs_dir / doc
        if doc_path.exists():
            print(f"✅ {doc}")
        else:
            print(f"❌ {doc} - 文件不存在")
            all_exist = False

    return all_exist


def verify_demo_script():
    """验证演示脚本"""
    print_section("验证演示脚本", "🎬")

    script_path = Path(__file__).parent / 'db_optimization_demo.py'

    if script_path.exists():
        print(f"✅ db_optimization_demo.py 存在")

        # 检查是否可执行
        import os
        if os.access(script_path, os.X_OK):
            print("✅ 脚本有执行权限")
        else:
            print("⚠️  脚本没有执行权限（可能需要 chmod +x）")

        return True
    else:
        print("❌ db_optimization_demo.py 不存在")
        return False


def run_basic_tests():
    """运行基本功能测试"""
    print_section("运行基本功能测试", "🧪")

    db = SessionLocal()

    try:
        # 测试 1: 导入优化函数
        from app.db_utils import get_user_submission_stats
        print("✅ 测试 1: 导入优化查询函数")

        # 测试 2: 执行聚合查询
        stats = get_user_submission_stats(db, user_id=1)
        print(f"✅ 测试 2: 聚合查询执行成功 - {stats}")

        # 测试 3: 性能监控
        from app.db_monitoring import query_stats
        query_stats.record_query(0.05, "SELECT * FROM users")
        stats_data = query_stats.get_stats()
        print(f"✅ 测试 3: 性能监控工作正常 - {stats_data}")

        # 测试 4: 索引检查
        status = check_index_status()
        print(f"✅ 测试 4: 索引状态检查成功 - 共 {status['total_indexes']} 个索引")

        return True
    except Exception as e:
        print(f"❌ 功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def main():
    """主函数"""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║               数据库优化验证 - HelloAgents Platform              ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    results = []

    # 运行所有验证
    checks = [
        ("模块导入", verify_imports),
        ("模型定义", verify_models),
        ("数据库配置", verify_database_config),
        ("索引状态", verify_indexes),
        ("查询优化函数", verify_query_functions),
        ("监控功能", verify_monitoring),
        ("迁移工具", verify_migration_tools),
        ("文档", verify_documentation),
        ("演示脚本", verify_demo_script),
        ("功能测试", run_basic_tests),
    ]

    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} 验证出错: {e}")
            results.append((name, False))

    # 打印总结
    print_section("验证总结", "📊")

    passed = sum(1 for _, result in results if result)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0

    print(f"\n通过: {passed}/{total} ({percentage:.1f}%)\n")

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {status}  {name}")

    # 最终结论
    print("\n" + "=" * 70)
    if passed == total:
        print("🎉 恭喜！所有验证都通过了！")
        print("\n下一步:")
        print("  1. 运行演示脚本: python scripts/db_optimization_demo.py")
        print("  2. 查看文档: docs/DATABASE_OPTIMIZATION_QUICK_START.md")
        print("  3. 在代码中使用优化函数")
        return 0
    else:
        print("⚠️  部分验证失败，请检查上述错误信息")
        print("\n建议:")
        print("  1. 确保所有依赖已安装")
        print("  2. 检查数据库文件是否存在")
        print("  3. 运行索引创建: python -m app.db_migration create_indexes")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
