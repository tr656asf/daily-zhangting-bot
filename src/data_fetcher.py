#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据获取模块 - 使用Playwright爬取财联社涨停分析
"""

import re
import logging
from datetime import datetime
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_zhangting_analysis(simulate_date=None):
    """
    获取当天涨停分析（使用Playwright爬取财联社）
    搜索格式：【X月X日涨停分析】财联社X月X日电
    
    Args:
        simulate_date: 模拟日期，格式为 datetime 对象，用于测试
    """
    if simulate_date:
        today = simulate_date
        logger.info(f"【模拟模式】使用日期：{today.strftime('%Y-%m-%d')}")
    else:
        today = datetime.now()
    
    month = today.month
    day = today.day
    date_str = f"{month}月{day}日"
    
    logger.info(f"开始获取 {date_str} 的涨停分析...")
    
    with sync_playwright() as p:
        # 启动浏览器（无头模式）
        logger.info("启动浏览器...")
        browser = p.chromium.launch(headless=True)
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        try:
            # 1. 访问财联社搜索页
            keyword = f"{date_str}涨停分析"
            search_url = f'https://www.cls.cn/searchPage?keyword={keyword}'
            
            logger.info(f"访问搜索页：{search_url}")
            page.goto(search_url, wait_until='networkidle', timeout=30000)
            page.wait_for_timeout(3000)  # 等待JS渲染
            
            # 2. 查找包含"【X月X日涨停分析】"的文章
            target_keyword = f"【{date_str}涨停分析】"
            logger.info(f"查找关键词：{target_keyword}")
            
            # 获取页面所有链接和文本
            links = page.query_selector_all('a')
            article_url = None
            
            for link in links:
                try:
                    text = link.inner_text()
                    href = link.get_attribute('href')
                    
                    # 找到包含目标关键词的链接
                    if target_keyword in text or ('涨停分析' in text and date_str in text):
                        if href:
                            article_url = href
                            logger.info(f"找到文章链接：{href}，文本：{text[:50]}")
                            break
                except:
                    continue
            
            if not article_url:
                logger.error("未找到文章链接")
                browser.close()
                return {
                    'source': f'涨停分析（{date_str}）',
                    'items': ['未找到财联社文章链接']
                }
            
            # 处理相对链接
            if not article_url.startswith('http'):
                article_url = f'https://www.cls.cn{article_url}'
            
            # 3. 打开文章页
            logger.info(f"打开文章页：{article_url}")
            page.goto(article_url, wait_until='networkidle', timeout=30000)
            page.wait_for_timeout(2000)
            
            # 4. 提取文章内容
            logger.info("提取文章内容...")
            content = None
            
            # 尝试多种选择器
            selectors = [
                '.dpu8C._2kCxD',      # 用户指定的class
                '.article-content',    # 财联社文章正文
                '.content-detail',
                '.news-content',
                'article',
                '.detail-content',
                '[class*="content"]',  # 模糊匹配
            ]
            
            for selector in selectors:
                try:
                    elem = page.query_selector(selector)
                    if elem:
                        content = elem.inner_text()
                        logger.info(f"使用选择器 '{selector}' 提取成功")
                        break
                except Exception as e:
                    continue
            
            # 如果都没找到，尝试提取所有文本
            if not content:
                logger.warning("标准选择器失败，尝试提取全部文本")
                content = page.inner_text('body')
                # 清理，只保留包含涨停相关内容的段落
                lines = content.split('\n')
                for line in lines:
                    if '涨停' in line and '【' in line and len(line) > 50:
                        content = line
                        break
            
            browser.close()
            
            if content:
                # 清理内容
                content = re.sub(r'\s+', ' ', content).strip()
                
                # 确保格式正确
                if not content.startswith('【'):
                    content = f"【{date_str}涨停分析】财联社{date_str}电，{content}"
                elif '财联社' not in content:
                    content = f"【{date_str}涨停分析】财联社{date_str}电，{content}"
                
                logger.info(f"成功获取内容，长度：{len(content)}")
                
                return {
                    'source': f'涨停分析（{date_str}）',
                    'items': [content]
                }
            else:
                return {
                    'source': f'涨停分析（{date_str}）',
                    'items': ['未能提取文章内容']
                }
                
        except Exception as e:
            logger.error(f"获取失败：{e}")
            import traceback
            logger.error(traceback.format_exc())
            browser.close()
            return {
                'source': f'涨停分析（{date_str}）',
                'items': [f'获取失败：{str(e)}']
            }


if __name__ == '__main__':
    result = get_zhangting_analysis()
    print(f"\n来源：{result['source']}")
    print(f"内容：{result['items'][0][:300]}...")
