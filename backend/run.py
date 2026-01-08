"""
HelloAgents 学习平台后端服务启动脚本
"""

import uvicorn
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

if __name__ == "__main__":
    # 从环境变量读取配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() == "true"

    print("=" * 60)
    print("🚀 启动 HelloAgents Learning Platform API")
    print("=" * 60)
    print(f"📍 地址: http://{host}:{port}")
    print(f"📝 API 文档: http://localhost:{port}/docs")
    print(f"🔌 WebSocket: ws://localhost:{port}/ws")
    print(f"🔄 热重载: {'开启' if reload else '关闭'}")
    print("=" * 60)

    # 启动服务
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
