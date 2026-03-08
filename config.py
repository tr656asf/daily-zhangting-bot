import os

# 读取 GitHub Secrets 或本地环境变量
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 测试打印，确保能读取到
print("TOKEN:", TELEGRAM_TOKEN)
print("CHAT_ID:", TELEGRAM_CHAT_ID)
