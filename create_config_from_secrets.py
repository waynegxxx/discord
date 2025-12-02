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
    
    if not feishu_webhook:
        print("⚠️ 未设置 FEISHU_WEBHOOK 环境变量")
        return
    
    if not rss_sources_json:
        print("⚠️ 未设置 RSS_SOURCES 环境变量")
        return
    
    try:
        rss_sources = json.loads(rss_sources_json)
    except json.JSONDecodeError as e:
        print(f"❌ RSS_SOURCES JSON格式错误: {e}")
        return
    
    config = {
        "feishu_webhook": feishu_webhook,
        "rss_sources": rss_sources
    }
    
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print("✅ 配置文件创建成功")

if __name__ == "__main__":
    main()

