
import pandas as pd
import feedparser
import re
from datetime import datetime, timedelta
from urllib.parse import urlparse
import math, time, html, json

try:
    import trafilatura
except Exception as e:
    trafilatura = None
try:
    from newspaper import Article
except Exception:
    Article = None



SOURCES = [
    # --- Space Agencies / Official News ---
    {"name": "NASA Breaking News", "domain": "nasa.gov", "category": "News", "rss": "https://www.nasa.gov/rss/dyn/breaking_news.rss"},
    {"name": "ESA Newsroom", "domain": "esa.int", "category": "News", "rss": "https://www.esa.int/rssfeed/Our_Activities"},
    {"name": "ESA Space Safety (Blog)", "domain": "esa.int", "category": "Policy/SSA", "rss": "https://www.esa.int/feeds/ESA_Space_Safety_Blog"},
    {"name": "JAXA Global Press", "domain": "jaxa.jp", "category": "News", "rss": "https://global.jaxa.jp/rss/rss.xml"},
    {"name": "UK Space Agency", "domain": "gov.uk", "category": "Policy/News", "rss": "https://www.gov.uk/government/organisations/uk-space-agency.atom"},
    {"name": "CNES News", "domain": "cnes.fr", "category": "News", "rss": "https://cnes.fr/en/rss.xml"},
    {"name": "DLR News", "domain": "dlr.de", "category": "News", "rss": "https://www.dlr.de/SiteTools/Functions/RSSFeeds/EN/RSSNewsFeed.xml"},
    {"name": "ASI News", "domain": "asi.it", "category": "News", "rss": "https://www.asi.it/en/feed/"},

    # --- Region-specific (CNSA/ISRO/Roscosmos/UNOOSA, commercial China) ---
    {"name": "CNSA (mirror/English)", "domain": "cnsa.gov.cn", "category": "News", "rss": "https://www.cnsa.gov.cn/english/rss.xml"},
    {"name": "ISRO Updates", "domain": "isro.gov.in", "category": "News", "rss": "https://www.isro.gov.in/rss.xml"},
    {"name": "Roscosmos News", "domain": "roscosmos.ru", "category": "News", "rss": "https://www.roscosmos.ru/rss/en/"},
    {"name": "UNOOSA News", "domain": "unoosa.org", "category": "Policy/UN", "rss": "https://www.unoosa.org/oosa/rss.xml"},
    {"name": "CASC Press Releases", "domain": "spacechina.com", "category": "Industry", "rss": "https://www.spacechina.com/n25/n144/n2066/index.html"},
    {"name": "CASIC News", "domain": "casic.com.cn", "category": "Industry", "rss": "https://www.casic.com.cn/rss.xml"},

    # --- Regulation / Spectrum / STM ---
    {"name": "FCC News Releases", "domain": "fcc.gov", "category": "Regulation", "rss": "https://www.fcc.gov/news-events/rss/releases.xml"},
    {"name": "FAA Newsroom (AST)", "domain": "faa.gov", "category": "Regulation", "rss": "https://www.faa.gov/newsroom/rss.xml"},
    {"name": "ITU News", "domain": "itu.int", "category": "Spectrum/Policy", "rss": "https://news.itu.int/feed/"},
    {"name": "NTIA News", "domain": "ntia.doc.gov", "category": "Spectrum/Policy", "rss": "https://www.ntia.gov/rss"},
    {"name": "Ofcom Features & News", "domain": "ofcom.org.uk", "category": "Spectrum/Policy", "rss": "https://www.ofcom.org.uk/about-ofcom/latest/features-and-news/rss"},

    # --- Defense / Military Official ---
    {"name": "US Space Force News", "domain": "spaceforce.mil", "category": "Defense", "rss": "https://www.spaceforce.mil/DesktopModules/ArticleCS/RSS.ashx?ContentType=1&Site=106&max=50"},
    {"name": "US Space Command News", "domain": "spacecom.mil", "category": "Defense", "rss": "https://www.spacecom.mil/DesktopModules/ArticleCS/RSS.ashx?ContentType=1&Site=323&max=50"},

    # --- Think Tanks / NGOs / Research ---
    {"name": "Secure World Foundation", "domain": "swfound.org", "category": "Policy/NGO", "rss": "https://swfound.org/news/rss/"},
    {"name": "CSIS Aerospace Security", "domain": "csis.org", "category": "Policy/Research", "rss": "https://www.csis.org/rss.xml"},
    {"name": "Aerospace Corporation", "domain": "aerospace.org", "category": "Policy/Research", "rss": "https://aerospace.org/rss.xml"},
    {"name": "European Space Policy Institute (ESPI)", "domain": "espi.or.at", "category": "Policy/Research", "rss": "https://www.espi.or.at/feed/"},

    # --- Independent/Trade News & Analysis ---
    {"name": "SpaceNews", "domain": "spacenews.com", "category": "News", "rss": "https://spacenews.com/feed/"},
    {"name": "SpacePolicyOnline", "domain": "spacepolicyonline.com", "category": "Policy/News", "rss": "https://spacepolicyonline.com/feed/"},
    {"name": "SpaceWatch.Global", "domain": "spacewatch.global", "category": "News", "rss": "https://spacewatch.global/feed/"},
    {"name": "The Space Review", "domain": "thespacereview.com", "category": "Analysis/Opinion", "rss": "http://www.thespacereview.com/rss.xml"},

    # --- Commercial SDA / STM (blogs) ---
    {"name": "LeoLabs Blog", "domain": "leolabs.space", "category": "SSA/STM", "rss": "https://blog.leolabs.space/rss/"},
]
sources_df = pd.DataFrame(SOURCES)

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

import math, time, html

def clean_text(t: str) -> str:
    if not t:
        return ''
    t = html.unescape(t)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def fetch_feed(feed_url: str, limit: int = 50):
    try:
        fp = feedparser.parse(feed_url)
        entries = []
        for e in fp.entries[:limit]:
            title = clean_text(getattr(e, 'title', ''))
            link = getattr(e, 'link', '')
            summary = clean_text(getattr(e, 'summary', ''))
            published = None
            if getattr(e, 'published_parsed', None):
                published = datetime(*e.published_parsed[:6])
            elif getattr(e, 'updated_parsed', None):
                published = datetime(*e.updated_parsed[:6])
            entries.append({
                'title': title,
                'link': link,
                'summary': summary,
                'published': published,
                'source': urlparse(feed_url).netloc,
                'feed': feed_url,
            })
        return entries
    except Exception as ex:
        print('Feed error:', feed_url, ex)
        return []

def fetch_article_text(url: str, timeout: int = 15):
    text = ''
    # Try trafilatura first
    if trafilatura is not None:
        try:
            downloaded = trafilatura.fetch_url(url, timeout=timeout)
            if downloaded:
                text = trafilatura.extract(downloaded) or ''
        except Exception:
            pass
    # Fallback to newspaper3k
    if not text and Article is not None:
        try:
            art = Article(url)
            art.download()
            art.parse()
            text = art.text or ''
        except Exception:
            pass
    return clean_text(text)

def summarize_text(text: str, query_terms=None, max_sentences=4):
    if not text:
        return ''
    sents = re.split(r'(?<=[.!?])\s+', text)
    if not sents:
        return text[:400] + '...'
    query_terms = [t.lower() for t in (query_terms or []) if t.strip()]
    scores = []
    for i, s in enumerate(sents):
        length_score = min(len(s) / 200, 1.0)
        term_score = sum(s.lower().count(q) for q in query_terms)
        scores.append((length_score + term_score, i, s))
    scores.sort(reverse=True)
    chosen = [s for _, _, s in scores[:max_sentences]]
    chosen.sort(key=lambda x: sents.index(x))
    return ' '.join(chosen)

DEFAULT_LIMIT = 30
def harvest(sources_table, include_categories=None, limit=DEFAULT_LIMIT, days_back=30):
    include_categories = set(include_categories or [])
    rows = []
    cutoff = datetime.now() - timedelta(days=days_back)
    for _, row in sources_table.iterrows():
        if include_categories and row['category'] not in include_categories:
            continue
        entries = fetch_feed(row['rss'], limit=limit)
        for e in entries:
            if e['published'] and e['published'] < cutoff:
                continue
            e['source_name'] = row['name']
            e['category'] = row['category']
            rows.append(e)
    if not rows:
        return pd.DataFrame(columns=['published','title','source_name','category','summary','link','feed'])
    df = pd.DataFrame(rows)
    df = df.sort_values(by=['published'], ascending=False, na_position='last').reset_index(drop=True)
    return df


if __name__ == "__main__":
    #sources_df = harvest(sources_df, include_categories={'Policy/Research'})
    feed = fetch_feed("https://www.nasa.gov/rss/dyn/breaking_news.rss")
    for x in feed:
        x["published"] = "xxx"

    # feed_text = json.dumps(feed, indent=2)
    # print(feed_text)
    text = ""
    try:
        downloaded = trafilatura.fetch_url("https://www.nasa.gov/science-research/earth-science/sarp-east-2025-terrestrial-fluxes-group/")
        if downloaded:
            text = trafilatura.extract(downloaded) or ''
    except Exception:
        print("trafilatura failed")
    print(text)