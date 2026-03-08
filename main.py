import os
import requests
import datetime
import re
import sys
from urllib.parse import quote
from playwright.sync_api import sync_playwright

# 配置信息
TG_TOKEN = os.getenv('TG_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')
DEBUG_DATE = os.getenv('DEBUG_DATE')

def send_tg_msg(text):
    if not TG_TOKEN or not TG_CHAT_ID:
        print("❌ 错误: 未配置 TG_TOKEN 或 TG_CHAT_ID")
        return
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": TG_CHAT_ID, "text": text}, timeout=10)
    except Exception as e:
        print(f"发送消息失败: {e}")

def get_target_date():
    if DEBUG_DATE and DEBUG_DATE.strip():
        return DEBUG_DATE.strip()
    return (datetime.datetime.now() + datetime.timedelta(hours=8)).strftime('%Y-%m-%d')

# --- 方案 A: 财联社 API 拦截 ---
def scrape_cls_direct(date_keyword):
    print(f"🚀 [方案 A] 尝试直接访问财联社 (关键词: {date_keyword})...")
    target_text = ""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()

        def handle_response(response):
            nonlocal target_text
            if "telegraph" in response.url and response.status == 200:
                try:
                    for item in response.json().get('data', {}).get('roll_data', []):
                        content = item.get('content', '')
                        if "全市场共" in content and date_keyword in content:
                            target_text = content
                except: pass

        page.on("response", handle_response)
        page.goto("https://www.cls.cn/telegraph", wait_until="networkidle", timeout=45000)
        
        if not target_text:
            for _ in range(8):
                page.mouse.wheel(0, 3000)
                page.wait_for_timeout(1000)
                if target_text: break
        browser.close()
    return target_text

# --- 方案 B: 百度搜索回退 ---
def scrape_via_search(date_keyword):
    print(f"🔍 [方案 B] 方案 A 失败，启动百度搜索回退...")
    query = f'site:cls.cn "今日全市场共" "涨停" "{date_keyword}"'
    url = f"https://www.baidu.com/s?wd={quote(query)}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        # 匹配包含核心信息的快照文本
        match = re.search(r"今日全市场共.*?焦点股方面.*?(?=\s|…|\"|&|$)", resp.text, re.S)
        if match:
            print("✅ 从百度搜索中成功提取数据！")
            return match.group(0)
    except Exception as e:
        print(f"百度搜索抓取异常: {e}")
    return ""

def parse_and_format(raw_text, date_keyword):
    # 清理 HTML 标签（针对搜索结果）
    raw_text = re.sub(r'<.*?>', '', raw_text)
    try:
        zt = re.search(r"共\s*(\d+)\s*股涨停", raw_text).group(1)
        lb = re.search(r"连板股总数\s*(\d+)\s*只", raw_text).group(1)
        fail = re.search(r"(\d+)\s*股封板未遂", raw_text).group(1)
        rate = re.search(r"封板率为\s*(\d+%)", raw_text).group(1)
        # 焦点股正则：匹配到句号或末尾
        focus = re.search(r"焦点股方面，(.*?)(?:。|$)", raw_text, re.S).group(1).strip()
        
        return (f"📊 财联社盘后分析 ({date_keyword})\n\n"
                f"✅ 涨停总数：{zt}\n"
                f"🔗 连板总数：{lb}\n"
                f"❌ 封板未遂：{fail}\n"
                f"📈 封板率：{rate}\n\n"
                f"🔥 焦点股：\n{focus}\n\n"
                f"💡 数据来源：{'直接抓取' if 'A' in current_mode else '搜索引擎备份'}")
    except Exception as e:
        raise Exception(f"解析失败: {e}\n原文: {raw_text[:60]}...")

if __name__ == "__main__":
    dt_str = get_target_date()
    dt_obj = datetime.datetime.strptime(dt_str, '%Y-%m-%d')
    date_key = f"{dt_obj.month}月{dt_obj.day}日"
    
    current_mode = "方案 A"
    try:
        # 1. 尝试方案 A
        final_text = scrape_cls_direct(date_key)
        
        # 2. 如果 A 失败，尝试方案 B
        if not final_text:
            current_mode = "方案 B"
            final_text = scrape_via_search(date_key)
            
        if not final_text:
            raise Exception("所有抓取方案均未找到数据")
            
        # 3. 解析并发送
        report = parse_and_format(final_text, date_key)
        send_tg_msg(report)
        print("🎉 任务圆满完成！")
        
    except Exception as e:
        err_msg = f"❌ 最终抓取失败: {str(e)}"
        print(err_msg)
        send_tg_msg(err_msg)
        sys.exit(1)
