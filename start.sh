#!/bin/bash
# Railway 启动脚本

cd backend
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
