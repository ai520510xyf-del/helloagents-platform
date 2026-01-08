#!/bin/bash
# ===========================
# HelloAgents Platform
# 环境变量验证脚本
# ===========================

set -e

echo "🔍 Checking required environment variables..."

# 定义必需的环境变量
REQUIRED_VARS=(
    "ANTHROPIC_API_KEY"
    "POSTGRES_PASSWORD"
)

# 定义可选的环境变量（会提示警告但不会失败）
OPTIONAL_VARS=(
    "OPENAI_API_KEY"
    "DEEPSEEK_API_KEY"
    "SENTRY_DSN"
)

# 检查标志
has_errors=0
has_warnings=0

# 检查必需变量
echo ""
echo "📋 Required Variables:"
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "  ❌ $var is not set (REQUIRED)"
        has_errors=1
    else
        # 检查是否使用了示例值
        if [[ "${!var}" == *"your_"* ]] || [[ "${!var}" == *"_here"* ]]; then
            echo "  ⚠️  $var is set but appears to be a placeholder value"
            has_errors=1
        else
            echo "  ✅ $var is set"
        fi
    fi
done

# 检查可选变量
echo ""
echo "📋 Optional Variables:"
for var in "${OPTIONAL_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "  ⚠️  $var is not set (optional)"
        has_warnings=1
    else
        if [[ "${!var}" == *"your_"* ]] || [[ "${!var}" == *"_here"* ]]; then
            echo "  ⚠️  $var is set but appears to be a placeholder value"
            has_warnings=1
        else
            echo "  ✅ $var is set"
        fi
    fi
done

# 检查 .env 文件
echo ""
echo "📄 Configuration Files:"
if [ -f ".env" ]; then
    echo "  ✅ .env file exists"
else
    echo "  ⚠️  .env file not found"
    echo "     Please copy .env.example to .env and configure it:"
    echo "     cp .env.example .env"
    has_warnings=1
fi

if [ -f ".env.example" ]; then
    echo "  ✅ .env.example file exists"
else
    echo "  ❌ .env.example file not found"
    has_errors=1
fi

# 安全检查
echo ""
echo "🔒 Security Checks:"

# 检查 POSTGRES_PASSWORD 强度
if [ -n "${POSTGRES_PASSWORD}" ]; then
    if [ ${#POSTGRES_PASSWORD} -lt 12 ]; then
        echo "  ⚠️  POSTGRES_PASSWORD is too short (minimum 12 characters recommended)"
        has_warnings=1
    else
        echo "  ✅ POSTGRES_PASSWORD length is acceptable"
    fi

    if [[ "${POSTGRES_PASSWORD}" == *"secret"* ]] || \
       [[ "${POSTGRES_PASSWORD}" == *"password"* ]] || \
       [[ "${POSTGRES_PASSWORD}" == *"123456"* ]]; then
        echo "  ❌ POSTGRES_PASSWORD is too weak (avoid common words)"
        has_errors=1
    else
        echo "  ✅ POSTGRES_PASSWORD doesn't contain common weak patterns"
    fi
fi

# 检查 .env 是否在 .gitignore 中
echo ""
echo "📝 Git Configuration:"
if [ -f ".gitignore" ]; then
    if grep -q "^\.env$" .gitignore; then
        echo "  ✅ .env is properly ignored in .gitignore"
    else
        echo "  ❌ .env is NOT in .gitignore (SECURITY RISK!)"
        has_errors=1
    fi
else
    echo "  ⚠️  .gitignore file not found"
    has_warnings=1
fi

# 总结
echo ""
echo "================================"
if [ $has_errors -eq 1 ]; then
    echo "❌ Environment validation FAILED"
    echo ""
    echo "Please fix the errors above before starting the application."
    echo ""
    echo "Quick start:"
    echo "  1. Copy .env.example to .env:"
    echo "     cp .env.example .env"
    echo ""
    echo "  2. Edit .env and set your actual values:"
    echo "     nano .env  # or use your preferred editor"
    echo ""
    echo "  3. Run this script again to verify:"
    echo "     ./scripts/check-env.sh"
    echo ""
    exit 1
elif [ $has_warnings -eq 1 ]; then
    echo "⚠️  Environment validation PASSED with warnings"
    echo ""
    echo "You can proceed, but consider addressing the warnings above."
    echo ""
    exit 0
else
    echo "✅ Environment validation PASSED"
    echo ""
    echo "All required environment variables are properly configured."
    echo "You can now start the application safely."
    echo ""
    exit 0
fi
