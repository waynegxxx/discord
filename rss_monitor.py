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
import re
import html
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
    
    def fix_xml_entities(self, xml_content: str) -> str:
        """修复XML中的未定义实体"""
        # 定义常见的HTML实体映射
        entity_map = {
            '&nbsp;': ' ',
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&apos;': "'",
            '&copy;': '©',
            '&reg;': '®',
            '&trade;': '™',
            '&mdash;': '—',
            '&ndash;': '–',
            '&hellip;': '…',
            '&lsquo;': ''',
            '&rsquo;': ''',
            '&ldquo;': '"',
            '&rdquo;': '"',
        }
        
        # 先替换已知的实体
        for entity, replacement in entity_map.items():
            xml_content = xml_content.replace(entity, replacement)
        
        # 替换其他未定义的字母实体（保留数字实体如 &#123; 和 &#x1F;）
        def replace_undefined_entity(match):
            entity = match.group(0)
            # 数字实体已经由XML解析器处理，不需要替换
            # 只替换字母实体
            return ' '  # 未定义的实体替换为空格
        
        # 匹配 &字母实体; 格式（排除已处理的）
        xml_content = re.sub(r'&[a-zA-Z][a-zA-Z0-9]{1,15};', replace_undefined_entity, xml_content)
        
        return xml_content
    
    def fetch_rss(self, url: str) -> List[Dict]:
        """获取RSS源的最新文章"""
        feed = None
        original_feed = None
        
        try:
            # 先尝试直接解析（feedparser会自动下载）
            print(f"   正在获取RSS内容...")
            feed = feedparser.parse(url)
            original_feed = feed
            
            # 如果解析失败且有实体错误，尝试修复
            if feed.bozo and feed.bozo_exception:
                error_str = str(feed.bozo_exception)
                if 'undefined entity' in error_str.lower():
                    print(f"⚠️ 检测到XML实体错误，尝试修复...")
                    fixed_success = False
                    
                    # 重试机制：最多尝试3次
                    for attempt in range(1, 4):
                        try:
                            print(f"   尝试 {attempt}/3: 下载并修复RSS内容...")
                            # 下载RSS内容（增加超时时间到60秒）
                            response = requests.get(
                                url, 
                                timeout=(10, 60),  # (连接超时, 读取超时)
                                headers={
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                                }
                            )
                            response.raise_for_status()
                            xml_content = response.text
                            
                            # 修复XML实体
                            fixed_xml = self.fix_xml_entities(xml_content)
                            
                            # 重新解析
                            feed = feedparser.parse(fixed_xml)
                            
                            if feed.bozo and feed.bozo_exception:
                                print(f"   ⚠️ 修复后仍有解析错误: {feed.bozo_exception}")
                                # 即使有错误，也尝试提取内容
                            else:
                                print(f"   ✅ XML实体修复成功")
                                fixed_success = True
                                break
                        except requests.exceptions.Timeout as timeout_error:
                            print(f"   ⚠️ 尝试 {attempt}/3 超时: {timeout_error}")
                            if attempt < 3:
                                wait_time = attempt * 5  # 递增等待时间
                                print(f"   等待 {wait_time} 秒后重试...")
                                time.sleep(wait_time)
                            else:
                                print(f"   ⚠️ 所有重试均超时，尝试使用原始解析结果")
                        except Exception as fix_error:
                            print(f"   ⚠️ 尝试 {attempt}/3 失败: {fix_error}")
                            if attempt < 3:
                                time.sleep(2)
                            else:
                                print(f"   ⚠️ 修复失败，尝试使用原始解析结果（可能仍能提取部分内容）")
                    
                    # 如果修复失败，检查原始feed是否有内容（feedparser即使有错误也能提取部分内容）
                    if not fixed_success:
                        if original_feed and hasattr(original_feed, 'entries') and original_feed.entries:
                            feed = original_feed
                            print(f"   ℹ️ 使用原始解析结果（找到 {len(original_feed.entries)} 篇文章）")
                        else:
                            print(f"   ⚠️ 原始解析结果也没有文章，可能RSS源确实有问题")
                else:
                    print(f"⚠️ RSS解析错误 ({url}): {feed.bozo_exception}")
                    print(f"   尝试继续提取内容...")
            
            # 检查是否有文章（即使有错误也尝试提取）
            if not hasattr(feed, 'entries') or not feed.entries:
                print(f"⚠️ RSS源中没有文章条目")
                # 如果有错误信息，显示更多细节
                if feed.bozo and feed.bozo_exception:
                    print(f"   错误详情: {feed.bozo_exception}")
                return []
            
            articles = []
            for entry in feed.entries[:10]:  # 只取最新10条
                # 清理标题和摘要中的HTML标签
                title = entry.get('title', '无标题')
                summary = entry.get('summary', entry.get('description', ''))
                
                # 移除HTML标签
                if title:
                    title = re.sub(r'<[^>]+>', '', title)
                    title = html.unescape(title).strip()
                
                if summary:
                    summary = re.sub(r'<[^>]+>', '', summary)
                    summary = html.unescape(summary).strip()
                
                article = {
                    'title': title or '无标题',
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'summary': summary[:200] if summary else '',  # 限制摘要长度
                    'source': url
                }
                articles.append(article)
            
            return articles
        except requests.exceptions.RequestException as e:
            print(f"❌ 获取RSS失败 ({url}): 网络请求错误 - {e}")
            return []
        except Exception as e:
            print(f"❌ 获取RSS失败 ({url}): {e}")
            import traceback
            traceback.print_exc()
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
        
        # 清理摘要，移除HTML标签
        if summary:
            import re
            summary = re.sub(r'<[^>]+>', '', summary)
            summary = summary.strip()[:200]  # 限制长度
        
        # 构建elements列表
        elements = []
        
        # 标题
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**{title}**"
            }
        })
        
        # 发布时间（如果有）
        if published:
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"📅 {published}"
                }
            })
        
        # 摘要（如果有）
        if summary:
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"📝 {summary}"
                }
            })
        
        # 按钮（如果有链接）
        if link:
            elements.append({
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
            })
        
        # 飞书消息格式
        header_title = f"📰 {source_name} - 新文章推送" if source_name else "📰 新文章推送"
        
        message = {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True
                },
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": header_title
                    },
                    "template": "blue"
                },
                "elements": elements
            }
        }
        
        try:
            print(f"📤 正在发送到飞书: {title[:50]}...")
            print(f"   Webhook: {webhook_url[:50]}...")
            
            response = requests.post(webhook_url, json=message, timeout=10)
            print(f"   HTTP状态码: {response.status_code}")
            
            response.raise_for_status()
            result = response.json()
            print(f"   响应内容: {result}")
            
            if result.get('code') == 0:
                print(f"✅ 推送成功: {title[:50]}...")
                return True
            else:
                error_msg = result.get('msg', '未知错误')
                print(f"❌ 推送失败: {error_msg}")
                print(f"   完整响应: {result}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ 网络请求失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   响应状态码: {e.response.status_code}")
                print(f"   响应内容: {e.response.text[:200]}")
            return False
        except Exception as e:
            print(f"❌ 发送到飞书失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def check_and_push(self):
        """检查RSS源并推送新文章"""
        # 验证配置
        print("\n📋 配置检查:")
        print(f"   飞书Webhook: {'已配置' if self.config.get('feishu_webhook') else '❌ 未配置'}")
        
        rss_sources = self.config.get('rss_sources', [])
        if not rss_sources:
            print("⚠️ 未配置RSS源")
            return
        
        print(f"   RSS源数量: {len(rss_sources)}")
        for i, source in enumerate(rss_sources, 1):
            print(f"   {i}. {source.get('name', '未命名')}: {source.get('url', '无URL')}")
        
        new_count = 0
        
        for source in rss_sources:
            url = source.get('url', '')
            name = source.get('name', url)
            
            if not url:
                print(f"⚠️ 跳过无效RSS源: {name} (无URL)")
                continue
            
            print(f"\n🔍 检查RSS源: {name}")
            print(f"   URL: {url}")
            articles = self.fetch_rss(url)
            print(f"   获取到 {len(articles)} 篇文章")
            
            if not articles:
                print("   ⚠️ 未获取到文章，可能RSS源有问题")
                continue
            
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
                    else:
                        print(f"   ⚠️ 推送失败，但继续处理其他文章")
                    
                    # 避免发送过快
                    time.sleep(1)
                else:
                    print(f"   ✓ 已推送过: {article['title'][:50]}...")
        
        # 保存状态
        if new_count > 0:
            self.save_state()
            print(f"\n✨ 本次共推送 {new_count} 条新消息")
        else:
            print("\n✨ 暂无新消息（所有文章都已推送过）")


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

