const MATERIALS_FILE = "./data/local_materials.json";

const state = {
  materials: [],
  filtered: [],
  metadata: {},
  generatedAt: "",
  query: "",
  company: "",
  kind: "",
  relatedOnly: false,
  page: 1,
  pageSize: 50,
};

const dom = {
  status: document.querySelector("#materials-status"),
  files: document.querySelector("#material-stat-files"),
  units: document.querySelector("#material-stat-units"),
  forum: document.querySelector("#material-stat-forum"),
  relatedStat: document.querySelector("#material-stat-related"),
  search: document.querySelector("#materials-search"),
  company: document.querySelector("#materials-company"),
  kind: document.querySelector("#materials-kind"),
  related: document.querySelector("#materials-related"),
  pageSize: document.querySelector("#materials-page-size"),
  count: document.querySelector("#materials-count"),
  table: document.querySelector("#material-table"),
  pagination: document.querySelector("#materials-pagination"),
  pages: document.querySelector("#materials-pages"),
  prev: document.querySelector("#materials-prev"),
  next: document.querySelector("#materials-next"),
  generated: document.querySelector("#materials-generated"),
  theme: document.querySelector("#materials-theme"),
  dialog: document.querySelector("#material-dialog"),
  detailClose: document.querySelector("#material-detail-close"),
  detailKind: document.querySelector("#material-detail-kind"),
  detailCompany: document.querySelector("#material-detail-company"),
  detailTitle: document.querySelector("#material-detail-title"),
  detailSummary: document.querySelector("#material-detail-summary"),
  detailFiles: document.querySelector("#material-detail-files"),
  detailRelated: document.querySelector("#material-detail-related"),
  relatedSection: document.querySelector("#material-related-section"),
  detailContent: document.querySelector("#material-detail-content"),
};

function companyLabel(value) {
  return { openai: "OpenAI", anthropic: "Anthropic", gdm: "Google DeepMind", all: "通用" }[value] || value;
}

function searchable(material) {
  return [
    material.title,
    material.summary,
    material.content,
    material.kind,
    material.company,
    ...(material.tags || []),
    ...(material.sourceFiles || []),
    ...(material.relatedQuestions || []).map((question) => question.title),
  ].join("\n").toLocaleLowerCase("zh-CN");
}

function option(select, value, label, count) {
  const node = document.createElement("option");
  node.value = value;
  node.textContent = `${label}（${count}）`;
  select.append(node);
}

function populateFilters() {
  const companyCounts = new Map();
  const kindCounts = new Map();
  state.materials.forEach((material) => {
    companyCounts.set(material.company, (companyCounts.get(material.company) || 0) + 1);
    kindCounts.set(material.kind, (kindCounts.get(material.kind) || 0) + 1);
  });
  [...companyCounts.entries()]
    .sort((left, right) => right[1] - left[1])
    .forEach(([value, count]) => option(dom.company, value, companyLabel(value), count));
  [...kindCounts.entries()]
    .sort((left, right) => right[1] - left[1] || left[0].localeCompare(right[0], "zh-CN"))
    .forEach(([value, count]) => option(dom.kind, value, value, count));
}

function pageItems(current, total) {
  if (total <= 7) return Array.from({ length: total }, (_, index) => index + 1);
  const values = new Set([1, total, current - 1, current, current + 1]);
  if (current <= 4) [2, 3, 4, 5].forEach((page) => values.add(page));
  if (current >= total - 3) [total - 4, total - 3, total - 2, total - 1].forEach((page) => values.add(page));
  const pages = [...values].filter((page) => page >= 1 && page <= total).sort((a, b) => a - b);
  const output = [];
  pages.forEach((page, index) => {
    if (index && page - pages[index - 1] > 1) output.push("ellipsis");
    output.push(page);
  });
  return output;
}

function renderPagination(totalPages) {
  dom.pagination.hidden = state.filtered.length === 0;
  dom.prev.disabled = state.page <= 1;
  dom.next.disabled = state.page >= totalPages;
  dom.pages.replaceChildren();
  pageItems(state.page, totalPages).forEach((item) => {
    if (item === "ellipsis") {
      const ellipsis = document.createElement("span");
      ellipsis.className = "pagination-ellipsis";
      ellipsis.textContent = "…";
      dom.pages.append(ellipsis);
      return;
    }
    const button = document.createElement("button");
    button.type = "button";
    button.className = `pagination-page${item === state.page ? " active" : ""}`;
    button.dataset.page = item;
    button.textContent = item;
    button.setAttribute("aria-label", `第 ${item} 页`);
    if (item === state.page) button.setAttribute("aria-current", "page");
    dom.pages.append(button);
  });
}

function createPill(text, className) {
  const pill = document.createElement("span");
  pill.className = className;
  pill.textContent = text;
  pill.title = text;
  return pill;
}

function createMaterialRow(material, position) {
  const row = document.createElement("article");
  row.className = "question-card material-row";

  const number = document.createElement("span");
  number.className = "row-number";
  number.textContent = String(position).padStart(2, "0");

  const main = document.createElement("div");
  main.className = "row-main";
  const titleLine = document.createElement("div");
  titleLine.className = "row-title-line";
  titleLine.append(createPill(companyLabel(material.company), `company-pill ${material.company}`));
  const heading = document.createElement("h3");
  const button = document.createElement("button");
  button.type = "button";
  button.className = "card-title-button";
  button.textContent = material.title;
  button.addEventListener("click", () => openMaterial(material));
  heading.append(button);
  const summary = document.createElement("p");
  summary.className = "card-summary";
  summary.textContent = material.summary || "这条阅读单元没有单独摘要，请打开查看本地内容。";
  main.append(titleLine, heading, summary);

  const taxonomy = document.createElement("div");
  taxonomy.className = "row-taxonomy";
  const tags = document.createElement("div");
  tags.className = "card-tags";
  (material.tags || []).slice(0, 4).forEach((tag) => tags.append(createPill(tag, "tag-pill")));
  taxonomy.append(tags);
  const kind = document.createElement("span");
  kind.className = "row-stage";
  kind.textContent = material.kind;
  taxonomy.append(kind);

  const meta = document.createElement("div");
  meta.className = "row-meta";
  const line = material.lineStart ? `第 ${material.lineStart}${material.lineEnd ? `–${material.lineEnd}` : ""} 行` : "整份文件/题包";
  [`${material.sourceFiles.length} 个源文件`, line, `${material.relatedQuestions.length} 道关联题`].forEach((value) => {
    const node = document.createElement("span");
    node.textContent = value;
    meta.append(node);
  });

  const actions = document.createElement("div");
  actions.className = "row-actions material-row-actions";
  const open = document.createElement("button");
  open.type = "button";
  open.className = "row-open-button";
  open.textContent = "查看资料";
  open.addEventListener("click", () => openMaterial(material));
  actions.append(open);

  row.append(number, main, taxonomy, meta, actions);
  row.addEventListener("click", (event) => {
    if (!event.target.closest("button, a")) openMaterial(material);
  });
  return row;
}

function render() {
  const queryTokens = state.query.toLocaleLowerCase("zh-CN").split(/\s+/).filter(Boolean);
  state.filtered = state.materials.filter((material) => {
    if (state.company && material.company !== state.company) return false;
    if (state.kind && material.kind !== state.kind) return false;
    if (state.relatedOnly && !material.relatedQuestions.length) return false;
    return queryTokens.every((token) => material._search.includes(token));
  });

  const totalPages = Math.max(1, Math.ceil(state.filtered.length / state.pageSize));
  state.page = Math.min(Math.max(1, state.page), totalPages);
  const start = (state.page - 1) * state.pageSize;
  const end = Math.min(start + state.pageSize, state.filtered.length);
  dom.table.replaceChildren();
  state.filtered.slice(start, end).forEach((material, index) => {
    dom.table.append(createMaterialRow(material, start + index + 1));
  });
  if (!state.filtered.length) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    const copy = document.createElement("div");
    copy.className = "empty-state-inner";
    copy.innerHTML = "<h3>没有匹配的本地资料</h3><p>请缩短搜索词或移除一个筛选条件。</p>";
    empty.append(copy);
    dom.table.append(empty);
  }
  dom.count.textContent = state.filtered.length
    ? `第 ${start + 1}–${end} 条 · 共 ${state.filtered.length} 个阅读单元`
    : "0 个阅读单元";
  renderPagination(totalPages);
}

function goToPage(page) {
  const total = Math.max(1, Math.ceil(state.filtered.length / state.pageSize));
  state.page = Math.min(Math.max(1, Number(page) || 1), total);
  render();
  document.querySelector(".materials-panel")?.scrollIntoView({ behavior: "smooth", block: "start" });
}

function prepUrl(path) {
  return `./prep/${path.split("/").map(encodeURIComponent).join("/")}`;
}

function openMaterial(material) {
  dom.detailKind.textContent = material.kind;
  dom.detailCompany.textContent = companyLabel(material.company);
  dom.detailTitle.textContent = material.title;
  dom.detailSummary.textContent = material.summary || "无单独摘要";
  dom.detailContent.textContent = material.content || "当前索引只记录了文件信息；请打开源文件查看完整内容。";
  dom.detailFiles.replaceChildren();
  material.sourceFiles.forEach((path, index) => {
    const row = document.createElement("div");
    row.className = "material-file-row";
    const link = document.createElement("a");
    link.href = prepUrl(path);
    link.target = "_blank";
    link.rel = "noreferrer noopener";
    link.textContent = path;
    const copy = document.createElement("button");
    copy.type = "button";
    copy.textContent = "复制路径";
    copy.addEventListener("click", async () => {
      const absolutePath = material.absoluteSourcePaths[index];
      try {
        await navigator.clipboard.writeText(absolutePath);
        copy.textContent = "已复制 ✓";
        window.setTimeout(() => { copy.textContent = "复制路径"; }, 1300);
      } catch (_) {
        window.prompt("复制本地路径：", absolutePath);
      }
    });
    row.append(link, copy);
    dom.detailFiles.append(row);
  });
  if (material.sourceUrl) {
    const external = document.createElement("a");
    external.className = "material-external-link";
    external.href = material.sourceUrl;
    external.target = "_blank";
    external.rel = "noreferrer noopener";
    external.textContent = "打开原始网页 ↗";
    dom.detailFiles.append(external);
  }

  dom.detailRelated.replaceChildren();
  dom.relatedSection.hidden = material.relatedQuestions.length === 0;
  material.relatedQuestions.forEach((question) => {
    const link = document.createElement("a");
    link.href = `./#q=${encodeURIComponent(`${question.company}:${question.id}`)}`;
    link.textContent = `${companyLabel(question.company)} · ${question.title}`;
    const score = document.createElement("small");
    score.textContent = `自动匹配 ${Math.round(question.score * 100)}%`;
    link.append(score);
    dom.detailRelated.append(link);
  });
  if (typeof dom.dialog.showModal === "function") dom.dialog.showModal();
  else dom.dialog.setAttribute("open", "");
}

function setTheme(theme) {
  document.documentElement.dataset.theme = theme;
  try { localStorage.setItem("acre3points:theme:v1", theme); } catch (_) { /* optional */ }
}

async function load() {
  try {
    const response = await fetch(MATERIALS_FILE, { cache: "no-store" });
    if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
    const payload = await response.json();
    state.metadata = payload.metadata || {};
    state.generatedAt = payload.generatedAt || "";
    state.materials = (payload.materials || []).map((material) => ({ ...material, _search: searchable(material) }));
    dom.status.textContent = `${state.metadata.indexedPhysicalFiles}/${state.metadata.physicalFiles} 个文件已索引`;
    dom.files.textContent = state.metadata.physicalFiles?.toLocaleString("zh-CN") || "0";
    dom.units.textContent = state.metadata.logicalMaterials?.toLocaleString("zh-CN") || "0";
    dom.forum.textContent = (state.metadata.byKind?.["一亩三分地本地原帖"] || 0).toLocaleString("zh-CN");
    dom.relatedStat.textContent = (state.metadata.questionsWithRelatedMaterials || 0).toLocaleString("zh-CN");
    dom.generated.textContent = `更新时间：${state.generatedAt ? new Date(state.generatedAt).toLocaleString("zh-CN") : "—"}`;
    populateFilters();
    render();
    const requestedMaterial = new URL(window.location.href).searchParams.get("material");
    if (requestedMaterial) {
      const material = state.materials.find((entry) => entry.id === requestedMaterial);
      if (material) openMaterial(material);
    }
  } catch (error) {
    dom.status.textContent = "资料索引读取失败";
    dom.count.textContent = `读取失败：${error instanceof Error ? error.message : String(error)}`;
  }
}

dom.search.addEventListener("input", () => { state.query = dom.search.value.trim(); state.page = 1; render(); });
dom.company.addEventListener("change", () => { state.company = dom.company.value; state.page = 1; render(); });
dom.kind.addEventListener("change", () => { state.kind = dom.kind.value; state.page = 1; render(); });
dom.related.addEventListener("change", () => { state.relatedOnly = dom.related.checked; state.page = 1; render(); });
dom.pageSize.addEventListener("change", () => { state.pageSize = Number(dom.pageSize.value) || 50; state.page = 1; render(); });
dom.prev.addEventListener("click", () => goToPage(state.page - 1));
dom.next.addEventListener("click", () => goToPage(state.page + 1));
dom.pages.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-page]");
  if (button) goToPage(button.dataset.page);
});
dom.theme.addEventListener("click", () => setTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark"));
dom.detailClose.addEventListener("click", () => dom.dialog.close());
dom.dialog.addEventListener("click", (event) => { if (event.target === dom.dialog) dom.dialog.close(); });

load();
