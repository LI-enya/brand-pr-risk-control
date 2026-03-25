"""Export sentiment-monitor SQLite data to static JSON files for GitHub Pages."""
import json
import os
import sqlite3
import sys

# Add parent sentiment-monitor to path
SM_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'sentiment-monitor')
sys.path.insert(0, SM_DIR)

DB_PATH = os.path.join(SM_DIR, 'data', 'sentiment.db')
OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

def dict_row(cursor, row):
    return {col[0]: row[i] for i, col in enumerate(cursor.description)}

def export():
    os.makedirs(OUT_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_row

    # Stats
    total = conn.execute("SELECT COUNT(*) as c FROM mentions").fetchone()['c']
    negative = conn.execute("SELECT COUNT(*) as c FROM mentions WHERE sentiment IN ('negative','very_negative')").fetchone()['c']
    valuable = conn.execute("SELECT COUNT(*) as c FROM mentions WHERE is_valuable=1").fetchone()['c']
    unread = conn.execute("SELECT COUNT(*) as c FROM mentions WHERE is_read=0").fetchone()['c']
    by_channel = conn.execute("SELECT channel, COUNT(*) as count FROM mentions GROUP BY channel").fetchall()
    by_sentiment = conn.execute("SELECT sentiment, COUNT(*) as count FROM mentions GROUP BY sentiment").fetchall()

    stats = {
        'total': total, 'negative': negative, 'valuable': valuable, 'unread': unread,
        'byChannel': by_channel, 'bySentiment': by_sentiment
    }
    with open(os.path.join(OUT_DIR, 'stats.json'), 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False)

    # Brand stats
    from brands import BRANDS
    brand_stats = []
    for b in BRANDS:
        t = conn.execute("SELECT COUNT(*) as c FROM mentions WHERE brand_id=?", (b['id'],)).fetchone()['c']
        n = conn.execute("SELECT COUNT(*) as c FROM mentions WHERE brand_id=? AND sentiment IN ('negative','very_negative')", (b['id'],)).fetchone()['c']
        p = conn.execute("SELECT COUNT(*) as c FROM mentions WHERE brand_id=? AND sentiment IN ('positive','very_positive')", (b['id'],)).fetchone()['c']
        if t > 0:
            brand_stats.append({'brand_id': b['id'], 'total': t, 'negative': n, 'positive': p})
    with open(os.path.join(OUT_DIR, 'brands_stats.json'), 'w', encoding='utf-8') as f:
        json.dump(brand_stats, f, ensure_ascii=False)

    # All mentions (for static site)
    mentions = conn.execute("""
        SELECT * FROM mentions
        ORDER BY
            CASE sentiment
                WHEN 'very_negative' THEN 1
                WHEN 'negative' THEN 2
                WHEN 'very_positive' THEN 3
                WHEN 'positive' THEN 4
                ELSE 5
            END,
            found_at DESC
    """).fetchall()
    with open(os.path.join(OUT_DIR, 'mentions.json'), 'w', encoding='utf-8') as f:
        json.dump(mentions, f, ensure_ascii=False)

    # Scan logs
    logs = conn.execute("SELECT * FROM scan_logs ORDER BY started_at DESC LIMIT 50").fetchall()
    with open(os.path.join(OUT_DIR, 'scan_logs.json'), 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False)

    conn.close()
    print(f"[Export] {total} mentions, {len(brand_stats)} brands -> {OUT_DIR}")

if __name__ == '__main__':
    export()
