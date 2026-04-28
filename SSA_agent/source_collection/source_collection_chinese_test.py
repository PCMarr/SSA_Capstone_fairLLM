import requests
import json
import os
import trafilatura
import sqlite3
from datetime import *; from dateutil.relativedelta import *

# load environment variables from .env
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("SERPER_API_KEY")

def fetch_article_text(url: str, timeout: int = 15):
    text = ''
    # Try trafilatura first
    if trafilatura is not None:
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                text = trafilatura.extract(downloaded) or ''
        except Exception as e:
            print(e)
            pass
    return text

WATCHLISTS = {
    'debris': [
        'debris', 'ASAT', 'anti-satellite', 'conjunction', 'fragmentation', 'ODQN', 'IADC', 'mitigation', 'reentry', 'post-mission disposal'
    ],
    'spectrum_policy': [
        'spectrum', 'licensing', 'ITU', 'WRC', 'Article 22', 'NTIA', 'ITU-R', 'Ka-band', 'Ku-band', 'LEO interference', 'coordination'
    ],
    'rpo': [
        'RPO', 'proximity operations', 'docking', 'grapple', 'inspection', 'rendezvous', 'on-orbit servicing', 'non-cooperative'
    ],
    'ssa_stm': [
        'SSA', 'STM', 'tracking', 'catalog', 'space traffic', 'conjunction assessment', 'COLA', 'space situational awareness'
    ],
}

WATCHLISTS_ZH = {
    'debris': [
        '太空碎片', '反卫星', '反卫星武器', '碰撞预警', '碎片化', '再入', '轨道碎片缓解'
    ],
    'spectrum_policy': [
        '频谱', '许可', '国际电信联盟', 'WRC大会', 'Ka波段', 'Ku波段', '干扰', '协调'
    ],
    'rpo': [
        '交会对接', '在轨服务', '接近操作', '空间对接', '非合作目标', '检查'
    ],
    'ssa_stm': [
        '空间态势感知', '空间交通管理', '跟踪', '编目', '碰撞评估'
    ],
}

WATCHLISTS_ZH_TW = {
    'debris': [
        '太空碎片', '反衛星', '碰撞預警', '再入', '軌道碎片緩解'
    ],
    'spectrum_policy': [
        '頻譜', '許可', '國際電信聯盟', '干擾', '協調'
    ],
    'rpo': [
        '交會對接', '在軌服務', '接近操作', '檢查'
    ],
    'ssa_stm': [
        '空間態勢感知', '空間交通管理', '跟蹤', '編目'
    ],
}

def join_watchlist(name, lang="en"):
    if lang == "zh":
        terms = WATCHLISTS_ZH.get(name, [])
    elif lang == "zh-tw":
        terms = WATCHLISTS_ZH_TW.get(name, [])
    else:
        terms = WATCHLISTS.get(name, [])
    
    return ' OR '.join(sorted(set(terms)))

def serper_search(watchlist, lang="en"):
    url = "https://google.serper.dev/search"
    news = []

    query = join_watchlist(watchlist, lang)

    for i in range(6):
        if (lang == "zh"):
            payload = json.dumps({
                "q": query,
                "start": i * 10,
                "num": 10,
                "type": "news",
                "hl": "zh-cn",
                "gl": "cn"
            })
        elif (lang == "zh-tw"):
            payload = json.dumps({
                "q": query,
                "start": i * 10,
                "num": 10,
                "type": "news",
                "hl": "zh-tw",
                "gl": "tw"
            })
        else:
            payload = json.dumps({
                "q": query,
                "start": i * 10,
                "num": 10,
                "type": "news",
                "hl": "en",
            })

        headers = {
            'X-API-KEY': API_KEY,
            'Content-Type': 'application/json'
        }

        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            data = response.json()
            news += data.get("news", [])
        except Exception as e:
            print(f"Serper error ({lang}): {e}")
            continue

        import time
        time.sleep(0.5)

    return news

def date_offset(offset_str):
    tokens = offset_str.split(" ")
    # check if date is already correctly formatted
    if(tokens[-1] != "ago"):
        source_date = datetime.strptime(offset_str, "%b %d, %Y")
        return str(source_date)
    
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
    

    for list in WATCHLISTS:
        connection = sqlite3.connect("SSA_agent/concept_db/pair.db")
        connection.execute("PRAGMA foreign_keys = ON")
        cursor = connection.cursor()

        print(f"Gathering sources about {list}")

        print("  -> English")
        sources_en = serper_search(list, lang="en") or []

        print("  -> Simplified Chinese")
        sources_zh = serper_search(list, lang="zh") or []
        print(len(sources_zh))

        print("  -> Traditional Chinese")
        sources_tw = serper_search(list, lang="zh-tw") or []
        print(len(sources_tw))

        sources = sources_en + sources_zh + sources_tw
        for source in sources:
            source["text"] = fetch_article_text(source["link"])
            source["date"] = date_offset(source["date"])
            source["language_code"] = "zh" if any('\u4e00' <= c <= '\u9fff' for c in source["title"]) else "en"
            # entry = {
            #     "title": source["title"],
            #     "source_name":  source["source"],
            #     "category": "News",
            #     "published": source["date"],
            #     "text": source["text"],
            #     "link": source["link"]
            # }
            print(f"inserting {source["title"]}")
            try:
                cursor.execute("""
                INSERT INTO sources (title, content, source, date, link, language_code) 
                VALUES (?, ?, ?, ?, ?)            
                """, (source["title"], source["text"], source["source"], source["date"], source["link"], source["language_code"]))
                connection.commit()
            except:
                pass

        connection.close()

if __name__ == "__main__":
    main()