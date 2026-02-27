#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主程序：百度搜索财联社涨停分析并推送到Telegram
"""

import os
import sys
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def is_workday():
    """检查今天是否是工作日（周一到周五）"""
    weekday = datetime.now().weekday()
    return weekday < 5


def send_to_telegram(content):
    """发送到Telegram"""
    try:
        import asyncio
        from telegram import Bot
        
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not token or not chat_id:
            logger.error("未配置 TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHAT_ID")
            return False
        
        # 直接发送原文，不做额外格式化
        bot = Bot(token=token)
        
        async def send():
            await bot.send_message(
                chat_id=chat_id,
                text=content,
                parse_mode=None  # 不解析markdown/html，原样发送
            )
        
        asyncio.run(send())
        logger.info("消息发送成功")
        return True
        
    except Exception as e:
        logger.error(f"发送失败：{e}")
        return False


def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("财联社涨停分析推送")
    logger.info("=" * 50)
    
    # 检查是否是工作日
    if not is_workday():
        logger.info("今天是周末，不运行")
        return True
    
    # 导入scraper
    sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
    from scraper import WebScraper
    
    # 获取数据
    logger.info("开始获取涨停分析...")
    scraper = WebScraper()
    result = scraper.fetch_zhangting_analysis()
    
    content = result['items'][0] if result['items'] else '无内容'
    
    logger.info(f"获取到的内容：{content[:200]}...")
    
    # 发送到Telegram
    logger.info("发送到 Telegram...")
    success = send_to_telegram(content)
    
    if success:
        logger.info("完成！")
    else:
        logger.error("发送失败")
    
    return success


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.exception("程序出错")
        sys.exit(1)
