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
    keyword = f"{date_str}涨停分析"
    # 尝试使用财联社另一个更稳定的 API 路径
    api_url = f"https://www.cls.cn/nodeapi/search?keyword={keyword}&type=telegraph&rn=1&os=web"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Content-Type": "application/json",
        "Referer": "https://www.cls.cn/searchPage",
        "Origin": "https://www.cls.cn"
    }

    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        
        # 核心调试步骤：如果状态码不是 200，说明被拦截了
        if response.status_code != 200:
            return f"请求被拦截！状态码: {response.status_code}。可能是 GitHub IP 被封锁。"

        # 检查返回内容是否为空
        if not response.text.strip():
            return f"服务器返回内容为空，可能该时段没有数据。"

        # 尝试解析 JSON
        try:
            data = response.json()
        except Exception:
            # 如果解析失败，打印前 100 个字符看看对方返回了什么（通常是 HTML 报错页）
            return f"解析 JSON 失败。返回内容预览: {response.text[:100]}"
        
        telegraph_list = data.get('data', {}).get('telegraph', {}).get('list', [])
        
        if telegraph_list:
            content = telegraph_list[0].get('content', '')
            clean_content = BeautifulSoup(content, "html.parser").get_text()
            return f"【财联社 {date_str} 涨停分析】\n\n{clean_content}"
        else:
            return f"未找到 {date_str} 的内容。搜索接口返回列表为空。"
            
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
