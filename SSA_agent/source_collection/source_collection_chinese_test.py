import requests
import json
import os
import trafilatura
import sqlite3
from datetime import *; from dateutil.relativedelta import *
import re

# load environment variables from .env
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("SERPER_API_KEY")

def fetch_article_text(url: str, timeout: int = 15):
    text = ''
    # Try trafilatura first
    if trafilatura is not None:
        try:
            downloaded = trafilatura.fetch_url(url, timeout=timeout)
            if downloaded:
                text = trafilatura.extract(downloaded) or ''
        except Exception as e:
            print(e)
            pass
    return text

WATCHLISTS = {
    'debris_en': [
        'debris', 'ASAT', 'anti-satellite', 'conjunction', 'fragmentation', 'ODQN', 'IADC', 'mitigation', 'reentry', 'post-mission disposal'
    ],
    'debris_zh_cn': [   #simplified chinese
        '太空碎片', '反卫星', '反卫星武器', '交会', '碎片化', '轨道碎片环境', '机构间太空碎片协调委员会', '减缓', '再入大气层', '任务后处置'
    ],
    'debris_zh_tw': [   #traditional chinese
        '太空碎片', '反衛星', '反衛星武器', '交會', '碎片化', '軌道碎片環境', '機構間太空碎片協調委員會', '減緩', '再入大氣層', '任務後處置'
    ],
    'spectrum_policy_en': [
        'spectrum', 'licensing', 'ITU', 'WRC', 'Article 22', 'NTIA', 'ITU-R', 'Ka-band', 'Ku-band', 'LEO interference', 'coordination'
    ],
    'spectrum_policy_zh_cn': [
        '频谱', '许可', '国际电信联盟', '世界无线电通信大会', '第22条', '国家电信和信息管理局', '国际电联无线电通信部门', 'Ka频段', 'Ku频段', '低轨干扰', '协调'
    ],
    'spectrum_policy_zh_tw': [
        '頻譜', '授權', '國際電信聯盟', '世界無線電通信大會', '第22條', '國家電信暨資訊管理局', '國際電聯無線電通信部門', 'Ka頻段', 'Ku頻段', '低軌干擾', '協調'
    ],
    'rpo_en': [
        'RPO', 'proximity operations', 'docking', 'grapple', 'inspection', 'rendezvous', 'on-orbit servicing', 'non-cooperative'
    ],
    'rpo_zh_cn': [
        '交会与临近操作', '临近操作', '对接', '抓取', '检查', '交会', '在轨服务', '非合作目标'
    ],
    'rpo_zh_tw': [
        '交會與臨近作業', '臨近作業', '對接', '抓取', '檢查', '交會', '在軌服務', '非合作目標'
    ],
    'ssa_stm_en': [
        'SSA', 'STM', 'tracking', 'catalog', 'space traffic', 'conjunction assessment', 'COLA', 'space situational awareness'
    ],
    'ssa_stm_zh_cn': [
        '太空态势感知', '太空交通管理', '跟踪', '目录', '太空交通', '交会评估', '碰撞避免', '太空态势感知系统'
    ],
    'ssa_stm_zh_tw': [
        '太空態勢感知', '太空交通管理', '追蹤', '目錄', '太空交通', '交會評估', '碰撞避免', '太空態勢感知系統'
    ]
}

def join_watchlist(name):
    terms = WATCHLISTS.get(name, [])
    return ' OR '.join(sorted(set(terms)))

def serper_search(watchlist):
    url = "https://google.serper.dev/search"
    news = []

    terms = f"({join_watchlist(watchlist)})"

    # determine language
    if "zh_cn" in watchlist:
        hl, gl = "zh-cn", "cn"
        base = "(太空 OR 卫星 OR 轨道)"

    elif "zh_tw" in watchlist:
        hl, gl = "zh-tw", "tw"
        base = "(太空 OR 衛星 OR 軌道)"

    else:
        hl, gl = "en", "us"
        base = "(space OR satellite OR orbit)"

    for i in range(6):
        payload = json.dumps({
            "q": f"{base} AND {terms}",
            "start": i * 10,
            "num": 10,
            "type": "news",
            "gl": gl,
            "hl": hl
        })
        headers = {
        'X-API-KEY': API_KEY,
        'Content-Type': 'application/json'
        }
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            data = response.json()
            results = data.get("news") or []
            news.extend(results)        
        except Exception as e:
            print(f"Search error: {e}")
            continue
    return news

def parse_chinese_date(s):
    if "刚刚" in s:
        return datetime.now()

    if "分钟前" in s:
        mins = int(re.findall(r'\d+', s)[0])
        return datetime.now() - timedelta(minutes=mins)

    if "小时前" in s:
        hours = int(re.findall(r'\d+', s)[0])
        return datetime.now() - timedelta(hours=hours)

    if "天前" in s:
        days = int(re.findall(r'\d+', s)[0])
        return datetime.now() - timedelta(days=days)

    if "昨天" in s:
        return datetime.now() - timedelta(days=1)

    if "年" in s:
        return datetime.strptime(s, "%Y年%m月%d日")
    
    if "前天" in s:
        return datetime.now() - timedelta(days=2)

    if "秒前" in s:
        return datetime.now()

    if re.match(r"\d{4}-\d{2}-\d{2}", s):
        return datetime.strptime(s[:10], "%Y-%m-%d")

    return None

def date_offset(offset_str):
    # try Chinese first
    cn_date = parse_chinese_date(offset_str)
    if cn_date:
        return str(cn_date)
    tokens = (offset_str or "").split()
    if len(tokens) < 2:
        return str(datetime.now())
    # check if date is already correctly formatted
    try:
        gap = -int(tokens[0])
    except:
        return str(datetime.now())
            
    Today = datetime.now()
    gap = -int(tokens[0])
    if(tokens[1] in ["month", "months"]):
        delta = relativedelta(months=gap)
    if(tokens[1] in ["hour", "hours"]):
        delta = relativedelta(hours=gap)
    if(tokens[1] in ["week", "weeks"]):
        delta = relativedelta(weeks=gap)
    if(tokens[1] in ["day", "days"]):
        delta = relativedelta(days=gap)

    source_date = Today + delta
    return str(source_date)


def main():
    
    connection = sqlite3.connect("SSA_agent/concept_db/chinese_test.db")
    connection.execute("PRAGMA foreign_keys = ON")
    cursor = connection.cursor()
    seen_links = set()

    for list in WATCHLISTS:
        
        print(f"Gathering sources about {list}")
        sources = serper_search(list)
    
        for source in sources:
            link = source.get("link")
            if not link or link in seen_links:
                continue

            seen_links.add(link)

            text = fetch_article_text(link)
            if not text:
                print(f"[SCRAPE FAIL] {link}")
            elif len(text) < 300:
                print(f"[SHORT TEXT] {link}")

            raw_date = source.get("date") or ""
            if not raw_date:
                raw_date = ""

            source["date"] = date_offset(raw_date).isoformat()            
            # entry = {
            #     "title": source["title"],
            #     "source_name":  source["source"],
            #     "category": "News",
            #     "published": source["date"],
            #     "text": source["text"],
            #     "link": source["link"]
            # }
            print(f'inserting {source["title"]}')
            try:
                cursor.execute("""
                INSERT INTO sources (title, content, source, date, link) 
                VALUES (?, ?, ?, ?, ?)            
                """, (source["title"], text, source.get("source", ""), source.get("date", ""), source["link"]))
            except Exception as e:
                print(f"DB insert failed for {link}: {e}")
                connection.rollback()
        connection.commit()

    connection.commit()
    connection.close()

if __name__ == "__main__":
    main()