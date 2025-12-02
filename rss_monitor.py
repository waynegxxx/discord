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
        
        # 准备请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache'
        }
        
        try:
            # 先尝试使用requests下载，然后解析（这样可以控制请求头）
            print(f"   正在获取RSS内容...")
            try:
                response = requests.get(url, headers=headers, timeout=(10, 30), allow_redirects=True)
                response.raise_for_status()
                
                # 检查是否是RSSHub的错误
                if 'rsshub.app' in url:
                    if response.status_code == 403:
                        print(f"   ⚠️ RSSHub返回403错误，可能的原因：")
                        print(f"      1. RSSHub公共实例有访问限制")
                        print(f"      2. 该路由需要特殊权限或已失效")
                        print(f"      3. 建议使用自建RSSHub实例或更换RSS源")
                        print(f"      4. 可以尝试访问 https://rsshub.app 查看该路由是否可用")
                        return []
                    elif response.status_code == 404:
                        print(f"   ❌ RSSHub返回404错误，路由不存在或格式错误")
                        print(f"      当前路由: {url}")
                        print(f"      可能的原因：")
                        print(f"      1. 路由格式不正确（检查RSSHub文档）")
                        print(f"      2. 路由已失效或已变更")
                        print(f"      3. 用户名或参数错误")
                        print(f"      解决建议：")
                        print(f"      - 访问 https://docs.rsshub.app/ 查看正确的路由格式")
                        print(f"      - 在浏览器中访问该路由验证是否可用")
                        print(f"      - 检查路由参数是否正确")
                        # 如果是Twitter路由，提供格式提示
                        if '/twitter/' in url:
                            print(f"      Twitter路由格式示例：")
                            print(f"      - 用户推文: https://rsshub.app/twitter/user/用户名")
                            print(f"      - 用户媒体: https://rsshub.app/twitter/media/用户名（可能不存在）")
                            print(f"      - 列表: https://rsshub.app/twitter/list/列表ID")
                        return []
                
                # 使用下载的内容解析
                feed = feedparser.parse(response.content)
                original_feed = feed
            except requests.exceptions.HTTPError as http_error:
                status_code = http_error.response.status_code if http_error.response else None
                if status_code == 403:
                    print(f"   ❌ 访问被拒绝 (403): {url}")
                    if 'rsshub.app' in url:
                        print(f"      RSSHub可能需要认证或该路由已失效")
                    return []
                elif status_code == 404:
                    print(f"   ❌ 路由不存在 (404): {url}")
                    if 'rsshub.app' in url:
                        print(f"      RSSHub路由可能格式错误或已失效")
                        print(f"      建议：访问 https://docs.rsshub.app/ 查看正确的路由格式")
                        # 如果是Twitter路由，提供格式提示
                        if '/twitter/' in url:
                            print(f"      Twitter路由正确格式：")
                            print(f"      - https://rsshub.app/twitter/user/用户名")
                    return []
                raise
            except requests.exceptions.RequestException as req_error:
                # 如果requests失败，尝试使用feedparser直接解析
                print(f"   ⚠️ 使用requests下载失败，尝试feedparser直接解析...")
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
                                headers=headers,
                                allow_redirects=True
                            )
                            
                            # 检查403错误
                            if response.status_code == 403:
                                print(f"   ❌ 访问被拒绝 (403)，无法修复")
                                if 'rsshub.app' in url:
                                    print(f"      RSSHub路由可能已失效或需要认证")
                                break
                            
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
                        except requests.exceptions.HTTPError as http_error:
                            if http_error.response.status_code == 403:
                                print(f"   ❌ 访问被拒绝 (403)，无法修复")
                                if 'rsshub.app' in url:
                                    print(f"      RSSHub路由可能已失效或需要认证")
                                break
                            else:
                                print(f"   ⚠️ 尝试 {attempt}/3 HTTP错误: {http_error}")
                                if attempt < 3:
                                    time.sleep(2)
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
                error_detail = ""
                if feed.bozo and feed.bozo_exception:
                    error_detail = str(feed.bozo_exception)
                    print(f"⚠️ RSS源中没有文章条目")
                    print(f"   错误详情: {error_detail}")
                else:
                    print(f"⚠️ RSS源中没有文章条目")
                    # 检查是否是Nitter源
                    if 'nitter' in url.lower():
                        print(f"   ℹ️ 这是Nitter源，可能的原因：")
                        print(f"      1. 用户名不存在或已更改")
                        print(f"      2. 用户没有推文")
                        print(f"      3. 账户被保护或已注销")
                        print(f"      4. Nitter实例无法获取该用户内容")
                        print(f"      建议：在浏览器中访问 {url} 验证")
                # 返回空列表，错误信息会在check_and_push中处理
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
            error_msg = str(e)
            print(f"❌ 获取RSS失败 ({url}): 网络请求错误 - {e}")
            # 如果是404错误，提供更详细的提示
            if '404' in error_msg and 'rsshub.app' in url:
                print(f"   提示：RSSHub路由可能不存在或格式错误")
                print(f"   建议：访问 https://docs.rsshub.app/ 查看正确的路由格式")
            # 抛出异常，让check_and_push捕获并发送错误通知
            raise Exception(f"网络请求错误: {error_msg}")
        except Exception as e:
            print(f"❌ 获取RSS失败 ({url}): {e}")
            import traceback
            traceback.print_exc()
            # 抛出异常，让check_and_push捕获并发送错误通知
            raise
    
    def send_error_to_discord(self, source_name: str, url: str, error_type: str, error_message: str = ""):
        """发送错误/状态消息到Discord"""
        webhook_url = self.config.get('discord_webhook')
        if not webhook_url:
            print("❌ 未配置Discord Webhook地址")
            return False
        
        # 根据错误类型设置颜色和图标
        error_colors = {
            'error': 0xFF0000,      # 红色
            'warning': 0xFFA500,   # 橙色
            'info': 0x5865F2,      # Discord蓝色
            'empty': 0x808080      # 灰色
        }
        
        error_icons = {
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
            'empty': '📭'
        }
        
        color = error_colors.get(error_type, 0xFF0000)
        icon = error_icons.get(error_type, '❌')
        
        # 构建错误消息
        title = f"{icon} RSS监控 - {source_name}"
        description = f"**状态**: {error_type.upper()}\n"
        
        if error_message:
            description += f"**错误信息**: {error_message[:500]}\n"
        
        description += f"**RSS源**: {url}"
        
        # 构建Discord Embed消息
        embed = {
            "title": title[:256],
            "description": description[:2000],  # Discord限制2000字符
            "color": color,
            "timestamp": datetime.now().isoformat(),
            "footer": {
                "text": "RSS监控系统"
            },
            "fields": [
                {
                    "name": "🔗 RSS链接",
                    "value": url[:1024],  # Discord字段值限制1024字符
                    "inline": False
                }
            ]
        }
        
        message = {
            "embeds": [embed]
        }
        
        try:
            print(f"📤 正在发送错误通知到Discord: {source_name}...")
            print(f"   Webhook: {webhook_url[:50]}...")
            response = requests.post(webhook_url, json=message, timeout=10)
            print(f"   HTTP状态码: {response.status_code}")
            response.raise_for_status()
            
            if response.status_code in [200, 204]:
                print(f"✅ 错误通知发送成功")
                return True
            else:
                print(f"❌ 错误通知发送失败: HTTP {response.status_code}")
                print(f"   响应内容: {response.text[:200]}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ 发送错误通知失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   响应状态码: {e.response.status_code}")
                print(f"   响应内容: {e.response.text[:200]}")
                print("\n可能的原因：")
                print("   1. Discord Webhook地址格式错误")
                print("   2. Webhook已失效或被删除")
                print("   3. 网络连接问题")
            return False
        except Exception as e:
            print(f"❌ 发送错误通知失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def send_to_discord(self, article: Dict, source_name: str = ""):
        """发送消息到Discord（使用纯文本格式，避免Embed格式问题）"""
        webhook_url = self.config.get('discord_webhook')
        if not webhook_url:
            print("❌ 未配置Discord Webhook地址")
            return False
        
        # 构建消息内容
        title = article.get('title', '无标题')
        link = article.get('link', '')
        summary = article.get('summary', '')
        published = article.get('published', '')
        
        # 清理标题，移除HTML标签
        if title:
            title = re.sub(r'<[^>]+>', '', title)
            title = html.unescape(title).strip()
        else:
            title = "无标题"
        
        # 清理摘要，移除HTML标签
        if summary:
            summary = re.sub(r'<[^>]+>', '', summary)
            summary = html.unescape(summary).strip()
        
        # 构建纯文本消息（使用Discord Markdown格式）
        # Discord content字段限制2000字符
        content_parts = []
        
        # 标题（加粗）
        if title:
            # 转义Discord特殊字符，避免格式问题
            title_escaped = title.replace('*', '\\*').replace('_', '\\_').replace('`', '\\`').replace('~', '\\~')
            content_parts.append(f"**{title_escaped[:1900]}**")  # 留出空间给其他内容
        
        # 摘要
        if summary:
            summary_escaped = summary.replace('*', '\\*').replace('_', '\\_').replace('`', '\\`').replace('~', '\\~')
            # 计算剩余空间
            current_length = sum(len(part) for part in content_parts) + len('\n') * (len(content_parts) - 1)
            remaining = 2000 - current_length - 50  # 留出空间给链接等
            if remaining > 0:
                content_parts.append(f"\n{summary_escaped[:remaining]}")
        
        # 链接
        if link:
            content_parts.append(f"\n🔗 {link}")
        
        # 发布时间（如果有）
        if published:
            # 简单格式化日期
            try:
                # 尝试提取日期部分
                date_str = published.split(' (')[0].split(' +')[0].split(' -')[0]
                content_parts.append(f"\n📅 {date_str}")
            except:
                pass
        
        # 来源（如果有）
        if source_name:
            content_parts.append(f"\n📰 来源: {source_name}")
        
        # 组合所有内容
        content = '\n'.join(content_parts)
        
        # 确保不超过2000字符限制
        if len(content) > 2000:
            content = content[:1997] + "..."
        
        # 构建消息（使用content字段，不使用embeds）
        message = {
            "content": content
        }
        
        try:
            print(f"📤 正在发送到Discord: {title[:50]}...")
            print(f"   Webhook: {webhook_url[:50]}...")
            print(f"   消息长度: {len(content)} 字符")
            
            response = requests.post(webhook_url, json=message, timeout=10)
            print(f"   HTTP状态码: {response.status_code}")
            
            response.raise_for_status()
            
            # Discord成功返回204 No Content或200 OK
            if response.status_code in [200, 204]:
                print(f"✅ 推送成功: {title[:50]}...")
                return True
            else:
                print(f"❌ 推送失败: HTTP {response.status_code}")
                print(f"   响应内容: {response.text[:200]}")
                return False
        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP错误: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   响应状态码: {e.response.status_code}")
                print(f"   响应内容: {e.response.text[:500]}")
            return False
        except requests.exceptions.RequestException as e:
            print(f"❌ 网络请求失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   响应状态码: {e.response.status_code}")
                print(f"   响应内容: {e.response.text[:200]}")
            return False
        except Exception as e:
            print(f"❌ 发送到Discord失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
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
        print(f"   Discord Webhook: {'已配置' if self.config.get('discord_webhook') else '❌ 未配置'}")
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
            
            # 捕获获取RSS时的错误信息
            error_info = None
            try:
                articles = self.fetch_rss(url)
                print(f"   获取到 {len(articles)} 篇文章")
            except Exception as e:
                error_info = str(e)
                articles = []
                print(f"   ❌ 获取RSS时发生异常: {e}")
            
            # 如果没有获取到文章，发送错误通知
            if not articles:
                error_message = "未获取到文章"
                error_type = 'warning'
                
                if error_info:
                    error_message = f"获取失败: {error_info}"
                    # 根据错误类型设置不同的错误级别
                    if '404' in error_info:
                        error_type = 'error'
                        error_message = "路由不存在 (404)"
                    elif '403' in error_info:
                        error_type = 'error'
                        error_message = "访问被拒绝 (403)"
                    elif 'timeout' in error_info.lower() or '超时' in error_info:
                        error_type = 'warning'
                        error_message = "请求超时"
                    else:
                        error_type = 'error'
                elif 'nitter' in url.lower():
                    # Nitter特定错误
                    error_message = "Nitter源返回空内容，可能用户名不存在或用户没有推文"
                    error_type = 'warning'
                    print(f"   ℹ️ Nitter源提示：")
                    print(f"      - 检查用户名是否正确")
                    print(f"      - 在浏览器中访问 {url} 验证")
                    print(f"      - 尝试其他Nitter实例")
                elif 'rsshub.app' in url:
                    # RSSHub特定错误
                    error_message = "RSSHub路由可能有问题"
                    error_type = 'warning'
                
                # 发送错误通知到Discord
                if self.config.get('discord_webhook'):
                    self.send_error_to_discord(
                        source_name=name,
                        url=url,
                        error_type=error_type,
                        error_message=error_message
                    )
                elif self.config.get('feishu_webhook'):
                    # 飞书也可以发送错误通知，但这里先只实现Discord
                    pass
                
                print("   ⚠️ 未获取到文章，已发送错误通知")
                continue
            
            for article in articles:
                article_id = self.get_article_id(article)
                source_key = f"{url}_{article_id}"
                
                # 检查是否已推送
                if source_key not in self.state:
                    print(f"📬 发现新文章: {article['title'][:50]}...")
                    
                    # 发送到Discord（优先）或飞书
                    success = False
                    if self.config.get('discord_webhook'):
                        success = self.send_to_discord(article, name)
                    elif self.config.get('feishu_webhook'):
                        success = self.send_to_feishu(article, name)
                    else:
                        print("   ⚠️ 未配置任何Webhook地址")
                    
                    if success:
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
            print("\n💡 提示：")
            print("   - 首次运行会推送RSS源中的最新文章（最多10条）")
            print("   - 之后只会推送新发布的文章")
            print("   - 如果想重新推送所有文章，可以删除 rss_state.json 文件")
            print("   - 如果RSS源有问题，会发送错误通知到Discord")


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

