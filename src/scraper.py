#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网页爬取模块 - 百度搜索财联社涨停分析
"""

import re
import logging
import requests
from typing import List, Dict
from urllib.parse import quote
from bs4 import BeautifulSoup
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebScraper:
    """网页爬虫"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        })
    
    def fetch_zhangting_analysis(self) -> Dict:
        """
        爬取当天涨停分析（财联社）
        搜索格式：【2月27日涨停分析】财联社2月27日电
        然后打开第一个链接，提取class="dpu8C _2kCxD"的div内容
        """
        today = datetime.now()
        month = today.month
        day = today.day
        date_str = f"{month}月{day}日"
        
        # 构造搜索关键词
        keyword = f"【{date_str}涨停分析】财联社{date_str}电"
        
        logger.info(f"搜索关键词：{keyword}")
        
        try:
            # 1. 百度搜索
            search_url = f'https://www.baidu.com/s?wd={quote(keyword)}'
            logger.info(f"百度搜索URL：{search_url}")
            
            response = self.session.get(search_url, timeout=15)
            response.encoding = 'utf-8'
            
            logger.info(f"百度响应状态码：{response.status_code}")
            
            # 2. 解析搜索结果，获取第一个链接
            soup = BeautifulSoup(response.text, 'html.parser')
            
            first_link = None
            
            # 查找搜索结果中的第一个链接
            # 百度结果通常在 .result 或特定div中
            for result in soup.select('.result'):
                link_elem = result.select_one('a[href]')
                if link_elem:
                    href = link_elem.get('href')
                    if href and ('cls.cn' in href or 'baidu.com/link' in href):
                        first_link = href
                        logger.info(f"找到财联社链接：{first_link}")
                        break
            
            # 如果没找到直接链接，尝试提取所有链接
            if not first_link:
                for link in soup.find_all('a', href=True):
                    href = link.get('href')
                    text = link.get_text(strip=True)
                    if href and ('cls.cn' in href or '财联社' in text):
                        first_link = href
                        logger.info(f"找到备选链接：{first_link}")
                        break
            
            if not first_link:
                logger.error("未找到财联社链接")
                return {
                    'source': f'涨停分析（{date_str}）',
                    'items': ['未找到财联社文章链接']
                }
            
            # 处理百度跳转链接
            if 'baidu.com/link' in first_link:
                # 需要解析跳转
                logger.info(f"处理百度跳转链接：{first_link}")
                jump_response = self.session.get(first_link, timeout=10, allow_redirects=True)
                final_url = jump_response.url
                logger.info(f"跳转后URL：{final_url}")
                first_link = final_url
            
            # 3. 访问第一个链接
            logger.info(f"访问文章页面：{first_link}")
            article_response = self.session.get(first_link, timeout=15)
            article_response.encoding = 'utf-8'
            
            logger.info(f"文章页面状态码：{article_response.status_code}")
            
            # 4. 解析文章页面，提取class="dpu8C _2kCxD"的div
            article_soup = BeautifulSoup(article_response.text, 'html.parser')
            
            # 查找指定的div
            target_div = article_soup.find('div', class_=lambda x: x and 'dpu8C' in x and '_2kCxD' in x)
            
            if not target_div:
                # 尝试模糊匹配
                logger.info("精确匹配失败，尝试模糊匹配...")
                for div in article_soup.find_all('div'):
                    div_class = div.get('class', [])
                    if isinstance(div_class, list):
                        div_class_str = ' '.join(div_class)
                    else:
                        div_class_str = str(div_class)
                    
                    if 'dpu8C' in div_class_str or '_2kCxD' in div_class_str:
                        target_div = div
                        logger.info(f"找到模糊匹配div，class: {div_class_str}")
                        break
            
            if target_div:
                content = target_div.get_text(strip=True)
                logger.info(f"成功提取内容，长度：{len(content)}")
                
                # 清理内容
                content = re.sub(r'\s+', ' ', content)
                
                return {
                    'source': f'涨停分析（{date_str}）',
                    'items': [content]
                }
            else:
                logger.error("未找到class为dpu8C _2kCxD的div")
                # 保存HTML用于调试
                html_preview = article_response.text[:1000]
                logger.info(f"HTML预览：{html_preview}")
                
                return {
                    'source': f'涨停分析（{date_str}）',
                    'items': ['未找到文章内容（div class=dpu8C _2kCxD不存在）']
                }
            
        except Exception as e:
            logger.error(f"爬取失败：{e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'source': f'涨停分析（{date_str}）',
                'items': [f'获取失败：{str(e)}']
            }


if __name__ == '__main__':
    # 测试
    scraper = WebScraper()
    result = scraper.fetch_zhangting_analysis()
    print(f"\n来源：{result['source']}")
    print(f"内容：{result['items'][0]}")
