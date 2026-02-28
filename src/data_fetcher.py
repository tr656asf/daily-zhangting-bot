#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据获取模块 - 使用AkShare获取涨停数据
"""

import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_zt_data():
    """
    获取涨停数据（使用AkShare）
    返回格式化的涨停分析报告
    """
    try:
        import akshare as ak
        
        today = datetime.now()
        date_str = today.strftime('%Y%m%d')
        date_display = today.strftime('%Y年%m月%d日')
        weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][today.weekday()]
        
        logger.info(f"获取 {date_display} 的涨停数据...")
        
        # 1. 获取涨停股票池
        try:
            df_zt = ak.stock_zt_pool_em(date=date_str)
            zt_count = len(df_zt)
            logger.info(f"涨停股票：{zt_count}只")
        except Exception as e:
            logger.error(f"获取涨停池失败：{e}")
            zt_count = 0
            df_zt = None
        
        # 2. 获取连板数据
        try:
            df_lb = ak.stock_zt_pool_zbgc_em(date=date_str)
            lb_count = len(df_lb)
            logger.info(f"连板股票：{lb_count}只")
        except Exception as e:
            logger.error(f"获取连板数据失败：{e}")
            lb_count = 0
            df_lb = None
        
        # 3. 构建报告内容（仿财联社格式）
        content = f"【{today.month}月{today.day}日涨停分析】AkShare{today.month}月{today.day}日电，"
        
        if df_zt is not None and len(df_zt) > 0:
            content += f"今日全市场共{zt_count}股涨停"
            
            if df_lb is not None and len(df_lb) > 0:
                content += f"，连板股总数{lb_count}只"
                
                # 获取最高连板数
                max_lb = df_lb['连板数'].max() if '连板数' in df_lb.columns else 1
                content += f"，最高{int(max_lb)}连板"
            
            content += "。"
            
            # 添加焦点股信息（前5名连板股）
            if df_lb is not None and len(df_lb) > 0:
                content += "焦点股方面，"
                
                # 按连板数排序，取前5
                if '连板数' in df_lb.columns:
                    df_top = df_lb.nlargest(5, '连板数')
                else:
                    df_top = df_lb.head(5)
                
                focus_stocks = []
                for idx, row in df_top.iterrows():
                    name = row.get('名称', row.get('股票简称', '未知'))
                    lb = row.get('连板数', 1)
                    if int(lb) >= 2:  # 只显示2连板以上
                        focus_stocks.append(f"{name}{int(lb)}连板")
                
                if focus_stocks:
                    content += "、".join(focus_stocks) + "。"
        else:
            content += "今日暂无涨停数据。"
        
        logger.info(f"报告生成完成，长度：{len(content)}")
        
        return {
            'source': f'涨停分析（{today.month}月{today.day}日）',
            'items': [content]
        }
        
    except ImportError:
        logger.error("未安装akshare")
        return {
            'source': '涨停分析',
            'items': ['数据获取失败：未安装akshare库']
        }
    except Exception as e:
        logger.error(f"获取数据失败：{e}")
        return {
            'source': '涨停分析',
            'items': [f'数据获取失败：{str(e)}']
        }


if __name__ == '__main__':
    result = get_zt_data()
    print(f"\n{result['items'][0]}")
