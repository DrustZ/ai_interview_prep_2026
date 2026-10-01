/* global window, document, marked, hljs */
(function () {
  const DATA = window.DATA;
  const P = DATA.problems;
  const TOOL = DATA.tool;

  document.getElementById('builtinfo').textContent =
    `${P.length} 题 · ${P.filter(p => p.content && p.content.length > 100).length} 题含正文/答案 · 抓取 ${DATA.built}`;

  const SRC_LABEL = { briefing: '情报', external: '外链帖', qbank: '会员题', oj: 'OJ' };
  const COMPANY_LABEL = { openai: 'OpenAI', anthropic: 'Anthropic' };
  const FREQ_ORDER = { 'very-high': 0, high: 1, medium: 2, low: 3, single: 4 };

  // ---- filter state: every dimension is a Set (multi-select). Empty set = no filter. ----
  // Cross-dimension = AND. Within a dimension = OR.
  const F = {
    company: new Set(), source: new Set(), status: new Set(),
    category: new Set(), freq: new Set(), role: new Set(), stage: new Set(),
  };
  let q = '';

  // how each dimension pulls candidate values from a problem
  const DIM = {
    company: p => [p.company],
    source: p => [p.source],
    status: p => [(p.content && p.content.length > 100) ? 'content' : 'link'],
    category: p => [p.category],
    freq: p => [p.frequency],
    role: p => p.roles,
    stage: p => p.stages,
  };
  const DIM_LABEL = {
    company: v => COMPANY_LABEL[v] || v,
    source: v => SRC_LABEL[v] || v,
    status: v => (v === 'content' ? '含正文' : '仅链接'),
    category: v => v, freq: v => v, role: v => v, stage: v => v,
  };
  const GROUPS = [
    ['company', '公司 Company'], ['source', '题型 Source'], ['status', '状态 Status'],
    ['category', '类别 Category'], ['freq', '频率 Frequency'], ['role', '岗位 Role'], ['stage', '轮次 Stage'],
  ];

  // does problem p pass all dimensions EXCEPT the named one? (for computing chip counts)
  function passExcept(p, except) {
    for (const dim of Object.keys(F)) {
      if (dim === except || F[dim].size === 0) continue;
      const vals = DIM[dim](p);
      if (!vals.some(v => F[dim].has(v))) return false;
    }
    if (q) {
      const s = q.toLowerCase();
      const hay = (p.title + ' ' + p.tags.join(' ') + ' ' + (p.content || '').slice(0, 400)).toLowerCase();
      if (!hay.includes(s)) return false;
    }
    return true;
  }
  function match(p) { return passExcept(p, null); }

  // counts for a dimension's chips, respecting all OTHER active filters
  function chipCounts(dim) {
    const m = {};
    for (const p of P) {
      if (!passExcept(p, dim)) continue;
      for (const v of DIM[dim](p)) { if (v == null) continue; m[v] = (m[v] || 0) + 1; }
    }
    return m;
  }

  // ---- sidebar ----
  function renderSidebar() {
    const s = document.getElementById('sidebar'); s.innerHTML = '';
    for (const [dim, title] of GROUPS) {
      const counts = chipCounts(dim);
      const entries = Object.entries(counts);
      if (dim === 'freq') entries.sort((a, b) => (FREQ_ORDER[a[0]] ?? 9) - (FREQ_ORDER[b[0]] ?? 9));
      else entries.sort((a, b) => b[1] - a[1]);
      if (!entries.length) continue;
      const g = document.createElement('div'); g.className = 'filter-group';
      const h = document.createElement('h3');
      h.innerHTML = `${title}<span class="gmode">${F[dim].size ? '多选·OR' : ''}</span>`;
      g.appendChild(h);
      for (const [v, c] of entries) {
        const on = F[dim].has(v);
        const b = document.createElement('button');
        b.className = 'chip' + (on ? ' on' : '');
        b.innerHTML = `${esc(DIM_LABEL[dim](v))} <span class="n">${c}</span>`;
        b.onclick = () => { on ? F[dim].delete(v) : F[dim].add(v); syncTabs(); render(); };
        g.appendChild(b);
      }
      s.appendChild(g);
    }
  }

  // ---- active filter bar ----
  function renderActiveBar() {
    const bar = document.getElementById('activebar');
    const active = [];
    for (const dim of Object.keys(F)) for (const v of F[dim]) active.push([dim, v]);
    if (!active.length && !q) { bar.style.display = 'none'; return; }
    bar.style.display = 'flex'; bar.innerHTML = '<span class="lbl">已选:</span>';
    for (const [dim, v] of active) {
      const b = document.createElement('button');
      b.className = 'achip';
      b.innerHTML = `${esc(DIM_LABEL[dim](v))} ✕`;
      b.title = dim;
      b.onclick = () => { F[dim].delete(v); syncTabs(); render(); };
      bar.appendChild(b);
    }
    if (q) {
      const b = document.createElement('button'); b.className = 'achip';
      b.innerHTML = `“${esc(q)}” ✕`;
      b.onclick = () => { q = ''; document.getElementById('search').value = ''; render(); };
      bar.appendChild(b);
    }
    const clr = document.createElement('button'); clr.className = 'clear'; clr.textContent = '全部清除';
    clr.onclick = () => { for (const d of Object.keys(F)) F[d].clear(); q = ''; document.getElementById('search').value = ''; syncTabs(); render(); };
    bar.appendChild(clr);
  }

  // ---- list ----
  let selected = null;
  function badgeHtml(p, withContentMark) {
    const b = [];
    b.push(`<span class="badge ${p.company === 'openai' ? 'oai' : 'ant'}">${COMPANY_LABEL[p.company]}</span>`);
    b.push(`<span class="badge src">${SRC_LABEL[p.source]}</span>`);
    if (p.category) b.push(`<span class="badge">${p.category}</span>`);
    if (p.frequency) b.push(`<span class="badge freq-${p.frequency}">${p.frequency}</span>`);
    if (p.difficulty) b.push(`<span class="badge diff-${p.difficulty}">${p.difficulty}</span>`);
    if (withContentMark) {
      if (p.content && p.content.length > 100) b.push('<span class="badge unlock">✓ 正文</span>');
      else b.push('<span class="badge lock">🔒 链接</span>');
    }
    if (p.last_asked) b.push(`<span class="badge">${p.last_asked}</span>`);
    return b.join('');
  }
  function renderList() {
    const list = document.getElementById('list'); list.innerHTML = '';
    const rows = P.filter(match).sort((a, b) => {
      const ca = (a.content && a.content.length > 100) ? 0 : 1, cb = (b.content && b.content.length > 100) ? 0 : 1;
      const fa = FREQ_ORDER[a.frequency] ?? 5, fb = FREQ_ORDER[b.frequency] ?? 5;
      return ca - cb || fa - fb || (b.last_asked || '').localeCompare(a.last_asked || '');
    });
    document.getElementById('count').textContent = rows.length + ' / ' + P.length + ' 题';
    for (const p of rows) {
      const r = document.createElement('div');
      r.className = 'row' + (selected === p.pid ? ' sel' : '');
      r.innerHTML = `<div class="t">${esc(p.title)}</div><div class="meta">${badgeHtml(p, true)}</div>`;
      r.onclick = () => { selected = p.pid; renderDetail(p); renderList();
        document.getElementById('app').classList.add('showdetail'); };
      list.appendChild(r);
    }
  }

  function renderDetail(p) {
    const d = document.getElementById('detail');
    const badges = [badgeHtml(p, false)];
    if (p.duration) badges.push(`<span class="badge">${p.duration} min</span>`);
    if (p.last_asked) badges.push(`<span class="badge">最近考 ${p.last_asked}</span>`);
    p.roles.forEach(r => badges.push(`<span class="badge">${r}</span>`));
    p.stages.forEach(x => badges.push(`<span class="badge">${x}</span>`));
    p.tags.forEach(t => badges.push(`<span class="badge">#${t}</span>`));

    const links = [];
    if (p.url) links.push(`<a class="btn" href="${p.url}" target="_blank">↗ 原帖 / 站内看题</a>`);
    const uq = p.tid || (p.url || '');
    if (uq) links.push(`<button class="btn primary" data-url="${p.url || ''}" data-tid="${p.tid || ''}">🔓 用解锁工具打开</button>`);
    (p.sources || []).forEach(s => { if (s.url) links.push(`<a class="btn" href="${s.url}" target="_blank">来源: ${esc((s.title || 'link').slice(0, 20))}</a>`); });

    let bodyHtml;
    if (p.content && p.content.length > 20) {
      bodyHtml = `<div class="md">${marked.parse(p.content)}</div>`;
    } else {
      const parts = [];
      if (p.overview) parts.push(`<div class="ovbox"><div class="ovlabel">题目概要（会员摘要）</div>${esc(p.overview)}</div>`);
      // embedded unlocked thread content (real 面经原文)
      if (p.threads && p.threads.length) {
        parts.push(`<div class="xref"><h3>📄 已解锁的相关帖子正文（${p.threads.length}）</h3></div>`);
        p.threads.forEach((th, i) => {
          parts.push(`<details class="thread" ${i === 0 ? 'open' : ''}>
            <summary>${esc(th.title || ('帖子 ' + th.tid))} <a href="${th.url}" target="_blank" onclick="event.stopPropagation()">↗原帖</a></summary>
            <div class="md">${marked.parse(th.md)}</div></details>`);
        });
      }
      // cross-reference resources
      if (p.refs && p.refs.length) {
        const items = p.refs.map(r =>
          `<li><span class="rkind">${esc(r.kind)}</span> <a href="${r.url}" target="_blank">${esc(r.title)}</a></li>`).join('');
        parts.push(`<div class="xref"><h3>🔗 相关资源（可用第三方解析）</h3><ul class="reflist">${items}</ul></div>`);
      }
      if (p.notes && p.notes.length) {
        parts.push(`<div class="xref"><h3>📓 本地笔记覆盖</h3><ul class="reflist">${p.notes.map(n => `<li>${esc(n)}（见 my_interview_prep）</li>`).join('')}</ul></div>`);
      }
      if (p.related && p.related.length) {
        const rel = p.related.map(r => `<li><a href="https://www.1point3acres.com/interview/problems/company/${p.company}/${r.slug}" target="_blank">${esc(r.title)}</a></li>`).join('');
        parts.push(`<div class="xref"><h3>🧩 站内关联题</h3><ul class="reflist">${rel}</ul></div>`);
      }
      const hasContent = (p.threads && p.threads.length) || p.overview;
      parts.push(`<div class="locknote">${hasContent ? '本题官方编辑正文在会员区（无独立原帖），上面已给出概要 + 已解锁的相关帖子原文 + 可解析资源。' : '正文在一亩三分地会员区，无独立原帖，本地未匹配到相关资源。'}
        点顶部 <b>原帖 / 站内看题</b> 登录后可看官方完整版。</div>`);
      bodyHtml = parts.join('');
    }
    d.innerHTML = `<h1 class="dt">${esc(p.title)}</h1><div class="dmeta">${badges.join('')}</div>
      <div class="links">${links.join('')}</div>${bodyHtml}`;

    d.querySelectorAll('[data-url]').forEach(btn => {
      btn.onclick = () => {
        const tid = btn.getAttribute('data-tid');
        const url = btn.getAttribute('data-url') || (tid ? 'https://www.1point3acres.com/interview/thread/' + tid : '');
        copy(url); window.open(TOOL, '_blank'); toast('链接已复制，粘贴到工具搜索框');
      };
    });
    d.querySelectorAll('pre code').forEach(b => { try { hljs.highlightElement(b); } catch (e) {} });
    d.scrollTop = 0;
  }

  function esc(s) { return (s == null ? '' : String(s)).replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c])); }
  function copy(t) { try { navigator.clipboard.writeText(t); } catch (e) {
    const ta = document.createElement('textarea'); ta.value = t; document.body.appendChild(ta); ta.select();
    try { document.execCommand('copy'); } catch (e2) {} ta.remove(); } }
  let toastTimer;
  function toast(msg) { const t = document.getElementById('toast'); t.textContent = msg; t.classList.add('show');
    clearTimeout(toastTimer); toastTimer = setTimeout(() => t.classList.remove('show'), 2200); }

  function syncTabs() {
    // tab reflects company set: all=empty, else single-company sets highlight
    document.querySelectorAll('.tab').forEach(t => {
      const c = t.dataset.c;
      const active = c === 'all' ? F.company.size === 0
        : (F.company.size === 1 && F.company.has(c));
      t.classList.toggle('active', active);
    });
  }

  function render() { renderSidebar(); renderActiveBar(); renderList(); }

  // company tabs = shortcut that sets the company filter dimension
  document.getElementById('tabs').onclick = (e) => {
    const b = e.target.closest('.tab'); if (!b) return;
    F.company.clear();
    if (b.dataset.c !== 'all') F.company.add(b.dataset.c);
    syncTabs(); render();
  };
  document.getElementById('search').oninput = (e) => { q = e.target.value.trim(); renderActiveBar(); renderList(); };

  marked.setOptions({ breaks: false, gfm: true });
  render();
})();
