"""
数据库初始化脚本
"""

from app.database import Base, engine, DATABASE_PATH
from app.models import User, Lesson, UserProgress, CodeSubmission, ChatMessage

def main():
    print('Initializing database...')
    print(f'Database path: {DATABASE_PATH}')

    # 创建所有表
    Base.metadata.create_all(bind=engine)

    print(f'✅ Database initialized successfully!')

    # 显示创建的表
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f'\nCreated tables:')
    for table in tables:
        print(f'  - {table}')

if __name__ == '__main__':
    main()
