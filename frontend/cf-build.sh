#!/bin/bash
set -e

echo "🚀 Starting Cloudflare Pages build..."

# 清理可能存在的损坏的 node_modules
if [ -d "node_modules" ]; then
  echo "📦 Cleaning existing node_modules..."
  rm -rf node_modules
fi

# 使用 npm install 而不是 npm ci（避免 clean-install 的问题）
echo "📦 Installing dependencies..."
npm install --prefer-offline --no-audit --no-fund --loglevel=error

# 运行构建
echo "🔨 Building project..."
npm run build

echo "✅ Build completed successfully!"
