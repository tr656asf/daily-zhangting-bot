import os

# 从 GitHub Secrets 读取
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 测试打印
print("TOKEN:", TELEGRAM_TOKEN)
print("CHAT_ID:", TELEGRAM_CHAT_ID)
