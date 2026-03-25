"""Brand configuration for all monitored brands"""

BRANDS = [
    {
        'id': 'indoorplus', 'name': 'Indoorplus', 'nameJa': 'インドアプラス',
        'category': 'furniture', 'categoryJa': '家具・インテリア', 'categoryCn': '家具家居',
        'website': 'https://indoorplus.jp/',
        'keywords': ['Indoorplus', 'indoorplus', 'インドアプラス', 'インドールプラス'],
        'noiseRisk': 'low',
        'categoryKeywords': ['家具', 'インテリア', 'ソファ', 'テーブル', '椅子', 'furniture', 'interior']
    },
    {
        'id': 'lduvin', 'name': 'LDUVIN', 'nameJa': 'ラデュービン',
        'category': 'luggage', 'categoryJa': 'スーツケース', 'categoryCn': '行李箱',
        'website': 'https://lduvin.jp/',
        'keywords': ['LDUVIN', 'lduvin', 'ラデュービン'],
        'noiseRisk': 'low',
        'categoryKeywords': ['スーツケース', 'キャリー', '旅行', 'luggage', 'suitcase']
    },
    {
        'id': 'isole', 'name': 'ISOLÉ', 'nameJa': 'イソレ',
        'category': 'bags', 'categoryJa': 'レディースバッグ', 'categoryCn': '女包',
        'website': 'https://isole.jp/',
        'keywords': ['isole', 'ISOLÉ', 'イソレ', 'イゾレ', 'いそれ', 'いぞれ'],
        'noiseRisk': 'medium',
        'categoryKeywords': ['バッグ', 'かばん', '鞄', 'bag', 'ハンドバッグ', 'ショルダー']
    },
    {
        'id': 'offineo', 'name': 'OFFINEO', 'nameJa': 'オフィネオ',
        'category': 'office_furniture', 'categoryJa': '法人家具', 'categoryCn': '办公家具',
        'website': 'https://offineo.jp/',
        'keywords': ['OFFINEO', 'offineo', 'オフィネオ'],
        'noiseRisk': 'low',
        'categoryKeywords': ['オフィス', '家具', 'デスク', 'チェア', 'office', 'furniture']
    },
    {
        'id': 'acex', 'name': 'ACEX', 'nameJa': 'アックス',
        'category': 'furniture', 'categoryJa': '家具・インテリア', 'categoryCn': '家具家居',
        'website': 'https://acex.jp/',
        'keywords': ['ACEX 家具', 'ACEX furniture', 'ACEX ソファ', 'acex.jp', 'ACEX インテリア'],
        'noiseRisk': 'high',
        'categoryKeywords': ['家具', 'インテリア', 'ソファ', 'テーブル', '椅子', 'furniture']
    },
    {
        'id': 'innerpeace', 'name': 'INNERPEACE', 'nameJa': 'インナーピース',
        'category': 'furniture', 'categoryJa': '家具・インテリア', 'categoryCn': '家具家居',
        'website': 'https://innerpeace.jp/',
        'keywords': ['INNERPEACE 家具', 'インナーピース 家具', 'INNERPEACE furniture', 'innerpeace.jp', 'INNERPEACE ソファ'],
        'noiseRisk': 'high',
        'categoryKeywords': ['家具', 'インテリア', 'ソファ', 'テーブル', '椅子', 'furniture']
    },
    {
        'id': 'ergopro', 'name': 'ERGOPRO', 'nameJa': 'エルゴプロ',
        'category': 'office_furniture', 'categoryJa': '法人家具', 'categoryCn': '办公家具',
        'website': 'https://ergopro.jp/',
        'keywords': ['ERGOPRO', 'ergopro', 'エルゴプロ'],
        'noiseRisk': 'low',
        'categoryKeywords': ['オフィス', '家具', 'デスク', 'チェア', 'office', 'エルゴ']
    },
    {
        'id': 'galapagos', 'name': 'GALAPAGOS', 'nameJa': 'ガラパゴス',
        'category': 'bags', 'categoryJa': 'メンズバッグ', 'categoryCn': '男包',
        'website': 'https://galapagos100.com/',
        'keywords': ['GALAPAGOS バッグ', 'ガラパゴス バッグ', 'GALAPAGOS bag', 'galapagos100', 'ガラパゴス 鞄'],
        'noiseRisk': 'high',
        'categoryKeywords': ['バッグ', 'かばん', '鞄', 'bag', 'メンズ', 'ビジネスバッグ']
    },
    {
        'id': 'chante', 'name': 'CHANTE', 'nameJa': 'シャンテ',
        'category': 'furniture', 'categoryJa': '家具・インテリア', 'categoryCn': '家具家居',
        'website': 'https://chante.jp/',
        'keywords': ['CHANTE 家具', 'シャンテ 家具', 'CHANTE furniture', 'chante.jp', 'シャンテ インテリア'],
        'noiseRisk': 'high',
        'categoryKeywords': ['家具', 'インテリア', 'ソファ', 'テーブル', '椅子', 'furniture']
    },
    {
        'id': 'laise', 'name': "l'aisé", 'nameJa': 'レーズ',
        'category': 'shoes', 'categoryJa': 'レディースシューズ', 'categoryCn': '女鞋',
        'website': 'https://laiseglobal.com/',
        'keywords': ["l'aisé 靴", "l'aisé shoes", 'laise シューズ', 'laiseglobal', "l'aisé パンプス"],
        'noiseRisk': 'high',
        'categoryKeywords': ['靴', 'シューズ', 'パンプス', 'ヒール', 'shoes', 'サンダル']
    },
    {
        'id': 'hueoffice', 'name': 'HUEOFFICE', 'nameJa': 'ヒューオフィス',
        'category': 'office_furniture', 'categoryJa': '法人家具', 'categoryCn': '办公家具',
        'website': 'https://hueoffice.jp/',
        'keywords': ['HUEOFFICE', 'hueoffice', 'ヒューオフィス'],
        'noiseRisk': 'low',
        'categoryKeywords': ['オフィス', '家具', 'デスク', 'チェア', 'office', 'furniture']
    },
    {
        'id': 'uandme', 'name': 'UANDME', 'nameJa': 'ユーアンドミー',
        'category': 'pet', 'categoryJa': 'ペット用品・家具', 'categoryCn': '宠物用品家具',
        'website': 'https://uandme-pet.com/',
        'keywords': ['UANDME ペット', 'ユーアンドミー ペット', 'uandme-pet', 'UANDME 犬', 'UANDME 猫'],
        'noiseRisk': 'medium',
        'categoryKeywords': ['ペット', '犬', '猫', 'pet', 'ドッグ', 'キャット']
    }
]

CHANNELS = [
    {'id': 'google', 'name': 'Google', 'nameJa': 'Google検索', 'icon': '🔍'},
    {'id': 'yahoo', 'name': 'Yahoo!知恵袋', 'nameJa': 'Yahoo!知恵袋', 'icon': '💬'},
    {'id': 'twitter', 'name': 'X (Twitter)', 'nameJa': 'X (Twitter)', 'icon': '𝕏'},
    {'id': 'instagram', 'name': 'Instagram', 'nameJa': 'Instagram', 'icon': '📷'},
    {'id': 'threads', 'name': 'Threads', 'nameJa': 'Threads', 'icon': '🧵'},
    {'id': 'facebook', 'name': 'Facebook', 'nameJa': 'Facebook', 'icon': '📘'},
    {'id': 'youtube', 'name': 'YouTube', 'nameJa': 'YouTube', 'icon': '▶️'},
]
