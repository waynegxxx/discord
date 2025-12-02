#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从GitHub Secrets创建配置文件
"""

import json
import os

def main():
    """从环境变量创建config.json"""
    discord_webhook = os.getenv('DISCORD_WEBHOOK', '')
    feishu_webhook = os.getenv('FEISHU_WEBHOOK', '')
    rss_sources_json = os.getenv('RSS_SOURCES', '')
    
    print("=" * 50)
    print("🔧 从GitHub Secrets创建配置文件")
    print("=" * 50)
    
    # 检查至少有一个Webhook
    if not discord_webhook and not feishu_webhook:
        print("❌ 未设置 DISCORD_WEBHOOK 或 FEISHU_WEBHOOK 环境变量")
        print("   请在GitHub仓库 Settings → Secrets 中添加至少一个Webhook")
        return 1
    
    if discord_webhook:
        print(f"✅ DISCORD_WEBHOOK: 已设置 ({discord_webhook[:30]}...)")
    else:
        print("ℹ️  DISCORD_WEBHOOK: 未设置（将使用飞书）")
    
    if feishu_webhook:
        print(f"✅ FEISHU_WEBHOOK: 已设置 ({feishu_webhook[:30]}...)")
    else:
        print("ℹ️  FEISHU_WEBHOOK: 未设置")
    
    if not rss_sources_json:
        print("❌ 未设置 RSS_SOURCES 环境变量")
        print("   请在GitHub仓库 Settings → Secrets 中添加 RSS_SOURCES")
        print("   格式示例：")
        print('   [{"name": "网站名称", "url": "https://example.com/rss"}]')
        return 1
    
    print(f"✅ RSS_SOURCES: 已设置 (长度: {len(rss_sources_json)} 字符)")
    
    # 验证和解析RSS_SOURCES JSON
    try:
        rss_sources = json.loads(rss_sources_json)
        if not isinstance(rss_sources, list):
            print("❌ RSS_SOURCES 必须是JSON数组格式")
            print("   正确格式: [{\"name\": \"网站名称\", \"url\": \"RSS链接\"}]")
            return 1
        
        print(f"✅ RSS源数量: {len(rss_sources)}")
        for i, source in enumerate(rss_sources, 1):
            name = source.get('name', '未命名')
            url = source.get('url', '无URL')
            print(f"   {i}. {name}: {url}")
            
            # 验证每个源的必要字段
            if not url:
                print(f"      ⚠️  警告: 第{i}个源缺少URL")
    except json.JSONDecodeError as e:
        print(f"❌ RSS_SOURCES JSON格式错误: {e}")
        print(f"   错误位置: 第{e.lineno}行，第{e.colno}列")
        print(f"   内容预览: {rss_sources_json[:200]}...")
        print("\n   正确格式示例：")
        print('   [')
        print('     {')
        print('       "name": "网站名称1",')
        print('       "url": "https://example.com/rss"')
        print('     },')
        print('     {')
        print('       "name": "网站名称2",')
        print('       "url": "https://another-example.com/feed"')
        print('     }')
        print('   ]')
        return 1
    
    # 构建配置
    config = {}
    if discord_webhook:
        config["discord_webhook"] = discord_webhook
    if feishu_webhook:
        config["feishu_webhook"] = feishu_webhook
    config["rss_sources"] = rss_sources
    
    # 写入配置文件
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print("\n✅ 配置文件创建成功: config.json")
    return 0

if __name__ == "__main__":
    exit(main())

