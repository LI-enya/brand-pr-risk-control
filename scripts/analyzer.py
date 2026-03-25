"""Sentiment analysis and noise filtering for brand mentions"""

from brands import BRANDS

# ====== Negative keywords (Japanese + English) ======
NEGATIVE_KEYWORDS = {
    # Severe (-3)
    '詐欺': -3, '最悪': -3, 'クソ': -3, 'ゴミ': -3, '不良品': -3, '粗悪': -3,
    'scam': -3, 'fraud': -3, 'terrible': -3, 'worst': -3, 'garbage': -3,
    # Strong (-2)
    '返品': -2, '返金': -2, '壊れ': -2, '割れ': -2, 'クレーム': -2, '苦情': -2,
    '被害': -2, 'ぼったくり': -2, '二度と': -2, '買わない': -2, '使えない': -2,
    'バキバキ': -2, '低品質': -2, '騙': -2,
    'refund': -2, 'broken': -2, 'complaint': -2, 'avoid': -2,
    # Moderate (-1)
    '残念': -1, 'がっかり': -1, '微妙': -1, 'イマイチ': -1, 'いまいち': -1,
    '期待はずれ': -1, '期待外れ': -1, '安っぽ': -1, 'チープ': -1, '遅い': -1,
    '届かない': -1, '連絡がない': -1, '無視': -1, '傷': -1, 'キズ': -1,
    '汚れ': -1, '臭い': -1, 'ニオイ': -1, '対応が悪': -1, '最低': -1,
    'ひどい': -1, '酷い': -1, '怒り': -1, '許せない': -1, 'ふざけ': -1,
    'disappointed': -1, 'waste': -1, 'never again': -1,
    # Legal escalation (-3)
    '消費者センター': -3, '弁護士': -3, '訴え': -3, '裁判': -3,
    '国民生活センター': -3, '通報': -3, '違法': -3,
}

POSITIVE_KEYWORDS = {
    # Strong (+3)
    '最高': 3, '大満足': 3, '感動': 3, '完璧': 3, '神': 3, 'コスパ最高': 3,
    'amazing': 3, 'love': 3, 'perfect': 3,
    # Good (+2)
    'おすすめ': 2, 'オススメ': 2, '買ってよかった': 2, 'リピート': 2, '人気': 2,
    'コスパ良': 2, 'お気に入り': 2,
    'recommend': 2, 'best': 2, 'quality': 2,
    # Mild (+1)
    '素晴らしい': 1, '美しい': 1, 'おしゃれ': 1, 'かわいい': 1, 'かっこいい': 1,
    '高級感': 1, '品質が良': 1, 'レビュー': 1,
    'beautiful': 1, 'gorgeous': 1,
    # Viral/engagement (+3)
    'バズ': 3, 'バズった': 3, '話題': 2, '万フォロワー': 3, '万いいね': 3,
}

# ====== Noise detection ======
def is_noise(mention, brand):
    content = ((mention.get('content', '') or '') + ' ' + (mention.get('title', '') or '')).lower()

    # Check if brand name itself appears in content (basic relevance check)
    brand_name_lower = brand['name'].lower()
    brand_name_ja = brand.get('nameJa', '').lower()
    has_brand_name = brand_name_lower in content or brand_name_ja in content
    has_cat = any(kw.lower() in content for kw in brand['categoryKeywords'])
    has_url = brand['website'].replace('https://', '').replace('/', '').lower() in content
    url_in_mention = brand['website'].replace('https://', '').rstrip('/').lower() in (mention.get('url', '') or '').lower()

    # High noise risk: filter out known noise patterns first
    if brand['noiseRisk'] == 'high':
        bid = brand['id']
        # Brand-specific noise patterns — always filter these out
        if bid == 'galapagos' and any(w in content for w in ['諸島', 'island', 'ゾウガメ', 'ダーウィン', 'エクアドル', '携帯', 'ガラケー', 'ガラパゴス化']):
            return True
        if bid == 'innerpeace' and any(w in content for w in ['瞑想', 'ヨガ', 'meditation', 'マインドフル', '心の平和', '精神']):
            return True
        if bid == 'chante' and any(w in content for w in ['日比谷', 'シャンテ・ド', '映画', '劇場', '歌']):
            return True
        if bid == 'laise' and any(w in content for w in ['レース編み', 'レースカーテン', 'レース生地', '競馬', 'カーレース', 'マラソン', 'race']):
            return True
        if bid == 'acex' and ('ace combat' in content or ('エース' in content and '家具' not in content)):
            return True

        # Accept if: has category keyword, brand URL in content/url, or brand name present
        if has_cat or has_url or url_in_mention:
            return False
        # Accept if brand name + any product-related term
        if has_brand_name and any(w in content for w in ['レビュー', '口コミ', '評判', '通販', '購入', '商品', '公式', 'review']):
            return False
        # Otherwise filter
        if not has_cat and not has_url and not url_in_mention:
            return True

    if brand['noiseRisk'] == 'medium':
        if has_cat or has_url or url_in_mention:
            return False
        if has_brand_name and any(w in content for w in ['レビュー', '口コミ', '評判', '通販', '購入', '商品', '公式', 'review']):
            return False
        if not has_cat and not has_url and not url_in_mention:
            return True

    # Skip official brand posts
    if mention.get('url') and brand['website'].replace('https://', '').replace('/', '') in (mention.get('url', '') or ''):
        return True

    return False


# ====== Sentiment analysis ======
def analyze_sentiment(text):
    lower = text.lower()
    score = 0
    neg_count = 0
    pos_count = 0

    for kw, weight in NEGATIVE_KEYWORDS.items():
        if kw.lower() in lower:
            score += weight
            neg_count += 1

    for kw, weight in POSITIVE_KEYWORDS.items():
        if kw.lower() in lower:
            score += weight
            pos_count += 1

    if score <= -5:
        sentiment = 'very_negative'
    elif score <= -1:
        sentiment = 'negative'
    elif score >= 5:
        sentiment = 'very_positive'
    elif score >= 1:
        sentiment = 'positive'
    else:
        sentiment = 'neutral'

    return {'sentiment': sentiment, 'score': score, 'neg_count': neg_count, 'pos_count': pos_count}


def is_valuable(mention, sentiment_result):
    """Valuable = clearly negative or very positive (high engagement)"""
    if sentiment_result['sentiment'] == 'very_negative':
        return True
    if sentiment_result['sentiment'] == 'negative' and sentiment_result['neg_count'] >= 2:
        return True
    if sentiment_result['sentiment'] == 'very_positive':
        return True

    content = (mention.get('content', '') or '').lower()
    if any(kw in content for kw in ['消費者センター', '弁護士', '訴え', 'バズ', '万フォロワー', '万いいね']):
        return True

    return False


def process_mentions(raw_mentions, brand):
    """Process raw scraped mentions: noise filter + sentiment + value assessment"""
    results = []
    for m in raw_mentions:
        noise = is_noise(m, brand)
        full_text = (m.get('title', '') or '') + ' ' + (m.get('content', '') or '')
        sent = analyze_sentiment(full_text)
        val = not noise and is_valuable(m, sent)

        results.append({
            **m,
            'sentiment': sent['sentiment'],
            'sentiment_score': sent['score'],
            'is_noise': 1 if noise else 0,
            'is_valuable': 1 if val else 0,
            'engagement_score': 0
        })
    return results
