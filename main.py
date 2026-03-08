from fetch.limit_up_pool import fetch_limit_up
from fetch.limit_up_fail import fetch_fail_pool

from analyze.stats import analyze_stats
from analyze.focus import get_focus_stocks
from analyze.sector import get_hot_sectors

from report.generate_report import generate_report

from notify.telegram_bot import TelegramBot

import config

import config

from notify.telegram_bot import TelegramBot
import config

# 测试 Telegram 推送
bot = TelegramBot(config.TELEGRAM_TOKEN, config.TELEGRAM_CHAT_ID)
bot.send_message("GitHub 测试消息")

print("TOKEN:", config.TELEGRAM_TOKEN)
print("CHAT_ID:", config.TELEGRAM_CHAT_ID)

bot = TelegramBot(
    config.TELEGRAM_TOKEN,
    config.TELEGRAM_CHAT_ID
)

bot.send_message("测试消息：GitHub运行成功")

def push_report(report):

    bot = TelegramBot(
        config.TELEGRAM_TOKEN,
        config.TELEGRAM_CHAT_ID
    )

    bot.send_message(report)


def main():

    limit_up = fetch_limit_up()

    fail_pool = fetch_fail_pool()

    stats = analyze_stats(limit_up, fail_pool)

    focus = get_focus_stocks(limit_up)

    sectors = get_hot_sectors(limit_up)

    report = generate_report(stats, focus, sectors)

    print(report)

    push_report(report)


if __name__ == "__main__":

    main()
