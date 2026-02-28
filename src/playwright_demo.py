#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Playwright 示例：搜索财联社2月5日涨停分析
"""

import logging
from datetime import datetime
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def search_cls_zhangting(target_month=2, target_day=5):
    """
    使用Playwright搜索财联社指定日期的涨停分析
    
    Args:
        target_month: 目标月份（默认2月）
        target_day: 目标日期（默认5日）
    """
    
    # 构建搜索关键词
    date_str = f"{target_month}月{target_day}日"
    keyword = f"【{date_str}涨停分析】"
    search_url = f'https://www.cls.cn/searchPage?keyword={date_str}涨停分析'
    
    logger.info(f"开始搜索：{keyword}")
    logger.info(f"搜索URL：{search_url}")
    
    with sync_playwright() as p:
        # 启动浏览器（无头模式）
        logger.info("启动浏览器...")
        browser = p.chromium.launch(headless=True)
        
        # 创建新页面
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        try:
            # 1. 访问搜索页面
            logger.info(f"访问搜索页：{search_url}")
            page.goto(search_url, wait_until='networkidle', timeout=30000)
            
            # 等待页面加载（等待搜索结果出现）
            logger.info("等待搜索结果加载...")
            page.wait_for_timeout(3000)  # 等待3秒确保JS渲染完成
            
            # 2. 查找包含"【2月5日涨停分析】"的文章
            logger.info(f"查找包含'{keyword}'的文章...")
            
            # 获取页面所有文本内容
            page_text = page.inner_text('body')
            
            # 检查是否找到目标内容
            if keyword in page_text:
                logger.info(f"✅ 找到'{keyword}'内容")
                
                # 查找文章链接（通常在搜索结果列表中）
                # 财联社的搜索结果选择器
                selectors = [
                    '.search-result-item',
                    '.news-item',
                    '.article-item',
                    '[class*="search"] a',
                    'a[href*="detail"]'
                ]
                
                article_link = None
                for selector in selectors:
                    try:
                        elements = page.query_selector_all(selector)
                        for elem in elements:
                            text = elem.inner_text()
                            if keyword in text or '涨停分析' in text:
                                # 找到链接
                                link_elem = elem.query_selector('a') if elem.tag_name != 'a' else elem
                                if link_elem:
                                    article_link = link_elem.get_attribute('href')
                                    logger.info(f"找到文章链接：{article_link}")
                                    break
                        if article_link:
                            break
                    except Exception as e:
                        continue
                
                # 3. 如果找到链接，打开文章页
                if article_link:
                    if not article_link.startswith('http'):
                        article_link = f'https://www.cls.cn{article_link}'
                    
                    logger.info(f"打开文章页：{article_link}")
                    page.goto(article_link, wait_until='networkidle', timeout=30000)
                    page.wait_for_timeout(2000)
                    
                    # 4. 提取文章内容
                    logger.info("提取文章内容...")
                    
                    # 尝试多种选择器提取正文
                    content_selectors = [
                        '.dpu8C._2kCxD',  # 用户指定的class
                        '.article-content',
                        '.content-detail',
                        '.news-content',
                        'article',
                        '.detail-content',
                        '[class*="content"]'
                    ]
                    
                    content = None
                    for selector in content_selectors:
                        try:
                            if page.query_selector(selector):
                                content = page.inner_text(selector)
                                logger.info(f"使用选择器 '{selector}' 提取成功，长度：{len(content)}")
                                break
                        except:
                            continue
                    
                    if content:
                        # 清理内容
                        content = content.strip()
                        # 确保包含日期前缀
                        if not content.startswith('【'):
                            content = f"【{date_str}涨停分析】{content}"
                        
                        browser.close()
                        return {
                            'success': True,
                            'date': date_str,
                            'content': content
                        }
                    else:
                        logger.error("未能提取文章内容")
                        # 保存页面截图用于调试
                        page.screenshot(path='article_page.png')
                        logger.info("已保存页面截图：article_page.png")
                else:
                    logger.error("未找到文章链接")
            else:
                logger.warning(f"页面中未找到'{keyword}'")
                # 保存搜索页截图
                page.screenshot(path='search_page.png')
                logger.info("已保存搜索页截图：search_page.png")
            
            browser.close()
            return {
                'success': False,
                'date': date_str,
                'content': f'未找到{date_str}的涨停分析'
            }
            
        except Exception as e:
            logger.error(f"运行出错：{e}")
            import traceback
            logger.error(traceback.format_exc())
            browser.close()
            return {
                'success': False,
                'date': date_str,
                'content': f'获取失败：{str(e)}'
            }


def main():
    """主函数"""
    # 搜索今年的2月5日涨停分析
    result = search_cls_zhangting(target_month=2, target_day=5)
    
    print("\n" + "="*50)
    print(f"搜索结果：{'成功' if result['success'] else '失败'}")
    print("="*50)
    print(f"\n内容：\n{result['content']}")
    
    return result


if __name__ == '__main__':
    main()
