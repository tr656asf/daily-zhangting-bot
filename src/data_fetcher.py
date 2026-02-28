#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据获取模块 - 支持正常模式和模拟模式
"""

import re
import logging
import requests
from datetime import datetime
from urllib.parse import quote
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_zhangting_analysis(simulate_date=None):
    """
    获取涨停分析
    
    Args:
        simulate_date: 模拟日期，datetime对象。如果提供，使用模拟模式
    """
    if simulate_date:
        # 模拟模式：百度搜索固定内容
        return _get_from_baidu_search(simulate_date)
    else:
        # 正常模式：使用Playwright爬取财联社（保持原有功能）
        return _get_from_cls_playwright(datetime.now())


def _get_from_baidu_search(simulate_date):
    """
    模拟模式：百度搜索指定日期的涨停分析
    搜索关键词：【2月5日涨停分析】财联社
    """
    month = simulate_date.month
    day = simulate_date.day
    date_str = f"{month}月{day}日"
    
    logger.info(f"【模拟模式】百度搜索 {date_str} 涨停分析")
    
    try:
        # 构造百度搜索关键词
        keyword = f"【{date_str}涨停分析】财联社"
        search_url = f'https://www.baidu.com/s?wd={quote(keyword)}'
        
        logger.info(f"百度搜索URL: {search_url}")
        
        # 设置请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        
        # 发送请求
        response = requests.get(search_url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        
        logger.info(f"百度响应状态码: {response.status_code}")
        
        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找包含目标内容的元素
        # 根据用户提供的信息，查找包含 "涨停分析】财联社" 的 em 标签
        content = None
        
        # 方法1：查找包含 "涨停分析】财联社" 的 em 标签
        logger.info("查找 em 标签...")
        for em in soup.find_all('em'):
            em_text = em.get_text(strip=True)
            if '涨停分析】财联社' in em_text:
                logger.info(f"找到 em 标签: {em_text}")
                # 获取父元素（应该是 span 或 div）
                parent = em.parent
                if parent:
                    content = parent.get_text(strip=True)
                    logger.info(f"从父元素提取内容，长度: {len(content)}")
                    break
        
        # 方法2：如果没找到，尝试查找包含特定class的div
        if not content:
            logger.info("方法1失败，尝试查找 summary-text 类...")
            for div in soup.find_all(['div', 'span'], class_=lambda x: x and 'summary' in str(x)):
                text = div.get_text(strip=True)
                if '涨停分析】财联社' in text and '股涨停' in text:
                    content = text
                    logger.info(f"找到 summary-text 内容，长度: {len(content)}")
                    break
        
        # 方法3：直接搜索整个页面文本
        if not content:
            logger.info("方法2失败，尝试正则提取...")
            # 使用正则匹配从 "【X月X日涨停分析】" 到 "</span>" 之间的内容
            pattern = r'【\d+月\d+日涨停分析】财联社.*?(?:</span>|</div>|</p>)'
            matches = re.findall(pattern, response.text, re.DOTALL)
            if matches:
                # 清理HTML标签
                content = re.sub(r'<[^>]+>', '', matches[0])
                content = re.sub(r'\s+', ' ', content)
                logger.info(f"正则提取成功，长度: {len(content)}")
        
        if content:
            # 清理内容
            content = content.strip()
            
            # 确保内容以【开头
            if not content.startswith('【'):
                # 查找【的位置
                idx = content.find('【')
                if idx > 0:
                    content = content[idx:]
            
            # 截断多余内容（只保留到第一个句号后的合理位置）
            # 查找 "焦点股方面" 后的内容，通常到这里就够了
            end_markers = ['。', '；']
            for marker in end_markers:
                if f'焦点股方面' in content and marker in content:
                    # 找到最后一个焦点股之后的句号
                    parts = content.split('焦点股方面')
                    if len(parts) > 1:
                        focus_part = parts[1]
                        # 找到焦点股部分的最后一个句号
                        last_period = focus_part.rfind('。')
                        if last_period > 0:
                            content = parts[0] + '焦点股方面' + focus_part[:last_period+1]
                            break
            
            logger.info(f"最终内容: {content[:100]}...")
            
            return {
                'source': f'涨停分析（{date_str}）- 模拟模式',
                'items': [content]
            }
        else:
            logger.error("未能从百度搜索结果中提取内容")
            # 保存部分HTML用于调试
            html_sample = response.text[:2000]
            logger.info(f"HTML样本: {html_sample}")
            
            return {
                'source': f'涨停分析（{date_str}）',
                'items': ['未能提取内容，请检查百度搜索结果页面结构']
            }
            
    except Exception as e:
        logger.error(f"模拟模式获取失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            'source': f'涨停分析（{date_str}）',
            'items': [f'获取失败: {str(e)}']
        }


def _get_from_cls_playwright(today):
    """
    正常模式：使用Playwright爬取财联社（原有功能）
    """
    # 这里保留原来的Playwright代码
    # 为简化，先返回提示信息
    month = today.month
    day = today.day
    date_str = f"{month}月{day}日"
    
    logger.info(f"正常模式：使用Playwright爬取财联社 {date_str}")
    
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            
            try:
                # 访问财联社搜索页
                keyword = f"{date_str}涨停分析"
                search_url = f'https://www.cls.cn/searchPage?keyword={keyword}'
                
                logger.info(f"访问搜索页: {search_url}")
                page.goto(search_url, wait_until='networkidle', timeout=30000)
                page.wait_for_timeout(3000)
                
                # 查找文章链接
                target_keyword = f"【{date_str}涨停分析】"
                links = page.query_selector_all('a')
                article_url = None
                
                for link in links:
                    try:
                        text = link.inner_text()
                        href = link.get_attribute('href')
                        if target_keyword in text or ('涨停分析' in text and date_str in text):
                            if href:
                                article_url = href
                                break
                    except:
                        continue
                
                if not article_url:
                    browser.close()
                    return {
                        'source': f'涨停分析（{date_str}）',
                        'items': ['未找到文章链接']
                    }
                
                if not article_url.startswith('http'):
                    article_url = f'https://www.cls.cn{article_url}'
                
                # 打开文章页
                page.goto(article_url, wait_until='networkidle', timeout=30000)
                page.wait_for_timeout(2000)
                
                # 提取内容
                content = None
                selectors = ['.dpu8C._2kCxD', '.article-content', '.content-detail', '.news-content']
                
                for selector in selectors:
                    try:
                        elem = page.query_selector(selector)
                        if elem:
                            content = elem.inner_text()
                            break
                    except:
                        continue
                
                browser.close()
                
                if content:
                    content = re.sub(r'\s+', ' ', content).strip()
                    if not content.startswith('【'):
                        content = f"【{date_str}涨停分析】财联社{date_str}电，{content}"
                    
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
                browser.close()
                raise e
                
    except Exception as e:
        logger.error(f"正常模式获取失败: {e}")
        return {
            'source': f'涨停分析（{date_str}）',
            'items': [f'获取失败: {str(e)}']
        }


if __name__ == '__main__':
    # 测试模拟模式
    test_date = datetime(2026, 2, 5)
    result = get_zhangting_analysis(simulate_date=test_date)
    print(f"\n来源: {result['source']}")
    print(f"内容: {result['items'][0][:300]}...")
