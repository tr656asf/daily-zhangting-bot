#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网页爬取模块 - 百度搜索财联社涨停分析
"""

import re
import logging
import requests
from typing import Dict
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
            
            # 查找搜索结果中的链接
            for result in soup.select('.result'):
                link_elem = result.select_one('a[href]')
                if link_elem:
                    href = link_elem.get('href')
                    text = link_elem.get_text(strip=True)
                    if href and ('cls.cn' in href or '财联社' in text or '涨停' in text):
                        first_link = href
                        logger.info(f"找到链接：{href}，文本：{text[:30]}")
                        break
            
            # 如果没找到，尝试其他选择器
            if not first_link:
                for link in soup.find_all('a', href=True):
                    href = link.get('href')
                    text = link.get_text(strip=True)
                    if href and ('cls.cn' in href or '财联社' in text):
                        first_link = href
                        logger.info(f"找到备选链接：{href}")
                        break
            
            if not first_link:
                logger.error("未找到财联社链接")
                return {
                    'source': f'涨停分析（{date_str}）',
                    'items': ['未找到财联社文章链接']
                }
            
            # 处理百度跳转链接
            if 'baidu.com/link' in first_link:
                logger.info(f"处理百度跳转链接")
                try:
                    jump_response = self.session.get(first_link, timeout=10, allow_redirects=True)
                    final_url = jump_response.url
                    logger.info(f"跳转后URL：{final_url}")
                    first_link = final_url
                except Exception as e:
                    logger.error(f"跳转解析失败：{e}")
            
            # 3. 访问第一个链接
            logger.info(f"访问文章页面：{first_link}")
            article_response = self.session.get(first_link, timeout=15)
            article_response.encoding = 'utf-8'
            
            logger.info(f"文章页面状态码：{article_response.status_code}")
            
            # 保存部分HTML用于调试
            html_sample = article_response.text[:2000]
            logger.info(f"HTML样本：{html_sample}")
            
            # 4. 解析文章页面，尝试多种方式提取内容
            article_soup = BeautifulSoup(article_response.text, 'html.parser')
            
            content = None
            
            # 方法1：尝试查找用户指定的class
            logger.info("尝试方法1：查找dpu8C _2kCxD...")
            target_div = article_soup.find('div', class_=lambda x: x and 'dpu8C' in str(x) and '_2kCxD' in str(x))
            if target_div:
                content = target_div.get_text(strip=True)
                logger.info(f"方法1成功，内容长度：{len(content)}")
            
            # 方法2：查找财联社文章正文常用class
            if not content:
                logger.info("尝试方法2：查找财联社文章正文...")
                for class_name in ['article-content', 'content-detail', 'news-content', 'detail-content', 
                                   'article-body', 'post-content', 'main-content']:
                    elem = article_soup.find(['div', 'article'], class_=class_name)
                    if elem:
                        content = elem.get_text(strip=True)
                        logger.info(f"方法2成功，class={class_name}，长度：{len(content)}")
                        break
            
            # 方法3：查找包含"涨停"关键词的最大文本块
            if not content:
                logger.info("尝试方法3：查找包含涨停的文本块...")
                candidates = []
                for elem in article_soup.find_all(['div', 'p', 'section']):
                    text = elem.get_text(strip=True)
                    if '涨停' in text and '股' in text and len(text) > 100:
                        candidates.append(text)
                
                if candidates:
                    # 找最长的那个
                    content = max(candidates, key=len)
                    logger.info(f"方法3成功，长度：{len(content)}")
            
            # 方法4：提取所有段落组合
            if not content:
                logger.info("尝试方法4：组合段落...")
                paragraphs = []
                for p in article_soup.find_all('p'):
                    text = p.get_text(strip=True)
                    if len(text) > 20:
                        paragraphs.append(text)
                
                if paragraphs:
                    # 找包含"涨停"的连续段落
                    for i, p in enumerate(paragraphs):
                        if '涨停' in p and '【' in p:
                            # 从这个段落开始，取接下来的3段
                            content = ' '.join(paragraphs[i:i+3])
                            logger.info(f"方法4成功，长度：{len(content)}")
                            break
            
            if content:
                # 清理内容
                content = re.sub(r'\s+', ' ', content)
                content = content.strip()
                
                # 确保包含日期前缀
                if not content.startswith('【'):
                    content = f"【{date_str}涨停分析】财联社{date_str}电，{content}"
                
                logger.info(f"最终内容长度：{len(content)}")
                
                return {
                    'source': f'涨停分析（{date_str}）',
                    'items': [content]
                }
            else:
                logger.error("所有方法都未能提取内容")
                return {
                    'source': f'涨停分析（{date_str}）',
                    'items': [f'未找到文章内容，HTML样本：{html_sample[:500]}']
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
    scraper = WebScraper()
    result = scraper.fetch_zhangting_analysis()
    print(f"\n来源：{result['source']}")
    print(f"内容：{result['items'][0][:300]}...")
