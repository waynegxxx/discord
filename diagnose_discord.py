#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord推送诊断工具
"""

import json
import os
import sys
import requests
from datetime import datetime

def check_config():
    """检查配置文件"""
    print("=" * 50)
    print("🔍 Discord推送诊断工具")
    print("=" * 50)
    
    # 检查配置文件
    config_file = "config.json"
    if not os.path.exists(config_file):
        print(f"\n❌ 配置文件不存在: {config_file}")
        print("   请先创建配置文件，参考 config.example.json")
        return False
    
    print(f"\n✅ 配置文件存在: {config_file}")
    
    # 读取配置
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ 读取配置文件失败: {e}")
        return False
    
    # 检查Discord Webhook
    discord_webhook = config.get('discord_webhook')
    if not discord_webhook:
        print("\n❌ 未配置Discord Webhook地址")
        print("   请在配置文件中添加 'discord_webhook' 字段")
        return False
    
    print(f"\n✅ Discord Webhook已配置")
    print(f"   Webhook: {discord_webhook[:50]}...")
    
    # 检查RSS源
    rss_sources = config.get('rss_sources', [])
    if not rss_sources:
        print("\n❌ 未配置RSS源")
        print("   请在配置文件中添加 'rss_sources' 字段")
        return False
    
    print(f"\n✅ RSS源已配置: {len(rss_sources)} 个")
    for i, source in enumerate(rss_sources, 1):
        print(f"   {i}. {source.get('name', '未命名')}: {source.get('url', '无URL')}")
    
    return True, config

def test_discord_webhook(webhook_url):
    """测试Discord Webhook"""
    print("\n" + "=" * 50)
    print("🧪 测试Discord Webhook")
    print("=" * 50)
    
    # 测试1: 简单文本消息
    print("\n📤 测试1: 发送简单文本消息...")
    message1 = {
        "content": "🧪 **Discord推送测试**\n\n如果你看到这条消息，说明Discord Webhook配置正确！\n\n时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    try:
        response = requests.post(webhook_url, json=message1, timeout=10)
        print(f"   HTTP状态码: {response.status_code}")
        
        if response.status_code in [200, 204]:
            print("   ✅ 简单文本消息发送成功")
        else:
            print(f"   ❌ 发送失败: {response.status_code}")
            print(f"   响应: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ 发送失败: {e}")
        return False
    
    # 测试2: Embed消息
    print("\n📤 测试2: 发送Embed消息...")
    embed = {
        "title": "📰 RSS监控测试",
        "description": "这是一条测试消息，用于验证Discord Embed格式是否正确。",
        "color": 0x5865F2,
        "footer": {
            "text": "RSS监控系统"
        },
        "fields": [
            {
                "name": "⏰ 测试时间",
                "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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
        
        if response.status_code in [200, 204]:
            print("   ✅ Embed消息发送成功")
            return True
        else:
            print(f"   ❌ 发送失败: {response.status_code}")
            print(f"   响应: {response.text[:200]}")
            if response.status_code == 400:
                print("\n   可能的原因：")
                print("   1. Embed格式错误")
                print("   2. 字段值超过限制")
                print("   3. 包含无效字符")
            return False
    except Exception as e:
        print(f"   ❌ 发送失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   响应状态码: {e.response.status_code}")
            print(f"   响应内容: {e.response.text[:200]}")
        return False

def check_state_file():
    """检查状态文件"""
    print("\n" + "=" * 50)
    print("📋 检查推送状态")
    print("=" * 50)
    
    state_file = "rss_state.json"
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            print(f"\n✅ 状态文件存在: {state_file}")
            print(f"   已推送文章数: {len(state)}")
            if len(state) > 0:
                print("\n   最近推送的文章（前5条）：")
                items = list(state.items())[:5]
                for key, value in items:
                    print(f"   - {value.get('title', '无标题')[:50]}...")
                    print(f"     推送时间: {value.get('pushed_at', '未知')}")
        except Exception as e:
            print(f"⚠️ 读取状态文件失败: {e}")
    else:
        print(f"\nℹ️ 状态文件不存在: {state_file}")
        print("   首次运行时会创建此文件")

def main():
    """主函数"""
    # 检查配置
    result = check_config()
    if not result:
        return 1
    
    success, config = result
    
    # 测试Webhook
    discord_webhook = config.get('discord_webhook')
    if not test_discord_webhook(discord_webhook):
        print("\n❌ Discord Webhook测试失败")
        print("\n建议：")
        print("1. 检查Webhook地址是否正确")
        print("2. 检查Discord服务器中Webhook是否仍然有效")
        print("3. 尝试重新创建Webhook")
        return 1
    
    # 检查状态文件
    check_state_file()
    
    print("\n" + "=" * 50)
    print("✨ 诊断完成")
    print("=" * 50)
    print("\n如果Webhook测试成功但仍然没有收到消息，可能的原因：")
    print("1. 所有文章都已经推送过了（首次运行会推送最新10条）")
    print("2. RSS源没有新文章")
    print("3. RSS源获取失败（会发送错误通知）")
    print("4. GitHub Actions没有运行或运行失败")
    print("\n建议：")
    print("- 查看GitHub Actions日志：https://github.com/waynegxxx/discord/actions")
    print("- 删除 rss_state.json 文件可以重新推送所有文章")
    print("- 手动触发GitHub Actions测试")
    
    return 0

if __name__ == "__main__":
    exit(main())

