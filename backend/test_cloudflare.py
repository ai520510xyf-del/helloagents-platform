#!/usr/bin/env python3
"""
测试 Cloudflare Workers AI 图片分析功能

使用方法：
    python test_cloudflare.py
"""

import os
import sys
import requests
import base64
from pathlib import Path

# 从环境变量读取配置
CLOUDFLARE_ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN")

def test_cloudflare_vision():
    """测试 Cloudflare Workers AI 视觉模型"""

    print("=" * 60)
    print("Cloudflare Workers AI 图片分析测试")
    print("=" * 60)

    # 检查配置
    if not CLOUDFLARE_ACCOUNT_ID:
        print("❌ 错误: CLOUDFLARE_ACCOUNT_ID 环境变量未设置")
        return False

    if not CLOUDFLARE_API_TOKEN:
        print("❌ 错误: CLOUDFLARE_API_TOKEN 环境变量未设置")
        return False

    print(f"✅ Account ID: {CLOUDFLARE_ACCOUNT_ID[:8]}...")
    print(f"✅ API Token: {CLOUDFLARE_API_TOKEN[:8]}...")
    print()

    # 准备测试
    model = "@cf/meta/llama-3.2-11b-vision-instruct"
    url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/{model}"

    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    # 创建一个简单的测试图片（红色方块）
    # 这是一个 1x1 像素的红色 PNG 图片的 base64
    test_image_base64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="

    # 测试消息
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "这是什么颜色的图片？"},
                {"type": "image_url", "image_url": {"url": test_image_base64}}
            ]
        }
    ]

    payload = {"messages": messages}

    print("📤 发送测试请求...")
    print(f"   模型: {model}")
    print(f"   消息数: {len(messages)}")
    print()

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)

        print(f"📥 响应状态码: {response.status_code}")

        if response.status_code != 200:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"   响应内容: {response.text}")
            return False

        result = response.json()
        print(f"   响应内容: {result}")
        print()

        # 检查响应格式
        if "result" in result and "response" in result["result"]:
            ai_response = result["result"]["response"]
            print("✅ Cloudflare API 调用成功!")
            print(f"   AI 回复: {ai_response}")
            return True
        else:
            print("❌ 响应格式不正确")
            print(f"   期望: {{'result': {{'response': '...'}}}}")
            print(f"   实际: {result}")
            return False

    except requests.exceptions.Timeout:
        print("❌ 请求超时 (60秒)")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    success = test_cloudflare_vision()
    print()
    print("=" * 60)
    if success:
        print("✅ 测试通过 - Cloudflare Workers AI 配置正确")
        sys.exit(0)
    else:
        print("❌ 测试失败 - 请检查配置或错误信息")
        sys.exit(1)

if __name__ == "__main__":
    main()
