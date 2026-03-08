import datetime


def generate_report(stats, focus, sectors):

    today = datetime.datetime.now().strftime("%Y-%m-%d")

    text = f"""
A股短线市场情绪日报
{today}

涨停：{stats['limit_up_total']}
炸板：{stats['fail_count']}
封板率：{stats['success_rate']}%

连板：{stats['lianban_count']}
最高连板：{stats['highest_board']}

市场龙头：
"""

    for s in focus:

        name = s.get("n")
        days = s.get("days")

        text += f"{name} {days}板\n"

    text += "\n热门板块：\n"

    for s in sectors:

        text += f"{s[0]}\n"

    return text
