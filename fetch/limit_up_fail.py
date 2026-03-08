import requests, datetime

def get_today():
    return datetime.datetime.now().strftime("%Y%m%d")

def fetch_fail_pool(date=None):
    if date is None:
        date = get_today()
    url = "https://push2ex.eastmoney.com/getTopicZTPool"
    params = {
        "ut": "7eea3edcaed734bea9cbfc24409ed989",
        "dpt": "wz.ztzt",
        "Pageindex": "1",
        "pagesize": "200",
        "sort": "fbt:desc",
        "date": date
    }
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, params=params, headers=headers)
    data = r.json()
    stocks = data.get("data", {}).get("pool", [])
    return stocks
