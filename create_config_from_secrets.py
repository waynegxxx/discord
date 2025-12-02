#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从GitHub Secrets创建配置文件
"""

import json
import os

def main():
    """从环境变量创建config.json"""
    feishu_webhook = os.getenv('FEISHU_WEBHOOK', '')
    rss_sources_json = os.getenv('RSS_SOURCES', '')
    
    print("=" * 50)
    print("🔧 从GitHub Secrets创建配置文件")
    print("=" * 50)
    
    if not feishu_webhook:
        print("❌ 未设置 FEISHU_WEBHOOK 环境变量")
        print("   请在GitHub仓库 Settings → Secrets 中添加 FEISHU_WEBHOOK")
        return 1
    
    print(f"✅ FEISHU_WEBHOOK: 已设置 ({feishu_webhook[:30]}...)")
    
    if not rss_sources_json:
        print("❌ 未设置 RSS_SOURCES 环境变量")
        print("   请在GitHub仓库 Settings → Secrets 中添加 RSS_SOURCES")
        return 1
    
    print(f"✅ RSS_SOURCES: 已设置 (长度: {len(rss_sources_json)} 字符)")
    
    try:
        rss_sources = json.loads(rss_sources_json)
        print(f"✅ RSS源数量: {len(rss_sources)}")
        for i, source in enumerate(rss_sources, 1):
            print(f"   {i}. {source.get('name', '未命名')}: {source.get('url', '无URL')}")
    except json.JSONDecodeError as e:
        print(f"❌ RSS_SOURCES JSON格式错误: {e}")
        print(f"   内容预览: {rss_sources_json[:100]}...")
        return 1
    
    config = {
        "feishu_webhook": feishu_webhook,
        "rss_sources": rss_sources
    }
    
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print("✅ 配置文件创建成功: config.json")
    return 0

if __name__ == "__main__":
    exit(main())

