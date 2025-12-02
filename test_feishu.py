#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试飞书推送功能
"""

import json
import requests
import sys

def test_feishu_webhook(webhook_url: str):
    """测试飞书Webhook"""
    print("=" * 50)
    print("🧪 测试飞书Webhook推送")
    print("=" * 50)
    print(f"Webhook地址: {webhook_url[:50]}...\n")
    
    # 构建测试消息
    message = {
        "msg_type": "text",
        "content": {
            "text": "🧪 这是一条测试消息\n\n如果你收到这条消息，说明飞书Webhook配置正确！"
        }
    }
    
    try:
        print("📤 发送测试消息...")
        response = requests.post(webhook_url, json=message, timeout=10)
        print(f"HTTP状态码: {response.status_code}")
        
        response.raise_for_status()
        result = response.json()
        print(f"响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if result.get('code') == 0:
            print("\n✅ 测试成功！飞书Webhook配置正确，你应该能在飞书群中看到测试消息。")
            return True
        else:
            print(f"\n❌ 测试失败: {result.get('msg', '未知错误')}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"\n❌ 网络请求失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"响应状态码: {e.response.status_code}")
            print(f"响应内容: {e.response.text[:200]}")
        return False
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    # 尝试从配置文件读取
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            webhook_url = config.get('feishu_webhook', '')
    except FileNotFoundError:
        print("❌ 未找到config.json文件")
        print("   请先创建配置文件，或直接提供Webhook地址作为参数")
        if len(sys.argv) > 1:
            webhook_url = sys.argv[1]
        else:
            webhook_url = input("请输入飞书Webhook地址: ").strip()
    except Exception as e:
        print(f"❌ 读取配置文件失败: {e}")
        if len(sys.argv) > 1:
            webhook_url = sys.argv[1]
        else:
            webhook_url = input("请输入飞书Webhook地址: ").strip()
    
    if not webhook_url:
        print("❌ 未提供Webhook地址")
        return 1
    
    success = test_feishu_webhook(webhook_url)
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())

