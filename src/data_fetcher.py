#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据获取模块 - 百度搜索财联社涨停分析
"""

import re
import logging
import requests
from datetime import datetime
from urllib.parse import quote
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_zhangting_analysis(target_date=None):
    """
    获取涨停分析
    
    Args:
        target_date: 目标日期，datetime对象。如果为None，使用当前日期
    """
    # 确定日期
    if target_date is None:
        target_date = datetime.now()
    
    month = target_date.month
    day = target_date.day
    date_str = f"{month}月{day}日"  # → "3月3日"
    
    logger.info(f"获取 {date_str} 的涨停分析...")
    
    # 百度搜索
    return _search_from_baidu(date_str)


def _search_from_baidu(date_str):
    """
    百度搜索指定日期的涨停分析
    搜索关键词：【2月5日涨停分析】财联社
    """
    try:
        # 构造百度搜索关键词
        keyword = f"【{date_str}涨停分析】财联社"
        search_url = f'https://www.baidu.com/s?wd={quote(keyword)}'
        
        logger.info(f"百度搜索: {keyword}")
        logger.info(f"搜索URL: {search_url}")
        
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
        content = None
        
        # 方法1：查找包含 "涨停分析】财联社" 的 em 标签
        logger.info("查找 em 标签...")
        for em in soup.find_all('em'):
            em_text = em.get_text(strip=True)
            if '涨停分析】财联社' in em_text:
                logger.info(f"找到 em 标签: {em_text}")
                # 获取父元素
                parent = em.parent
                if parent:
                    content = parent.get_text(strip=True)
                    logger.info(f"从父元素提取内容，长度: {len(content)}")
                    break
        
        # 方法2：如果没找到，尝试查找包含特定class的div
        if not content:
            logger.info("方法1失败，尝试查找 summary-text 类...")
            for elem in soup.find_all(['div', 'span'], class_=lambda x: x and ('summary' in str(x) or 'content' in str(x))):
                text = elem.get_text(strip=True)
                if '涨停分析】财联社' in text and '股涨停' in text:
                    content = text
                    logger.info(f"找到 summary-text 内容，长度: {len(content)}")
                    break
        
        # 方法3：直接搜索页面文本
        if not content:
            logger.info("方法2失败，尝试正则提取...")
            # 匹配从 "【X月X日涨停分析】" 开始的内容
            pattern = r'【\d+月\d+日涨停分析】财联社.*?(?:今日全市场共\d+股涨停.*?(?:焦点股方面|。))'
            matches = re.findall(pattern, response.text)
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
                idx = content.find('【')
                if idx > 0:
                    content = content[idx:]
            
            # 截断多余内容（只保留到焦点股描述结束）
            if '焦点股方面' in content:
                # 找到焦点股部分，保留到第一个句号
                focus_idx = content.find('焦点股方面')
                if focus_idx > 0:
                    # 从焦点股开始往后找句号
                    after_focus = content[focus_idx:]
                    period_idx = after_focus.find('。')
                    if period_idx > 0:
                        content = content[:focus_idx] + after_focus[:period_idx+1]
            
            logger.info(f"最终内容: {content[:100]}...")
            
            return {
                'source': f'涨停分析（{date_str}）',
                'items': [content]
            }
        else:
            logger.error("未能从百度搜索结果中提取内容")
            return {
                'source': f'涨停分析（{date_str}）',
                'items': ['未能提取内容']
            }
            
    except Exception as e:
        logger.error(f"获取失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            'source': f'涨停分析（{date_str}）',
            'items': [f'获取失败: {str(e)}']
        }


if __name__ == '__main__':
    # 测试
    result = get_zhangting_analysis()
    print(f"\n来源: {result['source']}")
    print(f"内容: {result['items'][0]}")
