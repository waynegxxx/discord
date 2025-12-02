#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RSS监控脚本 - 自动监控RSS源并推送到飞书群
"""

import json
import os
import time
import hashlib
import requests
from datetime import datetime
from typing import List, Dict
import feedparser
from pathlib import Path


class RSSMonitor:
    def __init__(self, config_file: str = "config.json"):
        """初始化RSS监控器"""
        self.config_file = config_file
        self.state_file = "rss_state.json"  # 存储已推送的文章ID
        self.config = self.load_config()
        self.state = self.load_state()
        
    def load_config(self) -> Dict:
        """加载配置文件"""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(
                f"配置文件 {self.config_file} 不存在！\n"
                "请先创建配置文件，参考 config.example.json"
            )
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_state(self) -> Dict:
        """加载状态文件（已推送的文章记录）"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_state(self):
        """保存状态文件"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)
    
    def get_article_id(self, entry: Dict) -> str:
        """生成文章唯一ID"""
        # 优先使用link，如果没有则使用title+published
        identifier = entry.get('link') or f"{entry.get('title', '')}{entry.get('published', '')}"
        return hashlib.md5(identifier.encode('utf-8')).hexdigest()
    
    def fetch_rss(self, url: str) -> List[Dict]:
        """获取RSS源的最新文章"""
        try:
            feed = feedparser.parse(url)
            if feed.bozo and feed.bozo_exception:
                print(f"⚠️ RSS解析错误 ({url}): {feed.bozo_exception}")
                return []
            
            articles = []
            for entry in feed.entries[:10]:  # 只取最新10条
                article = {
                    'title': entry.get('title', '无标题'),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'summary': entry.get('summary', entry.get('description', ''))[:200],  # 限制摘要长度
                    'source': url
                }
                articles.append(article)
            
            return articles
        except Exception as e:
            print(f"❌ 获取RSS失败 ({url}): {e}")
            return []
    
    def send_to_feishu(self, article: Dict, source_name: str = ""):
        """发送消息到飞书"""
        webhook_url = self.config.get('feishu_webhook')
        if not webhook_url:
            print("❌ 未配置飞书Webhook地址")
            return False
        
        # 构建消息卡片
        title = article.get('title', '无标题')
        link = article.get('link', '')
        summary = article.get('summary', '')
        published = article.get('published', '')
        
        # 飞书消息格式
        message = {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True
                },
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": "📰 新文章推送"
                    },
                    "template": "blue"
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**{title}**"
                        }
                    },
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"📅 {published}" if published else ""
                        }
                    },
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"📝 {summary}" if summary else ""
                        }
                    },
                    {
                        "tag": "action",
                        "actions": [
                            {
                                "tag": "button",
                                "text": {
                                    "tag": "plain_text",
                                    "content": "查看原文"
                                },
                                "type": "primary",
                                "url": link
                            }
                        ]
                    }
                ]
            }
        }
        
        # 如果有来源名称，添加到标题
        if source_name:
            message["card"]["header"]["title"]["content"] = f"📰 {source_name} - 新文章推送"
        
        try:
            response = requests.post(webhook_url, json=message, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') == 0:
                print(f"✅ 推送成功: {title[:50]}...")
                return True
            else:
                print(f"❌ 推送失败: {result.get('msg', '未知错误')}")
                return False
        except Exception as e:
            print(f"❌ 发送到飞书失败: {e}")
            return False
    
    def check_and_push(self):
        """检查RSS源并推送新文章"""
        rss_sources = self.config.get('rss_sources', [])
        if not rss_sources:
            print("⚠️ 未配置RSS源")
            return
        
        new_count = 0
        
        for source in rss_sources:
            url = source.get('url', '')
            name = source.get('name', url)
            
            if not url:
                continue
            
            print(f"\n🔍 检查RSS源: {name}")
            articles = self.fetch_rss(url)
            
            for article in articles:
                article_id = self.get_article_id(article)
                source_key = f"{url}_{article_id}"
                
                # 检查是否已推送
                if source_key not in self.state:
                    print(f"📬 发现新文章: {article['title'][:50]}...")
                    
                    # 发送到飞书
                    if self.send_to_feishu(article, name):
                        # 记录已推送
                        self.state[source_key] = {
                            'title': article['title'],
                            'link': article['link'],
                            'pushed_at': datetime.now().isoformat()
                        }
                        new_count += 1
                    
                    # 避免发送过快
                    time.sleep(1)
        
        # 保存状态
        if new_count > 0:
            self.save_state()
            print(f"\n✨ 本次共推送 {new_count} 条新消息")
        else:
            print("\n✨ 暂无新消息")


def main():
    """主函数"""
    print("=" * 50)
    print("🚀 RSS监控脚本启动")
    print("=" * 50)
    
    try:
        monitor = RSSMonitor()
        monitor.check_and_push()
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return 1
    except Exception as e:
        print(f"❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

