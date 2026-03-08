import requests
import datetime


def get_today():
    return datetime.datetime.now().strftime("%Y%m%d")


def fetch_limit_up(date=None):

    if date is None:
        date = get_today()

    url = "https://push2ex.eastmoney.com/getTopicZTPool"

    params = {
        "ut": "7eea3edcaed734bea9cbfc24409ed989",
        "dpt": "wz.ztzt",
        "Pageindex": "0",
        "pagesize": "200",
        "sort": "fbt:desc",
        "date": date
    }

    r = requests.get(url, params=params)

    data = r.json()

    stocks = data["data"]["pool"]

    return stocks
