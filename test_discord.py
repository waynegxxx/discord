#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Discord Webhook
"""

import sys
import requests
import json
from datetime import datetime

def test_discord_webhook(webhook_url=None):
    """测试Discord Webhook"""
    if not webhook_url:
        if len(sys.argv) > 1:
            webhook_url = sys.argv[1]
        else:
            print("使用方法: python test_discord.py <Discord Webhook URL>")
            print("或者: python test_discord.py")
            print("     然后在提示时输入Webhook URL")
            webhook_url = input("\n请输入Discord Webhook地址: ").strip()
    
    if not webhook_url:
        print("❌ 未提供Webhook地址")
        return False
    
    print("=" * 50)
    print("🧪 测试Discord Webhook")
    print("=" * 50)
    print(f"Webhook地址: {webhook_url[:50]}...")
    
    # 测试消息1：普通消息
    print("\n📤 测试1: 发送普通消息...")
    message1 = {
        "content": "🧪 这是一条测试消息\n如果你看到这条消息，说明Discord Webhook配置正确！"
    }
    
    try:
        response = requests.post(webhook_url, json=message1, timeout=10)
        print(f"   HTTP状态码: {response.status_code}")
        response.raise_for_status()
        
        if response.status_code in [200, 204]:
            print("   ✅ 普通消息发送成功")
        else:
            print(f"   ⚠️ 状态码: {response.status_code}")
            print(f"   响应: {response.text[:200]}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ 发送失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   响应状态码: {e.response.status_code}")
            print(f"   响应内容: {e.response.text[:200]}")
        return False
    
    # 测试消息2：Embed消息（错误通知格式）
    print("\n📤 测试2: 发送Embed消息（错误通知格式）...")
    embed = {
        "title": "⚠️ RSS监控 - 测试源",
        "description": "**状态**: WARNING\n**错误信息**: 这是测试错误消息\n**RSS源**: https://example.com/rss",
        "color": 0xFFA500,  # 橙色
        "timestamp": datetime.now().isoformat(),
        "footer": {
            "text": "RSS监控系统"
        },
        "fields": [
            {
                "name": "🔗 RSS链接",
                "value": "https://example.com/rss",
                "inline": False
            }
        ]
    }
    
    message2 = {
        "embeds": [embed]
    }
    
    try:
        response = requests.post(webhook_url, json=message2, timeout=10)
        print(f"   HTTP状态码: {response.status_code}")
        response.raise_for_status()
        
        if response.status_code in [200, 204]:
            print("   ✅ Embed消息发送成功")
            print("\n✨ 所有测试通过！Discord Webhook配置正确。")
            return True
        else:
            print(f"   ⚠️ 状态码: {response.status_code}")
            print(f"   响应: {response.text[:200]}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ 发送失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   响应状态码: {e.response.status_code}")
            print(f"   响应内容: {e.response.text[:200]}")
            print("\n可能的原因：")
            print("   1. Webhook地址格式错误")
            print("   2. Webhook已失效或被删除")
            print("   3. 网络连接问题")
        return False
    except Exception as e:
        print(f"   ❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_discord_webhook()
    sys.exit(0 if success else 1)

