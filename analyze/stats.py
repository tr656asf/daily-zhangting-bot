def analyze_stats(limit_up, fail_pool):
    total_limit_up = len(limit_up)
    fail_count = len(fail_pool)
    lianban = [s for s in limit_up if s.get("days", 1) >= 2]
    lianban_count = len(lianban)
    highest = max([s.get("days", 1) for s in limit_up], default=1)
    success_rate = round(total_limit_up / (total_limit_up + fail_count) * 100, 2) if (total_limit_up + fail_count) > 0 else 0
    return {
        "limit_up_total": total_limit_up,
        "fail_count": fail_count,
        "success_rate": success_rate,
        "lianban_count": lianban_count,
        "highest_board": highest
    }
