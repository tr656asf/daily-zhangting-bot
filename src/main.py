#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主程序：获取涨停数据并推送到Telegram
"""

import os
import sys
import logging
from datetime import datetime, timedelta

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def is_workday():
    """检查今天是否是工作日（周一到周五）"""
    weekday = datetime.now().weekday()
    return weekday < 5  # 0-4是周一到周五


def get_zt_data():
    """获取涨停数据"""
    try:
        import akshare as ak
        
        today = datetime.now().strftime('%Y%m%d')
        logger.info(f"获取 {today} 的涨停数据...")
        
        # 获取涨停股票池（东方财富数据）
        try:
            df_zt = ak.stock_zt_pool_em(date=today)
            zt_count = len(df_zt)
            logger.info(f"获取到 {zt_count} 只涨停股票")
        except Exception as e:
            logger.error(f"获取涨停数据失败：{e}")
            df_zt = None
            zt_count = 0
        
        # 获取连板股票池
        try:
            df_lb = ak.stock_zt_pool_zbgc_em(date=today)
            lb_count = len(df_lb)
            logger.info(f"获取到 {lb_count} 只连板股票")
        except Exception as e:
            logger.error(f"获取连板数据失败：{e}")
            df_lb = None
            lb_count = 0
        
        # 获取昨日涨停股今日表现（用于计算封板率等）
        try:
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
            df_yz = ak.stock_zt_pool_previous_em(date=today)
            yz_count = len(df_yz)
        except:
            yz_count = 0
        
        return {
            'zt_count': zt_count,
            'lb_count': lb_count,
            'yz_count': yz_count,
            'df_zt': df_zt,
            'df_lb': df_lb
        }
        
    except ImportError:
        logger.error("未安装 akshare，请运行：pip install akshare")
        return None
    except Exception as e:
        logger.error(f"获取数据失败：{e}")
        return None


def format_report(data):
    """格式化报告"""
    if not data:
        return "❌ 数据获取失败"
    
    today = datetime.now()
    date_str = today.strftime('%Y年%m月%d日')
    weekday_str = ['周一','周二','周三','周四','周五','周六','周日'][today.weekday()]
    
    report = f"📊 {date_str} {weekday_str} 涨停分析\n"
    report += "=" * 30 + "\n\n"
    
    # 涨停概况
    report += f"🔥 涨停概况\n"
    report += f"今日涨停股票：{data['zt_count']}只\n"
    report += f"连板股票：{data['lb_count']}只\n"
    
    # 连板天梯
    if data['df_lb'] is not None and len(data['df_lb']) > 0:
        report += f"\n📈 连板天梯（前10）\n"
        df_lb = data['df_lb'].head(10)
        for idx, row in df_lb.iterrows():
            name = row.get('名称', row.get('股票简称', '未知'))
            code = row.get('代码', row.get('股票代码', ''))
            lb_days = row.get('连板天数', row.get('连续涨停天数', 1))
            report += f"{lb_days}连板：{name}({code})\n"
    
    # 涨停个股列表（如果有）
    if data['df_zt'] is not None and len(data['df_zt']) > 0:
        report += f"\n💡 今日涨停股票（前15）\n"
        df_zt = data['df_zt'].head(15)
        stocks = []
        for idx, row in df_zt.iterrows():
            name = row.get('名称', row.get('股票简称', '未知'))
            stocks.append(name)
        report += "、".join(stocks) + "\n"
    
    return report


def send_to_telegram(message):
    """发送到Telegram"""
    try:
        import asyncio
        from telegram import Bot
        
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not token or not chat_id:
            logger.error("未配置 TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHAT_ID")
            return False
        
        bot = Bot(token=token)
        
        async def send():
            await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='HTML'
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
    logger.info("AkShare 每日涨停数据推送")
    logger.info("=" * 50)
    
    # 检查是否是工作日
    if not is_workday():
        logger.info("今天是周末，不运行")
        return True
    
    # 获取数据
    logger.info("开始获取数据...")
    data = get_zt_data()
    
    if not data:
        logger.error("数据获取失败")
        return False
    
    # 格式化报告
    report = format_report(data)
    logger.info(f"报告内容：\n{report}")
    
    # 发送推送
    logger.info("发送到 Telegram...")
    success = send_to_telegram(report)
    
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
