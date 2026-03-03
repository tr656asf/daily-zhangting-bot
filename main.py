import os
import requests
import datetime
import pytz
from bs4 import BeautifulSoup
from chinese_calendar import is_workday  # 专门处理中国节假日的库

def get_beijing_time():
    """获取北京时间"""
    tz = pytz.timezone('Asia/Shanghai')
    return datetime.datetime.now(tz)

def send_telegram(text):
    """发送 Telegram 消息"""
    token = os.environ.get('TG_TOKEN')
    chat_id = os.environ.get('TG_CHAT_ID')
    if not token or not chat_id:
        print("未配置 Telegram Token 或 Chat ID")
        return
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": text[:4000]}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"发送消息失败: {e}")

def fetch_cls_data(date_str):
    """抓取财联社数据"""
    keyword = f"{date_str}涨停分析"
    # 建议使用 searchPage 的全量接口，或者尝试直接请求 API 接口
    url = f"https://www.cls.cn/searchPage?keyword={keyword}&type=all"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.cls.cn/"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 寻找目标 div
        target_div = soup.find('div', class_='search-telegraph-list')
        if target_div:
            return target_div.get_text(strip=True, separator='\n')
        else:
            return f"未能找到 {date_str} 的涨停分析内容。"
    except Exception as e:
        return f"爬取出错: {str(e)}"

def main():
    # 1. 获取北京时间
    bj_now = get_beijing_time()
    date_str = f"{bj_now.month}月{bj_now.day}日"
    
    # 2. 判断是否为工作日 (考虑了法定节假日和调休)
    # is_workday 会自动判断周六日是否需要补班，以及周一到周五是否是过节
    if not is_workday(bj_now):
        print(f"今天 {date_str} 是节假日或周末，发送通知并退出。")
        send_telegram("今天是节假日")
        return # 结束程序

    # 3. 如果是工作日，执行爬取
    print(f"今天 {date_str} 是工作日，开始运行爬虫...")
    content = fetch_cls_data(date_str)
    send_telegram(content)

if __name__ == "__main__":
    main()
