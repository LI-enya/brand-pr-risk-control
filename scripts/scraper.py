"""Web scraper for brand mentions across multiple channels.
Uses Google Search + Yahoo Japan Search for maximum coverage.
Extracts publication dates from search result snippets.
"""

import re
import time
import random
import urllib.parse
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
]

def _headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept-Language': 'ja,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }

def _delay(base=2):
    time.sleep(base + random.random() * 2)

def _safe_get(url, timeout=15, retries=1):
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, headers=_headers(), timeout=timeout)
            resp.encoding = 'utf-8'
            if resp.status_code == 200:
                return resp.text
            if resp.status_code == 429 and attempt < retries:
                wait = 10 + random.random() * 5
                print(f"  [Scraper] 429 rate limit, waiting {wait:.0f}s...", flush=True)
                time.sleep(wait)
                continue
            print(f"  [Scraper] HTTP {resp.status_code} for {url[:80]}")
        except Exception as e:
            print(f"  [Scraper] Error: {e}")
    return None

def _now():
    return datetime.now(timezone.utc).isoformat()

def _clean_text(text):
    """Remove HTML tags from text."""
    return re.sub(r'<[^>]+>', '', text).strip()

# ====== Date extraction from text ======
DATE_PATTERNS = [
    # 2025/04/14, 2025/4/14
    (r'(\d{4})/(\d{1,2})/(\d{1,2})', lambda m: f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"),
    # 2025-04-14
    (r'(\d{4})-(\d{1,2})-(\d{1,2})', lambda m: f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"),
    # 2025年4月14日
    (r'(\d{4})年(\d{1,2})月(\d{1,2})日', lambda m: f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"),
    # Apr 14, 2025 / April 14, 2025
    (r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+(\d{1,2}),?\s+(\d{4})',
     lambda m: _parse_en_date(m)),
    # 14 Apr 2025
    (r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+(\d{4})',
     lambda m: _parse_en_date_rev(m)),
]

MONTH_MAP = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
}

def _parse_en_date(m):
    month = MONTH_MAP.get(m.group(1)[:3].lower(), 1)
    return f"{m.group(3)}-{month:02d}-{int(m.group(2)):02d}"

def _parse_en_date_rev(m):
    month = MONTH_MAP.get(m.group(2)[:3].lower(), 1)
    return f"{m.group(3)}-{month:02d}-{int(m.group(1)):02d}"

def _extract_date(text):
    """Extract the earliest plausible publication date from text."""
    if not text:
        return None
    for pattern, formatter in DATE_PATTERNS:
        match = re.search(pattern, text)
        if match:
            try:
                date_str = formatter(match)
                # Validate it's a real date and not too old
                dt = datetime.strptime(date_str, '%Y-%m-%d')
                if 2015 <= dt.year <= 2030:
                    return date_str + 'T00:00:00+09:00'
            except Exception:
                continue
    return None

def _detect_channel(url):
    """Detect which channel a URL belongs to"""
    url_lower = url.lower()
    if 'twitter.com' in url_lower or 'x.com' in url_lower:
        return 'twitter'
    if 'instagram.com' in url_lower:
        return 'instagram'
    if 'threads.net' in url_lower:
        return 'threads'
    if 'facebook.com' in url_lower:
        return 'facebook'
    if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return 'youtube'
    if 'chiebukuro.yahoo.co.jp' in url_lower:
        return 'yahoo'
    return 'google'

# ====== Google Search ======
def scrape_google(brand):
    """Search via Google (primary engine for coverage)."""
    results = []
    for keyword in brand['keywords'][:3]:
        _delay(3)
        query = urllib.parse.quote(keyword)
        url = f'https://www.google.co.jp/search?q={query}&hl=ja&num=20'
        html = _safe_get(url, retries=1)
        if not html:
            continue

        soup = BeautifulSoup(html, 'html.parser')
        # Google search result containers
        for div in soup.select('div.g, div[data-sokoban-container]'):
            link_el = div.select_one('a[href^="http"]')
            if not link_el:
                continue
            href = link_el.get('href', '')
            # Skip Google's own pages
            if 'google.' in href or not href.startswith('http'):
                continue

            title_el = div.select_one('h3')
            title = title_el.get_text(strip=True) if title_el else link_el.get_text(strip=True)
            if not title or len(title) < 5:
                continue

            snippet_el = div.select_one('div.VwiC3b, span.aCOpRe, div[data-sncf]')
            snippet = snippet_el.get_text(strip=True) if snippet_el else ''
            full_text = f"{title} {snippet}"

            try:
                host = urllib.parse.urlparse(href).hostname or ''
            except Exception:
                host = ''
            if brand.get('website') and host and host in brand['website']:
                continue

            published = _extract_date(full_text)
            channel = _detect_channel(href)

            results.append({
                'brand_id': brand['id'], 'channel': channel,
                'title': title[:200], 'content': (snippet or title)[:500],
                'url': href, 'author': host,
                'found_at': _now(), 'published_at': published
            })
    return results

def scrape_google_site(brand, site, channel):
    """Search a specific platform via Google site: operator."""
    results = []
    keyword = brand['keywords'][0]
    _delay(4)
    query = urllib.parse.quote(f'site:{site} {keyword}')
    url = f'https://www.google.co.jp/search?q={query}&hl=ja&num=15'
    html = _safe_get(url, retries=1)
    if not html:
        return results

    soup = BeautifulSoup(html, 'html.parser')
    for div in soup.select('div.g, div[data-sokoban-container]'):
        link_el = div.select_one('a[href^="http"]')
        if not link_el:
            continue
        href = link_el.get('href', '')
        if 'google.' in href or site.split(' ')[0] not in href.lower():
            continue

        title_el = div.select_one('h3')
        title = title_el.get_text(strip=True) if title_el else link_el.get_text(strip=True)
        snippet_el = div.select_one('div.VwiC3b, span.aCOpRe')
        snippet = snippet_el.get_text(strip=True) if snippet_el else ''
        full_text = f"{title} {snippet}"

        try:
            host = urllib.parse.urlparse(href).hostname or ''
        except Exception:
            host = ''

        published = _extract_date(full_text)
        results.append({
            'brand_id': brand['id'], 'channel': channel,
            'title': title[:200], 'content': (snippet or title)[:500],
            'url': href, 'author': host,
            'found_at': _now(), 'published_at': published
        })
    return results

# ====== Yahoo Japan Search ======
def scrape_yahoo_search(brand):
    """General web search via Yahoo Japan Search (backup engine)."""
    results = []
    for keyword in brand['keywords'][:3]:
        _delay(2)
        query = urllib.parse.quote(keyword)
        url = f'https://search.yahoo.co.jp/search?p={query}&ei=UTF-8'
        html = _safe_get(url)
        if not html:
            continue

        soup = BeautifulSoup(html, 'html.parser')
        seen_urls = set()

        # Try structured parsing first: Yahoo search result sections
        for section in soup.select('section, div.algo, div.dd, li'):
            full_section_text = section.get_text(' ', strip=True)
            a = section.find('a', href=True)
            if not a:
                continue
            href = a.get('href', '')
            text = a.get_text(strip=True)
            if not (href.startswith('http') and text and len(text) > 10):
                continue
            if 'yahoo' in href.lower() or 'bing' in href.lower():
                continue
            if href in seen_urls or 'search.yahoo.co.jp/r/' in href:
                continue
            seen_urls.add(href)
            try:
                host = urllib.parse.urlparse(href).hostname or ''
            except Exception:
                host = ''
            if brand.get('website') and host and host in brand['website']:
                continue
            channel = _detect_channel(href)
            # Extract date from the full section text (includes date spans)
            published = _extract_date(full_section_text)
            results.append({
                'brand_id': brand['id'], 'channel': channel,
                'title': text[:200], 'content': full_section_text[:500],
                'url': href, 'author': host,
                'found_at': _now(), 'published_at': published
                })
    return results

def scrape_yahoo_site(brand, site, channel):
    """Search specific platforms via Yahoo Japan site: operator."""
    results = []
    keyword = brand['keywords'][0]
    _delay(2)
    query = urllib.parse.quote(f'site:{site} {keyword}')
    url = f'https://search.yahoo.co.jp/search?p={query}&ei=UTF-8'
    html = _safe_get(url)
    if not html:
        return results

    soup = BeautifulSoup(html, 'html.parser')
    seen_urls = set()
    for section in soup.select('section, div.algo, div.dd, li'):
        full_text = section.get_text(' ', strip=True)
        a = section.find('a', href=True)
        if not a:
            continue
        href = a.get('href', '')
        text = a.get_text(strip=True)
        if not (href.startswith('http') and text and len(text) > 10):
            continue
        if site.split(' ')[0] not in href.lower() or href in seen_urls:
            continue
        if 'search.yahoo.co.jp/r/' in href:
            continue
        seen_urls.add(href)
        try:
            host = urllib.parse.urlparse(href).hostname or ''
        except Exception:
            host = ''
        published = _extract_date(full_text)
        results.append({
            'brand_id': brand['id'], 'channel': channel,
            'title': text[:200], 'content': full_text[:500],
            'url': href, 'author': host,
            'found_at': _now(), 'published_at': published
        })
    return results

# ====== Yahoo Japan Chiebukuro ======
def scrape_chiebukuro(brand):
    """Search Yahoo Chiebukuro Q&A"""
    results = []
    for keyword in brand['keywords'][:2]:
        _delay(2)
        query = urllib.parse.quote(keyword)
        url = f'https://chiebukuro.yahoo.co.jp/search?p={query}&type=tag'
        html = _safe_get(url)
        if not html:
            continue

        soup = BeautifulSoup(html, 'html.parser')
        for item in soup.select('div.ClapLay_listItem, li.SearchResult, div.Result'):
            link_el = item.select_one('a')
            title = link_el.get_text(strip=True) if link_el else ''
            href = link_el['href'] if link_el and link_el.has_attr('href') else ''
            snippet_el = item.select_one('div.ClapLay_listDetail, p, div.Result__detail')
            snippet = snippet_el.get_text(strip=True) if snippet_el else title
            # Try to find date in the item
            date_el = item.select_one('time, span.ClapLay_listDate, span.Date')
            pub_date = None
            if date_el:
                pub_date = _extract_date(date_el.get_text(strip=True))
            if not pub_date:
                pub_date = _extract_date(snippet)

            if title and href:
                full_url = href if href.startswith('http') else f'https://chiebukuro.yahoo.co.jp{href}'
                results.append({
                    'brand_id': brand['id'], 'channel': 'yahoo',
                    'title': title, 'content': snippet,
                    'url': full_url, 'author': 'Yahoo! Chiebukuro',
                    'found_at': _now(), 'published_at': pub_date
                })
    return results

# ====== Master Scrape ======
def scrape_all_brands(brand):
    """Scrape all channels for a single brand - dual engine (Google + Yahoo)"""
    print(f"[Scraper] Scanning: {brand['name']}", flush=True)
    all_results = []
    seen_urls = set()

    def _add_results(r):
        for item in r:
            url = item.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                # Clean HTML tags from title and content
                item['title'] = _clean_text(item.get('title', ''))
                item['content'] = _clean_text(item.get('content', ''))
                all_results.append(item)

    try:
        # 1. Google general search (primary, better structured results)
        r = scrape_google(brand)
        _add_results(r)
        print(f"  Google Search: {len(r)}")

        # 2. Yahoo Japan general search (backup, different index)
        r = scrape_yahoo_search(brand)
        _add_results(r)
        print(f"  Yahoo Search: {len(r)}")

        # 3. Yahoo Chiebukuro Q&A
        r = scrape_chiebukuro(brand)
        _add_results(r)
        print(f"  Chiebukuro: {len(r)}")

        # 4. Platform-specific searches (Google site:)
        r = scrape_google_site(brand, 'twitter.com OR x.com', 'twitter')
        _add_results(r)
        print(f"  Twitter/X: {len(r)}")

        r = scrape_google_site(brand, 'instagram.com', 'instagram')
        _add_results(r)
        print(f"  Instagram: {len(r)}")

        r = scrape_google_site(brand, 'youtube.com', 'youtube')
        _add_results(r)
        print(f"  YouTube: {len(r)}")

        r = scrape_google_site(brand, 'facebook.com', 'facebook')
        _add_results(r)
        print(f"  Facebook: {len(r)}")

        r = scrape_google_site(brand, 'threads.net', 'threads')
        _add_results(r)
        print(f"  Threads: {len(r)}")

        # 5. Yahoo site: searches (backup for social platforms)
        r = scrape_yahoo_site(brand, 'twitter.com', 'twitter')
        _add_results(r)
        r = scrape_yahoo_site(brand, 'instagram.com', 'instagram')
        _add_results(r)
        r = scrape_yahoo_site(brand, 'youtube.com', 'youtube')
        _add_results(r)
        print(f"  Yahoo site: backups added")

    except Exception as e:
        print(f"  [Scraper] Error for {brand['name']}: {e}")

    print(f"  Total unique: {len(all_results)}", flush=True)
    return all_results
