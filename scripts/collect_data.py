"""Run a full scrape cycle and export data to static JSON for GitHub Pages.
Used by GitHub Actions daily workflow."""
import json
import os
import sys
import sqlite3
from datetime import datetime, timezone

# Setup paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
OUT_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
DATA_DIR = os.path.join(SCRIPT_DIR, 'data')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

from brands import BRANDS, CHANNELS
from scraper import scrape_all_brands
from analyzer import process_mentions

DB_PATH = os.path.join(DATA_DIR, 'sentiment.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS mentions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand_id TEXT NOT NULL,
            channel TEXT NOT NULL,
            title TEXT,
            content TEXT,
            url TEXT,
            author TEXT,
            sentiment TEXT DEFAULT 'neutral',
            sentiment_score INTEGER DEFAULT 0,
            is_noise INTEGER DEFAULT 0,
            is_valuable INTEGER DEFAULT 0,
            is_read INTEGER DEFAULT 0,
            is_actioned INTEGER DEFAULT 0,
            engagement_score INTEGER DEFAULT 0,
            found_at TEXT,
            published_at TEXT,
            UNIQUE(url, brand_id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scan_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at TEXT, completed_at TEXT,
            brands_scanned INTEGER DEFAULT 0,
            mentions_found INTEGER DEFAULT 0,
            status TEXT DEFAULT 'running'
        )
    """)
    conn.commit()
    conn.close()

def is_official_url(url, brand_id):
    if not url:
        return False
    for b in BRANDS:
        if b['id'] == brand_id:
            domain = b['website'].replace('https://', '').replace('http://', '').rstrip('/')
            return domain in url
    return False

def insert_mentions(mentions):
    conn = get_db()
    inserted = 0
    for m in mentions:
        if is_official_url(m.get('url', ''), m.get('brand_id', '')):
            continue
        try:
            conn.execute("""
                INSERT OR IGNORE INTO mentions
                (brand_id, channel, title, content, url, author, sentiment, sentiment_score,
                 is_noise, is_valuable, engagement_score, found_at, published_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (m['brand_id'], m['channel'], m.get('title',''), m['content'],
                  m.get('url',''), m.get('author',''), m.get('sentiment','neutral'),
                  m.get('sentiment_score',0), m.get('is_noise',0), m.get('is_valuable',0),
                  m.get('engagement_score',0), m['found_at'], m.get('published_at')))
            if conn.total_changes:
                inserted += 1
        except:
            pass
    conn.commit()
    conn.close()
    return inserted

def run_scan():
    print(f"\n{'='*60}")
    print(f"[Scan] Starting at {datetime.now(timezone.utc).isoformat()}")
    print(f"{'='*60}", flush=True)

    conn = get_db()
    conn.execute("INSERT INTO scan_logs (started_at, status) VALUES (?, 'running')",
                 (datetime.now(timezone.utc).isoformat(),))
    conn.commit()
    log_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()

    total_found = 0
    brands_done = 0

    for brand in BRANDS:
        print(f"[Scraper] Scanning: {brand['name']}", flush=True)
        try:
            raw = scrape_all_brands(brand)
            processed = process_mentions(raw, brand)
            inserted = insert_mentions(processed)
            total_found += inserted
            brands_done += 1
            print(f"  -> {len(raw)} raw, {inserted} new inserted", flush=True)
        except Exception as e:
            print(f"  -> Error: {e}", flush=True)
            brands_done += 1

        conn = get_db()
        conn.execute("UPDATE scan_logs SET brands_scanned=?, mentions_found=? WHERE id=?",
                     (brands_done, total_found, log_id))
        conn.commit()
        conn.close()

    conn = get_db()
    conn.execute("UPDATE scan_logs SET completed_at=?, status='completed', brands_scanned=?, mentions_found=? WHERE id=?",
                 (datetime.now(timezone.utc).isoformat(), brands_done, total_found, log_id))
    conn.commit()
    conn.close()

    print(f"\n[Scan] Complete: {brands_done} brands, {total_found} new mentions", flush=True)

def dict_row(cursor, row):
    return {col[0]: row[i] for i, col in enumerate(cursor.description)}

def export_json():
    """Export DB to static JSON files."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_row

    total = conn.execute("SELECT COUNT(*) as c FROM mentions").fetchone()['c']
    negative = conn.execute("SELECT COUNT(*) as c FROM mentions WHERE sentiment IN ('negative','very_negative')").fetchone()['c']
    valuable = conn.execute("SELECT COUNT(*) as c FROM mentions WHERE is_valuable=1").fetchone()['c']
    unread = conn.execute("SELECT COUNT(*) as c FROM mentions WHERE is_read=0").fetchone()['c']
    by_channel = conn.execute("SELECT channel, COUNT(*) as count FROM mentions GROUP BY channel").fetchall()
    by_sentiment = conn.execute("SELECT sentiment, COUNT(*) as count FROM mentions GROUP BY sentiment").fetchall()

    stats = {'total': total, 'negative': negative, 'valuable': valuable, 'unread': unread,
             'byChannel': by_channel, 'bySentiment': by_sentiment}

    brand_stats = []
    for b in BRANDS:
        t = conn.execute("SELECT COUNT(*) as c FROM mentions WHERE brand_id=?", (b['id'],)).fetchone()['c']
        n = conn.execute("SELECT COUNT(*) as c FROM mentions WHERE brand_id=? AND sentiment IN ('negative','very_negative')", (b['id'],)).fetchone()['c']
        p = conn.execute("SELECT COUNT(*) as c FROM mentions WHERE brand_id=? AND sentiment IN ('positive','very_positive')", (b['id'],)).fetchone()['c']
        if t > 0:
            brand_stats.append({'brand_id': b['id'], 'total': t, 'negative': n, 'positive': p})

    mentions = conn.execute("""
        SELECT * FROM mentions ORDER BY
            CASE sentiment WHEN 'very_negative' THEN 1 WHEN 'negative' THEN 2
                WHEN 'very_positive' THEN 3 WHEN 'positive' THEN 4 ELSE 5 END,
            found_at DESC
    """).fetchall()

    logs = conn.execute("SELECT * FROM scan_logs ORDER BY started_at DESC LIMIT 50").fetchall()
    conn.close()

    brands_info = [{
        'id': b['id'], 'name': b['name'], 'nameJa': b['nameJa'],
        'category': b['category'], 'categoryJa': b['categoryJa'],
        'categoryCn': b.get('categoryCn', b['category']),
        'website': b['website'], 'noiseRisk': b['noiseRisk']
    } for b in BRANDS]

    channels_info = [{'id': c['id'], 'name': c['name'], 'nameJa': c['nameJa'], 'icon': c['icon']} for c in CHANNELS]

    # Write all data into a single file for efficiency
    all_data = {
        'stats': stats,
        'brandStats': brand_stats,
        'mentions': mentions,
        'scanLogs': logs,
        'brands': brands_info,
        'channels': channels_info,
        'exportedAt': datetime.now(timezone.utc).isoformat()
    }
    with open(os.path.join(OUT_DIR, 'all.json'), 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False)

    print(f"[Export] {total} mentions -> {OUT_DIR}/all.json")

if __name__ == '__main__':
    init_db()
    run_scan()
    export_json()
