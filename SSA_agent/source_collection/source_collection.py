import requests
import json
import os
import trafilatura
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
def join_watchlist(name):
    terms = WATCHLISTS.get(name, [])
    return ' OR '.join(sorted(set(terms)))

def serper_search(watchlist):
    url = "https://google.serper.dev/search"
    news = []
    for i in range(3):
        payload = json.dumps({
        "q": f"Space articles about: {join_watchlist(watchlist)}",
        "start": i*10,
        "num":10,
        "type": "news"
        })
        headers = {
        'X-API-KEY': API_KEY,
        'Content-Type': 'application/json'
        }
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            data = response.json()
            news = news + data.get("news")
        except Exception as e:
            return(e)
    return news

def main():
    sources_database = []
    with open("/home/peter-marriott/SSA_Capstone_fairLLM/SSA_agent/source_collection/sources.json", "r") as fp:
        sources_database = json.load(fp)
    
    for list in WATCHLISTS:
        print(f"Gathering sources about {list}")
        sources = serper_search(list)
        for source in sources:
            source["text"] = fetch_article_text(source["link"])
            entry = {
                "title": source["title"],
                "source_name":  source["source"],
                "category": "News",
                "published": source["date"],
                "text": source["text"],
                "link": source["link"]
            }
            sources_database.append(entry)
        print(f"Current source count: {len(sources_database)}")

    with open("/home/peter-marriott/SSA_Capstone_fairLLM/SSA_agent/source_collection/sources.json", "w") as fp:
        json.dump(sources_database, fp)
    
if __name__ == "__main__":
    main()