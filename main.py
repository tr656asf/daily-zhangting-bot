import os
import requests
import datetime
import pytz
from bs4 import BeautifulSoup

def get_beijing_date():
    # 1. 确定北京时间
    tz = pytz.timezone('Asia/Shanghai')
    now = datetime.datetime.now(tz)
    return f"{now.month}月{now.day}日"

def fetch_cls_data(date_str):
    # 2. 构建网址 (注意对关键词进行 URL 编码)
    keyword = f"{date_str}涨停分析"
    url = f"https://www.cls.cn/searchPage?keyword={keyword}&type=all" # 修正type为all获取更多结果
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.cls.cn/"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 3. 爬取目标 div
        # 财联社搜索页是动态渲染的，如果通过 HTML 无法直接抓取，通常需要寻找其 API 接口
        # 这里尝试直接定位你要求的 class
        target_div = soup.find('div', class_='search-telegraph-list')
        if target_div:
            return target_div.get_text(strip=True, separator='\n')
        else:
            return f"未能找到 {date_str} 的涨停分析内容，请检查网页结构或关键词。"
    except Exception as e:
        return f"爬取过程中出错: {str(e)}"

def send_telegram(text):
    # 4. 通过 Telegram 机器人发送
    token = os.environ.get('TG_TOKEN')
    chat_id = os.environ.get('TG_CHAT_ID')
    
    if not token or not chat_id:
        print("未配置 Telegram Token 或 Chat ID")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text[:4000] # TG 单条消息长度限制
    }
    requests.post(url, data=data)

if __name__ == "__main__":
    date_var = get_beijing_date()
    print(f"正在处理日期: {date_var}")
    content = fetch_cls_data(date_var)
    send_telegram(content)
