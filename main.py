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
    # 1. 构造关键词
    keyword = f"{date_str}涨停分析"
    
    # 2. 直接请求财联社的搜索接口 (这是他们后台真正的地址)
    # rn=1 表示我们只需要第一条结果
    api_url = f"https://www.cls.cn/nodeapi/search?keyword={keyword}&type=telegraph&rn=1&os=web"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.cls.cn/searchPage"
    }

    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        data = response.json() # 直接解析成 JSON 字典
        
        # 3. 提取内容 (顺着数据层级往下找)
        # 财联社的接口返回结构是 data -> telegraph -> list -> [0] -> content
        telegraph_list = data.get('data', {}).get('telegraph', {}).get('list', [])
        
        if telegraph_list:
            content = telegraph_list[0].get('content', '')
            # 清理一下 HTML 标签（如果有的话）
            clean_content = BeautifulSoup(content, "html.parser").get_text()
            return f"【财联社 {date_str} 涨停分析】\n\n{clean_content}"
        else:
            return f"未能找到 {date_str} 的涨停分析内容。原因：当天可能尚未发布或关键词无结果。"
            
    except Exception as e:
        return f"接口请求出错: {str(e)}"

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
