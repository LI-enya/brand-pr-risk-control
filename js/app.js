// ====== i18n ======
const I18N = {
  ja: {
    title: 'ブランドPRリスク管理',
    page_title: 'Brand PR Risk Control',
    total_mentions: '総メンション数', negative_mentions: 'ネガティブ',
    valuable_mentions: '要対応', unread_mentions: '未読',
    brand: 'ブランド', channel: 'チャネル', sentiment: '感情',
    filter_type: 'フィルタ', search: '検索', search_placeholder: 'キーワード...',
    all_brands: '全ブランド', all_channels: '全チャネル', all_sentiments: '全て',
    very_negative: '深刻なネガティブ', neg: 'ネガティブ', neutral_opt: '中立',
    pos: 'ポジティブ', very_positive: '非常にポジティブ',
    all: '全て', valuable_only: '要対応のみ', unread_only: '未読のみ',
    brand_overview: 'ブランド別概要', mentions_list: 'メンション一覧',
    loading: '読み込み中...', load_more: 'もっと見る',
    scan_history: 'スキャン履歴',
    no_mentions: 'メンションが見つかりません',
    no_mentions_hint: 'フィルタ条件を変更してください',
    no_brands: 'まだデータがありません', no_scan_logs: 'スキャン履歴なし',
    open_link: 'リンクを開く',
    detail_brand: 'ブランド', detail_channel: 'チャネル',
    detail_sentiment: '感情分析', detail_author: '投稿者',
    detail_found: '発見日時', detail_content: '内容',
    total_count: '件', legend_total: '合計', legend_neg: 'ネガ', legend_pos: 'ポジ',
    tag_valuable: '要対応', tag_noise: 'ノイズ',
    date_from: '開始日', date_to: '終了日', date_type: '日付種別',
    date_found: '発見日', date_published: '公開日',
    detail_published: '公開日', published_unknown: '不明',
    noise_only: 'ノイズのみ', relevant_only: '関連のみ',
    last_update: '最終更新', mentions_found: '件発見',
  },
  zh: {
    title: '品牌PR风控',
    page_title: 'Brand PR Risk Control',
    total_mentions: '总提及数', negative_mentions: '负面提及',
    valuable_mentions: '需处理', unread_mentions: '未读',
    brand: '品牌', channel: '渠道', sentiment: '情感',
    filter_type: '筛选', search: '搜索', search_placeholder: '关键词...',
    all_brands: '全部品牌', all_channels: '全部渠道', all_sentiments: '全部',
    very_negative: '严重负面', neg: '负面', neutral_opt: '中性',
    pos: '正面', very_positive: '高度正面',
    all: '全部', valuable_only: '仅需处理', unread_only: '仅未读',
    brand_overview: '品牌概览', mentions_list: '提及列表',
    loading: '加载中...', load_more: '加载更多',
    scan_history: '扫描历史',
    no_mentions: '未找到相关提及',
    no_mentions_hint: '请修改筛选条件',
    no_brands: '暂无数据', no_scan_logs: '暂无扫描记录',
    open_link: '打开链接',
    detail_brand: '品牌', detail_channel: '渠道',
    detail_sentiment: '情感分析', detail_author: '作者',
    detail_found: '发现时间', detail_content: '内容',
    total_count: '条', legend_total: '合计', legend_neg: '负面', legend_pos: '正面',
    tag_valuable: '需处理', tag_noise: '噪音',
    date_from: '开始日期', date_to: '结束日期', date_type: '日期类型',
    date_found: '发现日', date_published: '发布日',
    detail_published: '发布日期', published_unknown: '未知',
    noise_only: '仅噪音', relevant_only: '仅相关',
    last_update: '最后更新', mentions_found: '条发现',
  }
};

let currentLang = localStorage.getItem('lang') || 'ja';
let currentOffset = 0;
const PAGE_SIZE = 50;

// Data store (loaded from static JSON)
let ALL_DATA = null;
let BRANDS_MAP = {};
const CHANNELS_MAP = {
  google: { name: 'Google', icon: '🔍' },
  yahoo: { name: 'Yahoo!知恵袋', icon: '💬' },
  twitter: { name: 'X (Twitter)', icon: '𝕏' },
  instagram: { name: 'Instagram', icon: '📷' },
  threads: { name: 'Threads', icon: '🧵' },
  facebook: { name: 'Facebook', icon: '📘' },
  youtube: { name: 'YouTube', icon: '▶️' }
};
const SENTIMENT_EMOJI = {
  very_negative: '🔴', negative: '🟠', neutral: '⚪', positive: '🟢', very_positive: '🔵'
};
const SENTIMENT_LABELS = {
  ja: { very_negative: '深刻', negative: 'ネガ', neutral: '中立', positive: 'ポジ', very_positive: '高ポジ' },
  zh: { very_negative: '严重负面', negative: '负面', neutral: '中性', positive: '正面', very_positive: '高度正面' }
};

function setLang(lang) {
  currentLang = lang;
  localStorage.setItem('lang', lang);
  document.querySelectorAll('.lang-btn').forEach(btn =>
    btn.classList.toggle('active', btn.dataset.lang === lang)
  );
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (I18N[lang][key]) {
      if (el.tagName === 'INPUT') el.placeholder = I18N[lang][key];
      else el.textContent = I18N[lang][key];
    }
  });
  document.title = I18N[lang].page_title;
  document.getElementById('filterSearch').placeholder = I18N[lang].search_placeholder;
  if (ALL_DATA) {
    renderBrandOverview();
    applyFilters();
    renderScanLogs();
  }
}

function t(key) { return I18N[currentLang][key] || key; }

// ====== Client-side filtering ======
function getFilteredMentions() {
  if (!ALL_DATA) return [];
  let mentions = ALL_DATA.mentions;

  const brand = document.getElementById('filterBrand').value;
  const channel = document.getElementById('filterChannel').value;
  const sentiment = document.getElementById('filterSentiment').value;
  const valuable = document.getElementById('filterValuable').value;
  const search = document.getElementById('filterSearch').value.toLowerCase();
  const dateType = document.getElementById('filterDateType').value;
  const dateFrom = document.getElementById('filterDateFrom').value;
  const dateTo = document.getElementById('filterDateTo').value;

  if (brand) mentions = mentions.filter(m => m.brand_id === brand);
  if (channel) mentions = mentions.filter(m => m.channel === channel);
  if (sentiment) mentions = mentions.filter(m => m.sentiment === sentiment);
  if (valuable === '1') mentions = mentions.filter(m => m.is_valuable);
  if (valuable === 'relevant') mentions = mentions.filter(m => !m.is_noise);
  if (valuable === 'noise') mentions = mentions.filter(m => m.is_noise);
  if (search) mentions = mentions.filter(m =>
    ((m.content || '') + ' ' + (m.title || '')).toLowerCase().includes(search)
  );
  if (dateFrom || dateTo) {
    const col = dateType === 'published' ? 'published_at' : 'found_at';
    if (dateFrom) {
      mentions = mentions.filter(m => {
        const d = m[col];
        if (!d) return false;
        const dateStr = new Date(new Date(d).getTime() + 9*3600000).toISOString().slice(0,10);
        return dateStr >= dateFrom;
      });
    }
    if (dateTo) {
      mentions = mentions.filter(m => {
        const d = m[col];
        if (!d) return false;
        const dateStr = new Date(new Date(d).getTime() + 9*3600000).toISOString().slice(0,10);
        return dateStr <= dateTo;
      });
    }
  }
  return mentions;
}

function applyFilters() {
  currentOffset = 0;
  renderMentions();
}

function renderMentions(append = false) {
  const filtered = getFilteredMentions();
  const page = filtered.slice(0, currentOffset + PAGE_SIZE);
  const container = document.getElementById('mentionsList');
  const countEl = document.getElementById('mentionsCount');

  container.innerHTML = '';

  if (page.length === 0) {
    container.innerHTML = `<div class="empty-state">
      <div class="empty-icon">📡</div>
      <div class="empty-title">${t('no_mentions')}</div>
      <div class="empty-hint">${t('no_mentions_hint')}</div>
    </div>`;
    countEl.textContent = '';
    document.getElementById('loadMore').style.display = 'none';
    return;
  }

  page.forEach(m => container.appendChild(createMentionEl(m)));
  countEl.textContent = `${page.length} / ${filtered.length} ${t('total_count')}`;
  document.getElementById('loadMore').style.display = page.length < filtered.length ? '' : 'none';
}

function loadMore() {
  currentOffset += PAGE_SIZE;
  renderMentions();
}

function createMentionEl(m) {
  const div = document.createElement('div');
  const classes = ['mention-item'];
  if (m.is_noise) classes.push('noise');
  if (m.is_valuable) classes.push('valuable');
  if (m.sentiment === 'very_negative' || m.sentiment === 'negative') classes.push('negative');
  div.className = classes.join(' ');
  div.onclick = () => showDetail(m);

  const brand = BRANDS_MAP[m.brand_id] || { name: m.brand_id };
  const channel = CHANNELS_MAP[m.channel] || { icon: '🌐', name: m.channel };
  const sentimentLabel = SENTIMENT_LABELS[currentLang][m.sentiment] || m.sentiment;
  const locale = currentLang === 'ja' ? 'ja-JP' : 'zh-CN';
  const foundStr = m.found_at ? new Date(m.found_at).toLocaleString(locale) : '';
  const pubStr = m.published_at ? new Date(m.published_at).toLocaleDateString(locale) : '';

  let tags = '';
  if (m.is_noise) tags += `<span class="tag tag-noise">${t('tag_noise')}</span>`;
  if (m.is_valuable) tags += `<span class="tag tag-valuable">${t('tag_valuable')}</span>`;
  if (m.sentiment === 'very_negative' || m.sentiment === 'negative') tags += `<span class="tag tag-negative">${sentimentLabel}</span>`;
  if (m.sentiment === 'very_positive' || m.sentiment === 'positive') tags += `<span class="tag tag-positive">${sentimentLabel}</span>`;

  div.innerHTML = `
    <div class="mention-sentiment sentiment-${m.sentiment}">${SENTIMENT_EMOJI[m.sentiment] || '⚪'}</div>
    <div class="mention-body">
      <div class="mention-meta">
        <span class="mention-brand">${brand.name}</span>
        <span class="mention-channel">${channel.icon} ${channel.name}</span>
        ${pubStr ? `<span class="mention-time mention-pub-date">${pubStr}</span>` : ''}
        <span class="mention-time mention-found-date">${foundStr}</span>
      </div>
      <div class="mention-title">${escHtml(m.title || '')}</div>
      <div class="mention-content">${escHtml(m.content || '')}</div>
      ${tags ? `<div class="mention-tags">${tags}</div>` : ''}
    </div>
  `;
  return div;
}

function showDetail(m) {
  const brand = BRANDS_MAP[m.brand_id] || { name: m.brand_id };
  const channel = CHANNELS_MAP[m.channel] || { icon: '🌐', name: m.channel };
  const sentimentLabel = SENTIMENT_LABELS[currentLang][m.sentiment] || m.sentiment;

  document.getElementById('modalTitle').textContent = m.title || t('detail_content');
  document.getElementById('modalBody').innerHTML = `
    <div class="detail-row"><div class="detail-label">${t('detail_brand')}</div><div class="detail-value">${brand.name}</div></div>
    <div class="detail-row"><div class="detail-label">${t('detail_channel')}</div><div class="detail-value">${channel.icon} ${channel.name}</div></div>
    <div class="detail-row"><div class="detail-label">${t('detail_sentiment')}</div><div class="detail-value">${SENTIMENT_EMOJI[m.sentiment]} ${sentimentLabel} (score: ${m.sentiment_score})</div></div>
    <div class="detail-row"><div class="detail-label">${t('detail_published')}</div><div class="detail-value">${m.published_at ? new Date(m.published_at).toLocaleDateString(currentLang === 'ja' ? 'ja-JP' : 'zh-CN') : t('published_unknown')}</div></div>
    <div class="detail-row"><div class="detail-label">${t('detail_found')}</div><div class="detail-value">${m.found_at ? new Date(m.found_at).toLocaleString() : '-'}</div></div>
    <div class="detail-row"><div class="detail-label">${t('detail_content')}</div><div class="detail-content">${escHtml(m.content || '')}</div></div>
  `;

  let footerHtml = '';
  if (m.url) footerHtml += `<a href="${escHtml(m.url)}" target="_blank" rel="noopener" class="btn btn-primary">${t('open_link')}</a>`;
  document.getElementById('modalFooter').innerHTML = footerHtml;
  document.getElementById('modalOverlay').classList.add('show');
}

function closeModal() {
  document.getElementById('modalOverlay').classList.remove('show');
}

function renderStats() {
  const s = ALL_DATA.stats;
  document.getElementById('statTotal').textContent = s.total;
  document.getElementById('statNegative').textContent = s.negative;
  document.getElementById('statValuable').textContent = s.valuable;
  document.getElementById('statUnread').textContent = s.unread;
}

function renderBrands() {
  const select = document.getElementById('filterBrand');
  while (select.options.length > 1) select.remove(1);
  ALL_DATA.brands.forEach(b => {
    BRANDS_MAP[b.id] = b;
    const opt = document.createElement('option');
    opt.value = b.id;
    opt.textContent = `${b.name} (${b.nameJa})`;
    select.appendChild(opt);
  });
  // Populate channel filter
  const chSelect = document.getElementById('filterChannel');
  while (chSelect.options.length > 1) chSelect.remove(1);
  ALL_DATA.channels.forEach(c => {
    CHANNELS_MAP[c.id] = c;
    const opt = document.createElement('option');
    opt.value = c.id;
    opt.textContent = `${c.icon} ${c.name}`;
    chSelect.appendChild(opt);
  });
}

function renderBrandOverview() {
  const data = ALL_DATA.brandStats;
  const container = document.getElementById('brandCards');
  container.innerHTML = '';
  if (data.length === 0) { container.innerHTML = `<div class="empty">${t('no_brands')}</div>`; return; }
  data.sort((a, b) => b.negative - a.negative || b.total - a.total);
  data.forEach(b => {
    const card = document.createElement('div');
    card.className = 'brand-card' + (b.negative > 0 ? ' has-negative' : '');
    card.onclick = () => {
      document.getElementById('filterBrand').value = b.brand_id;
      applyFilters();
      document.querySelector('.mentions-section').scrollIntoView({ behavior: 'smooth' });
    };
    const brand = BRANDS_MAP[b.brand_id] || { name: b.brand_id };
    const catLabel = currentLang === 'zh' ? (brand.categoryCn || brand.category) : (brand.categoryJa || brand.category);
    card.innerHTML = `
      <div class="brand-card-header">
        <span class="brand-card-name">${brand.name || b.brand_id}</span>
        <span class="brand-card-category">${catLabel}</span>
      </div>
      <div class="brand-card-stats">
        <span class="brand-stat" title="${t('legend_total')}"><span class="dot dot-total"></span> ${b.total}</span>
        <span class="brand-stat" title="${t('legend_neg')}"><span class="dot dot-neg"></span> ${b.negative}</span>
        <span class="brand-stat" title="${t('legend_pos')}"><span class="dot dot-pos"></span> ${b.positive}</span>
      </div>
    `;
    container.appendChild(card);
  });
}

function renderScanLogs() {
  const data = ALL_DATA.scanLogs || [];
  const container = document.getElementById('scanLogs');
  container.innerHTML = '';
  if (data.length === 0) { container.innerHTML = `<div class="empty">${t('no_scan_logs')}</div>`; return; }
  data.slice(0, 10).forEach(log => {
    const div = document.createElement('div');
    div.className = 'scan-log-item';
    const statusClass = log.status === 'completed' ? 'success' : log.status === 'running' ? 'running' : 'error';
    const timeStr = log.started_at ? new Date(log.started_at).toLocaleString() : '-';
    div.innerHTML = `
      <span class="scan-log-status ${statusClass}">${log.status}</span>
      <span class="scan-log-time">${timeStr}</span>
      <span class="scan-log-stats">${log.mentions_found || 0} ${t('mentions_found')}</span>
    `;
    container.appendChild(div);
  });
}

function escHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

let searchTimer;
function debounceSearch() {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => applyFilters(), 400);
}

async function init() {
  setLang(currentLang);
  try {
    const resp = await fetch('data/all.json');
    ALL_DATA = await resp.json();
  } catch (e) {
    document.getElementById('mentionsList').innerHTML =
      '<div class="empty-state"><div class="empty-icon">⚠️</div><div class="empty-title">Data not available</div></div>';
    return;
  }

  renderBrands();
  renderStats();
  renderBrandOverview();
  renderMentions();
  renderScanLogs();

  // Show last update time
  if (ALL_DATA.exportedAt) {
    const d = new Date(ALL_DATA.exportedAt);
    document.getElementById('lastUpdate').textContent =
      `${t('last_update')}: ${d.toLocaleDateString()} ${d.toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})}`;
  }
}

document.addEventListener('DOMContentLoaded', init);
