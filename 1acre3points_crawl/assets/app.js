const DATA_FILES = [
  { path: "./data/questions.json", origin: "用户资料" },
  { path: "./data/supplemental.json", origin: "补充研究" },
];
const SOURCES_FILE = "./data/sources.json";
const LOCAL_MATERIALS_FILE = "./data/local_material_links.json";
const MEMBER_AUDIT_FILE = "./data/member_content_audit.json";
const DEFAULT_PAGE_SIZE = 25;
const PAGE_SIZE_OPTIONS = new Set([25, 50, 100]);
const USER_PROVIDED_THREAD_VIEWER_URL = "http://117.72.46.162/?code=AGI30S2Z8GX1Y2J7PMER";
const LOCAL_PREP_ROOT = "/Users/mingrui/Documents/codes/interview/my_interview_prep/";

const STORAGE = {
  favorites: "acre3points:favorites:v1",
  completed: "acre3points:completed:v1",
  imported: "acre3points:imported-data:v1",
  importedAt: "acre3points:imported-at:v1",
  theme: "acre3points:theme:v1",
  pageSize: "acre3points:page-size:v1",
};

const DEFAULT_SOURCES = [
  {
    name: "OpenAI 官方题库页",
    url: "https://www.1point3acres.com/interview/problems/company/openai",
  },
  {
    name: "Anthropic 官方题库页",
    url: "https://www.1point3acres.com/interview/problems/company/anthropic",
  },
];

const CATEGORY_LABELS = {
  process: "面试流程",
  coding: "编程",
  oj: "编程",
  algorithm: "编程",
  algorithms: "编程",
  "ml-coding": "ML 编程",
  mlcoding: "ML 编程",
  "ml-theory": "ML 理论",
  mltheory: "ML 理论",
  theory: "ML 理论",
  "system-design": "系统设计",
  systemdesign: "系统设计",
  "ml-system-design": "ML 系统设计",
  mlsystemdesign: "ML 系统设计",
  behavioral: "行为 / 文化",
  behaviour: "行为 / 文化",
  culture: "行为 / 文化",
  other: "其他",
  unknown: "未分类",
};

const ROLE_LABELS = {
  "all-roles": "全部岗位",
  allroles: "全部岗位",
  swe: "软件工程师",
  softwareengineer: "软件工程师",
  "software-engineer": "软件工程师",
  mle: "机器学习工程师",
  mlengineer: "机器学习工程师",
  "ml-engineer": "机器学习工程师",
  researchengineer: "Research Engineer",
  "research-engineer": "Research Engineer",
  re: "Research Engineer",
  researchscientist: "Research Scientist",
  "research-scientist": "Research Scientist",
  rs: "Research Scientist",
  appliedengineer: "Applied Engineer",
  "applied-engineer": "Applied Engineer",
  manager: "管理岗",
  internship: "实习",
  intern: "实习",
};

const ACCESS_LABELS = {
  public: "公开内容",
  summary: "摘要 / 预览",
  locked: "登录 / 会员",
  external: "来源链接",
  unknown: "状态未知",
};

const PROGRESS_LABELS = {
  favorite: "只看收藏",
  completed: "已经完成",
  pending: "尚未完成",
};

const DIFFICULTY_LABELS = {
  easy: "简单",
  medium: "中等",
  hard: "困难",
  unknown: "未知",
};

const state = {
  questions: [],
  filtered: [],
  payloads: [],
  metadata: {},
  sources: DEFAULT_SOURCES,
  favorites: loadStoredSet(STORAGE.favorites),
  completed: loadStoredSet(STORAGE.completed),
  filters: {
    company: new Set(),
    category: new Set(),
    role: new Set(),
    tag: new Set(),
    access: new Set(),
    progress: new Set(),
  },
  query: "",
  sort: "relevance",
  currentPage: 1,
  pageSize: loadStoredPageSize(),
  tagQuery: "",
  showAllTags: false,
  activeQuestion: null,
  loading: true,
  loadFailures: [],
  localMaterialsPromise: null,
  memberAudit: null,
};

const dom = {
  snapshotBadge: document.querySelector("#snapshot-badge"),
  snapshotLabel: document.querySelector("#snapshot-label"),
  snapshotDate: document.querySelector("#snapshot-date"),
  statTotal: document.querySelector("#stat-total"),
  statCompanies: document.querySelector("#stat-companies"),
  statFavorites: document.querySelector("#stat-favorites"),
  statCompleted: document.querySelector("#stat-completed"),
  favoriteCount: document.querySelector("#favorite-count"),
  completedCount: document.querySelector("#completed-count"),
  pendingCount: document.querySelector("#pending-count"),
  companyOptions: document.querySelector("#company-options"),
  categoryOptions: document.querySelector("#category-options"),
  roleOptions: document.querySelector("#role-options"),
  tagOptions: document.querySelector("#tag-options"),
  accessOptions: document.querySelector("#access-options"),
  filtersPanel: document.querySelector("#filters-panel"),
  filtersOpen: document.querySelector("#filters-open"),
  filtersClose: document.querySelector("#filters-close"),
  filterOverlay: document.querySelector("#filter-overlay"),
  resetFilters: document.querySelector("#reset-filters"),
  mobileFilterCount: document.querySelector("#mobile-filter-count"),
  tagSearch: document.querySelector("#tag-search"),
  showAllTags: document.querySelector("#show-all-tags"),
  mainSearch: document.querySelector("#main-search"),
  clearSearch: document.querySelector("#clear-search"),
  sortSelect: document.querySelector("#sort-select"),
  activeFilters: document.querySelector("#active-filters"),
  resultCount: document.querySelector("#result-count"),
  resultsHeading: document.querySelector("#results-heading"),
  notice: document.querySelector("#notice"),
  grid: document.querySelector("#question-grid"),
  pagination: document.querySelector("#pagination"),
  pageNumbers: document.querySelector("#page-numbers"),
  pagePrev: document.querySelector("#page-prev"),
  pageNext: document.querySelector("#page-next"),
  pageSize: document.querySelector("#page-size"),
  themeToggle: document.querySelector("#theme-toggle"),
  dialog: document.querySelector("#question-dialog"),
  detailClose: document.querySelector("#detail-close"),
  detailCompany: document.querySelector("#detail-company"),
  detailAccess: document.querySelector("#detail-access"),
  detailTitle: document.querySelector("#detail-title"),
  detailFavorite: document.querySelector("#detail-favorite"),
  detailComplete: document.querySelector("#detail-complete"),
  detailTags: document.querySelector("#detail-tags"),
  detailMeta: document.querySelector("#detail-meta"),
  detailContent: document.querySelector("#detail-content"),
  importData: document.querySelector("#import-data"),
  headerImport: document.querySelector("#header-import"),
  importFile: document.querySelector("#import-file"),
  importStatus: document.querySelector("#import-status"),
  clearImported: document.querySelector("#clear-imported"),
  officialLinks: document.querySelector("#official-links"),
};

function loadStoredSet(key) {
  try {
    const value = JSON.parse(localStorage.getItem(key) || "[]");
    return new Set(Array.isArray(value) ? value.map(String) : []);
  } catch (_) {
    return new Set();
  }
}

function loadStoredPageSize() {
  try {
    const value = Number(localStorage.getItem(STORAGE.pageSize));
    return PAGE_SIZE_OPTIONS.has(value) ? value : DEFAULT_PAGE_SIZE;
  } catch (_) {
    return DEFAULT_PAGE_SIZE;
  }
}

function saveStoredSet(key, values) {
  try {
    localStorage.setItem(key, JSON.stringify([...values]));
  } catch (_) {
    showNotice("浏览器无法保存学习状态；请检查隐私模式或存储空间。", "error");
  }
}

function pick(object, ...keys) {
  for (const key of keys) {
    if (object && object[key] !== undefined && object[key] !== null && object[key] !== "") {
      return object[key];
    }
  }
  return null;
}

function rawList(value) {
  if (value === null || value === undefined || value === "") return [];
  return Array.isArray(value) ? value : [value];
}

function plainText(value) {
  if (value === null || value === undefined) return "";
  if (Array.isArray(value)) return value.map(plainText).filter(Boolean).join("\n");
  if (typeof value === "object") {
    if (value.name || value.label || value.title) {
      return plainText(value.name || value.label || value.title);
    }
    try {
      return JSON.stringify(value, null, 2);
    } catch (_) {
      return String(value);
    }
  }

  const text = String(value).trim();
  if (!text) return "";
  if (/<(?:p|div|br|li|ul|ol|strong|em|code|pre|h[1-6])(?:\s|>)/i.test(text)) {
    try {
      return new DOMParser().parseFromString(text, "text/html").body.textContent.trim();
    } catch (_) {
      return text;
    }
  }
  return text;
}

function splitLabels(value) {
  const items = rawList(value).flatMap((item) => {
    if (item && typeof item === "object") {
      return [plainText(item.name || item.label || item.title || item.value)];
    }
    const text = plainText(item);
    if (!text) return [];
    if (/[,，;；|]/.test(text)) return text.split(/[,，;；|]/).map((part) => part.trim());
    return [text];
  });
  return [...new Set(items.filter(Boolean))];
}

function canonicalKey(value) {
  return plainText(value)
    .toLowerCase()
    .trim()
    .replace(/[\s_]+/g, "-")
    .replace(/[^\p{L}\p{N}-]+/gu, "")
    .replace(/-+/g, "-");
}

function humanize(value) {
  const text = plainText(value).replace(/[_-]+/g, " ").replace(/\s+/g, " ").trim();
  if (!text) return "";
  if (/^[a-z\d ]+$/i.test(text)) {
    return text
      .split(" ")
      .map((word) => {
        const lower = word.toLowerCase();
        if (["ai", "ml", "rl", "llm", "gpu", "api", "sql", "oa", "bq", "nlp"].includes(lower)) {
          return lower.toUpperCase();
        }
        return word.charAt(0).toUpperCase() + word.slice(1);
      })
      .join(" ");
  }
  return text;
}

function companyLabel(value) {
  const raw = plainText(value);
  const key = canonicalKey(raw);
  if (key.includes("openai") || key === "open-ai") return "OpenAI";
  if (key.includes("anthropic")) return "Anthropic";
  return humanize(raw) || "未知公司";
}

function categoryLabel(value) {
  const raw = plainText(value) || "unknown";
  const key = canonicalKey(raw);
  const compact = key.replace(/-/g, "");
  return CATEGORY_LABELS[key] || CATEGORY_LABELS[compact] || humanize(raw) || "未分类";
}

function roleLabel(value) {
  const raw = plainText(value);
  const key = canonicalKey(raw);
  const compact = key.replace(/-/g, "");
  return ROLE_LABELS[key] || ROLE_LABELS[compact] || humanize(raw);
}

function difficultyLabel(value) {
  const raw = plainText(value);
  const key = canonicalKey(raw);
  if (!raw || ["0", "unknown", "n-a", "na", "none", "null"].includes(key)) return "";
  return DIFFICULTY_LABELS[key] || humanize(raw);
}

function contentPreview(value, limit = 280) {
  const preview = String(value || "")
    .replace(/^\s*`{3,}[^\n]*\n[\s\S]*?^\s*`{3,}\s*$/gm, " ")
    .replace(/^\s*`{3,}[^\n]*$/gm, " ")
    .replace(/^\s*#{1,6}\s+/gm, "")
    .replace(/^\s*>\s?/gm, "")
    .replace(/^\s*(?:[-*+]\s+|\d+[.)]\s+)/gm, "")
    .replace(/\*\*([^*\n]+)\*\*/g, "$1")
    .replace(/`([^`\n]+)`/g, "$1")
    .replace(/\s+/g, " ")
    .trim();
  if (preview.length <= limit) return preview;
  return `${preview.slice(0, limit).trimEnd()}…`;
}

function frequencyLabel(value) {
  const raw = plainText(value);
  const key = canonicalKey(raw);
  if (!raw || key === "unknown") return "";
  if (["very-high", "veryhigh", "highest"].includes(key)) return "极高频";
  if (key === "high") return "高频";
  if (["medium", "moderate"].includes(key)) return "中频";
  if (key === "low") return "低频";
  return raw;
}

function accessInfo(question) {
  const explicit = plainText(
    pick(question, "access", "accessStatus", "access_status", "visibility", "availability")
  ).toLowerCase();

  const isLocked = pick(question, "isLocked", "is_locked", "locked");
  const isPublic = pick(question, "isPublic", "is_public", "public");
  const candidates = `${explicit} ${plainText(pick(question, "sourceType", "source_type"))}`;

  let code = "unknown";
  if (isLocked === true || /locked|member|login|paywall|会员|登录|付费/.test(candidates)) {
    code = "locked";
  } else if (/summary|preview|overview|摘要|预览/.test(candidates)) {
    code = "summary";
  } else if (/external|third.party|link.only|supplemental.research|来源链接|外部|第三方/.test(candidates)) {
    code = "external";
  } else if (isPublic === true || /public|full|open|公开|全文/.test(candidates)) {
    code = "public";
  }
  return { code, label: ACCESS_LABELS[code] };
}

function normalizeSources(question) {
  const sources = [];
  const candidateLists = [
    pick(question, "sources", "references", "sourceLinks", "source_links"),
    pick(question, "sourceUrls", "source_urls", "contentSourceUrls", "content_source_urls"),
    pick(question, "source", "reference"),
  ];

  for (const candidateList of candidateLists) {
    for (const entry of rawList(candidateList)) {
      if (!entry) continue;
      if (typeof entry === "string") {
        const possibleUrl = entry.trim();
        if (/^https?:\/\//i.test(possibleUrl)) {
          sources.push({ url: possibleUrl, title: "原始来源", relationship: "", confidence: "", note: "" });
        }
      } else if (typeof entry === "object") {
        const url = plainText(pick(entry, "url", "href", "link", "sourceUrl", "source_url"));
        if (url) {
          sources.push({
            url,
            title: plainText(pick(entry, "title", "name", "label", "sourceTitle", "source_title")) ||
              "原始来源",
            relationship: plainText(pick(entry, "relationship", "relation", "matchType", "match_type")),
            confidence: plainText(pick(entry, "confidence", "matchConfidence", "match_confidence")),
            note: plainText(pick(entry, "note", "matchNote", "match_note", "description")),
          });
        }
      }
    }
  }

  const directUrl = plainText(
    pick(question, "sourceUrl", "source_url", "originalUrl", "original_url", "url", "link")
  );
  if (directUrl) {
    sources.push({
      url: directUrl,
      title: plainText(pick(question, "sourceTitle", "source_title")) || "原始来源",
      relationship: "official-entry",
      confidence: "high",
      note: "",
    });
  }

  const normalized = new Map();
  sources.forEach((source) => {
    const url = safeExternalUrl(source.url);
    if (!url) return;
    const candidate = { ...source, url };
    const existing = normalized.get(url);
    if (!existing) {
      normalized.set(url, candidate);
      return;
    }
    if ((!existing.title || existing.title === "原始来源") && candidate.title) {
      existing.title = candidate.title;
    }
    for (const key of ["relationship", "confidence", "note"]) {
      if (!existing[key] && candidate[key]) existing[key] = candidate[key];
    }
  });
  return [...normalized.values()];
}

function safeExternalUrl(value) {
  try {
    const raw = String(value);
    const localPath = raw.startsWith(LOCAL_PREP_ROOT)
      ? `./prep/${raw.slice(LOCAL_PREP_ROOT.length).split("/").map(encodeURIComponent).join("/")}`
      : raw;
    const url = new URL(localPath, window.location.href);
    return ["http:", "https:"].includes(url.protocol) ? url.href : "";
  } catch (_) {
    return "";
  }
}

function stableHash(input) {
  let hash = 2166136261;
  for (let index = 0; index < input.length; index += 1) {
    hash ^= input.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return (hash >>> 0).toString(36);
}

function dateScore(value) {
  const text = plainText(value);
  const matches = text.match(/\d{4}[-/.]\d{1,2}(?:[-/.]\d{1,2})?/g) || [];
  let max = 0;
  for (const match of matches) {
    const parsed = Date.parse(match.replace(/[/.]/g, "-"));
    if (Number.isFinite(parsed)) max = Math.max(max, parsed);
  }
  if (!max) {
    const parsed = Date.parse(text);
    if (Number.isFinite(parsed)) max = parsed;
  }
  return max;
}

function frequencyScore(value, sourceCount = 0) {
  const text = plainText(value).toLowerCase();
  if (/very.high|极高|最高/.test(text)) return 500 + sourceCount;
  if (/high|高频|\b高\b/.test(text)) return 400 + sourceCount;
  if (/medium|moderate|中频|\b中\b/.test(text)) return 300 + sourceCount;
  if (/low|低频|\b低\b/.test(text)) return 200 + sourceCount;
  const number = Number.parseFloat(text.match(/\d+(?:\.\d+)?/)?.[0] || "0");
  return number * 10 + sourceCount;
}

function normalizeQuestion(rawQuestion, origin, index) {
  const question = rawQuestion && typeof rawQuestion === "object" ? rawQuestion : { title: rawQuestion };
  const company = companyLabel(pick(question, "company", "companyName", "company_name", "organization"));
  const rawTitle = plainText(pick(question, "title", "name", "questionTitle", "question_title"));
  const slug = plainText(pick(question, "slug", "key"));
  const title = rawTitle || humanize(slug) || `未命名条目 ${index + 1}`;
  const category = categoryLabel(pick(question, "category", "type", "questionType", "question_type"));
  const roles = splitLabels(pick(question, "roles", "role", "positions", "jobRoles", "job_roles"))
    .map(roleLabel)
    .filter(Boolean);
  const tags = [
    ...splitLabels(pick(question, "tags", "topics", "topicTags", "topic_tags")),
    ...splitLabels(pick(question, "algorithms", "skills", "concepts")),
  ]
    .map(humanize)
    .filter(Boolean);
  const stages = splitLabels(pick(question, "stages", "stage", "rounds", "round")).map(humanize);
  const summary = plainText(
    pick(question, "summary", "overview", "excerpt", "preview", "abstract", "shortDescription")
  );
  const content = plainText(
    pick(
      question,
      "content",
      "description",
      "detail",
      "problemStatement",
      "problem_statement",
      "question",
      "body"
    )
  );
  const contentKind = plainText(pick(question, "contentKind", "content_kind"));
  const contentQuality = plainText(pick(question, "contentQuality", "content_quality"));
  const contentMatch = plainText(pick(question, "contentMatch", "content_match"));
  const contentMatchConfidence = plainText(
    pick(question, "contentMatchConfidence", "content_match_confidence")
  );
  const solutionHint = plainText(
    pick(question, "solutionHint", "solution_hint", "hint", "hints", "approach", "solution")
  );
  const sourceMatchNote = plainText(
    pick(question, "sourceMatchNote", "source_match_note", "sourceNote", "source_note")
  );
  const sources = normalizeSources(question);
  const sourceCount = Number(
    pick(question, "sourceCount", "source_count", "reportCount", "report_count") || sources.length || 0
  );
  const lastAsked = plainText(
    pick(question, "lastAsked", "last_asked", "reportedTo", "reported_to", "date", "updatedAt", "updated_at")
  );
  const rawId = plainText(pick(question, "id", "questionId", "question_id", "slug"));
  const identityBasis = rawId
    ? `${company}\u241f${rawId}`
    : `${company}\u241f${title}\u241f${sources[0]?.url || ""}`;
  const id = rawId ? `${canonicalKey(company)}:${rawId}` : `local-${stableHash(identityBasis)}`;
  const access = accessInfo(question);
  const difficulty = difficultyLabel(pick(question, "difficulty", "level"));
  const frequency = frequencyLabel(pick(question, "frequency", "frequencyLabel", "frequency_label"));
  const duration = pick(question, "durationMinutes", "duration_minutes", "duration", "timeLimit", "time_limit");
  const isNew = Boolean(pick(question, "isNew", "is_new", "new"));
  const displaySummary = summary || contentPreview(content) || "当前索引只保存了元数据与来源链接。";
  const searchText = [
    title,
    company,
    category,
    roles.join(" "),
    tags.join(" "),
    stages.join(" "),
    summary,
    content,
    contentKind,
    contentQuality,
    contentMatch,
    contentMatchConfidence,
    solutionHint,
    sourceMatchNote,
    frequency,
    difficulty,
  ]
    .join("\n")
    .toLocaleLowerCase("zh-CN");

  return {
    id,
    identityKey: canonicalKey(identityBasis),
    company,
    title,
    category,
    roles: [...new Set(roles)],
    tags: [...new Set(tags)],
    stages: [...new Set(stages)],
    summary,
    displaySummary,
    content,
    contentKind,
    contentQuality,
    contentMatch,
    contentMatchConfidence,
    solutionHint,
    sourceMatchNote,
    sources,
    sourceCount: Number.isFinite(sourceCount) ? sourceCount : sources.length,
    lastAsked,
    lastAskedScore: dateScore(lastAsked),
    difficulty,
    frequency,
    frequencyScore: frequencyScore(frequency, Number.isFinite(sourceCount) ? sourceCount : 0),
    duration: plainText(duration),
    access,
    isNew,
    origins: [origin],
    searchText,
    originalIndex: index,
  };
}

function mergeQuestion(existing, incoming) {
  const preferLonger = (left, right) => (right?.length > left?.length ? right : left);
  const incomingContentPreferred = incoming.content?.length > existing.content?.length;
  const mergeObjects = (left, right, key) => {
    const byKey = new Map(left.map((item) => [item[key], item]));
    right.forEach((item) => byKey.set(item[key], item));
    return [...byKey.values()];
  };
  const merged = {
    ...existing,
    summary: preferLonger(existing.summary, incoming.summary),
    displaySummary: preferLonger(existing.displaySummary, incoming.displaySummary),
    content: preferLonger(existing.content, incoming.content),
    solutionHint: preferLonger(existing.solutionHint, incoming.solutionHint),
    sourceMatchNote: preferLonger(existing.sourceMatchNote, incoming.sourceMatchNote),
    roles: [...new Set([...existing.roles, ...incoming.roles])],
    tags: [...new Set([...existing.tags, ...incoming.tags])],
    stages: [...new Set([...existing.stages, ...incoming.stages])],
    sources: mergeObjects(existing.sources, incoming.sources, "url"),
    origins: [...new Set([...existing.origins, ...incoming.origins])],
    sourceCount: Math.max(existing.sourceCount, incoming.sourceCount),
    isNew: existing.isNew || incoming.isNew,
  };
  if (incomingContentPreferred) {
    merged.contentKind = incoming.contentKind;
    merged.contentQuality = incoming.contentQuality;
    merged.contentMatch = incoming.contentMatch;
    merged.contentMatchConfidence = incoming.contentMatchConfidence;
  }
  if (incoming.lastAskedScore > existing.lastAskedScore) {
    merged.lastAsked = incoming.lastAsked;
    merged.lastAskedScore = incoming.lastAskedScore;
  }
  if (incoming.frequencyScore > existing.frequencyScore) {
    merged.frequency = incoming.frequency;
    merged.frequencyScore = incoming.frequencyScore;
  }
  if (existing.access.code === "unknown" && incoming.access.code !== "unknown") merged.access = incoming.access;
  if (!existing.difficulty && incoming.difficulty) merged.difficulty = incoming.difficulty;
  if (!existing.duration && incoming.duration) merged.duration = incoming.duration;
  merged.searchText = [
    merged.title,
    merged.company,
    merged.category,
    ...merged.roles,
    ...merged.tags,
    ...merged.stages,
    merged.summary,
    merged.content,
    merged.solutionHint,
    merged.sourceMatchNote,
  ]
    .join("\n")
    .toLocaleLowerCase("zh-CN");
  return merged;
}

function extractRecords(payload) {
  if (Array.isArray(payload)) return payload;
  if (!payload || typeof payload !== "object") return [];
  for (const key of ["questions", "items", "problems", "entries", "records"]) {
    if (Array.isArray(payload[key])) return payload[key];
  }
  if (Array.isArray(payload.data)) return payload.data;
  if (payload.data && typeof payload.data === "object") return extractRecords(payload.data);
  return [];
}

function extractMetadata(payload) {
  if (!payload || Array.isArray(payload) || typeof payload !== "object") return {};
  const nested = payload.meta || payload.metadata || {};
  const metadata = {
    ...nested,
    generatedAt: pick(
      nested,
      "generatedAt",
      "generated_at",
      "snapshotDate",
      "snapshot_date",
      "updatedAt",
      "updated_at"
    ) ||
      pick(payload, "generatedAt", "generated_at", "snapshotDate", "snapshot_date", "updatedAt", "updated_at"),
  };
  const counts = payload.counts && typeof payload.counts === "object" ? payload.counts : {};
  [
    "recordsWithAnyContent",
    "canonicalSourceBodyRecords",
    "qbankDirectTopicContentRecords",
    "qbankResearchSummaryRecords",
    "ojRecordsWithSameTopicLocalContent",
    "ojRecordsWithLocalResearchContent",
    "recordsWithTitleDerivedOutline",
    "ojRecordsWithPublicOrExternalSummary",
    "ojRecordsWithOriginalPreparationGuide",
    "qbankRecordsWithOriginalPreparationGuide",
    "recordsWithOriginalPreparationGuide",
  ].forEach((key) => {
    if (metadata[key] === undefined && counts[key] !== undefined) metadata[key] = counts[key];
  });
  return metadata;
}

async function fetchOptionalJson(path) {
  try {
    const response = await fetch(path, { cache: "no-store" });
    if (!response.ok) {
      return { ok: false, missing: response.status === 404, error: `${response.status} ${response.statusText}` };
    }
    const payload = await response.json();
    return {
      ok: true,
      payload,
      modified: response.headers.get("last-modified") || "",
    };
  } catch (error) {
    return { ok: false, missing: false, error: error instanceof Error ? error.message : String(error) };
  }
}

function readImportedPayload() {
  try {
    const raw = localStorage.getItem(STORAGE.imported);
    return raw ? JSON.parse(raw) : null;
  } catch (_) {
    return null;
  }
}

function buildQuestionIndex(payloads) {
  const records = [];
  payloads.forEach(({ payload, origin }) => {
    extractRecords(payload).forEach((record) => records.push({ record, origin }));
  });

  const merged = new Map();
  records.forEach(({ record, origin }, index) => {
    const normalized = normalizeQuestion(record, origin, index);
    const duplicateKey = normalized.identityKey || `${canonicalKey(normalized.company)}:${canonicalKey(normalized.title)}`;
    const titleKey = `${canonicalKey(normalized.company)}:${canonicalKey(normalized.title)}`;
    const knownKey = merged.has(duplicateKey) ? duplicateKey : merged.has(titleKey) ? titleKey : duplicateKey;
    if (merged.has(knownKey)) {
      merged.set(knownKey, mergeQuestion(merged.get(knownKey), normalized));
    } else {
      merged.set(duplicateKey, normalized);
      if (titleKey !== duplicateKey && !merged.has(titleKey)) {
        // Title aliases make cross-file duplicates merge even when one source has an id and another does not.
        Object.defineProperty(merged.get(duplicateKey), "_titleKey", { value: titleKey, enumerable: false });
      }
    }
  });

  // A second, conservative title pass catches the common id/no-id duplication case.
  const byTitle = new Map();
  for (const question of merged.values()) {
    const titleKey = `${canonicalKey(question.company)}:${canonicalKey(question.title)}`;
    if (byTitle.has(titleKey)) {
      byTitle.set(titleKey, mergeQuestion(byTitle.get(titleKey), question));
    } else {
      byTitle.set(titleKey, question);
    }
  }
  return [...byTitle.values()].map((question, index) => ({ ...question, originalIndex: index }));
}

async function loadAllData() {
  state.loading = true;
  renderLoading();
  setSnapshotStatus("loading", "正在读取本地资料");

  const results = await Promise.all([
    ...DATA_FILES.map((file) => fetchOptionalJson(file.path)),
    fetchOptionalJson(SOURCES_FILE),
    fetchOptionalJson(MEMBER_AUDIT_FILE),
  ]);

  const payloads = [];
  const failures = [];
  DATA_FILES.forEach((file, index) => {
    const result = results[index];
    if (result.ok) {
      payloads.push({ payload: result.payload, origin: file.origin, modified: result.modified });
    } else {
      failures.push({ ...file, ...result });
    }
  });

  const imported = readImportedPayload();
  if (imported) payloads.push({ payload: imported, origin: "浏览器导入", modified: "" });

  const sourcesResult = results[DATA_FILES.length];
  const memberAuditResult = results[DATA_FILES.length + 1];
  state.sources = sourcesResult.ok ? normalizeSourceCatalog(sourcesResult.payload) : DEFAULT_SOURCES;
  state.memberAudit = memberAuditResult.ok ? memberAuditResult.payload : null;
  if (!state.sources.length) state.sources = DEFAULT_SOURCES;
  state.payloads = payloads;
  state.loadFailures = failures;
  state.questions = buildQuestionIndex(payloads);
  state.metadata = payloads.reduce(
    (metadata, entry) => ({ ...metadata, ...extractMetadata(entry.payload) }),
    {}
  );
  if (!state.metadata.generatedAt) {
    state.metadata.generatedAt = payloads.map((entry) => entry.modified).filter(Boolean)[0] || "";
  }
  state.loading = false;

  renderSourceCatalog();
  renderFilterOptions();
  syncFilterInputs();
  applyFilters();
  renderStats();
  updateImportState();

  if (state.questions.length) {
    const savedCatalog = Number(state.metadata.canonicalCatalogRecords || 0);
    const targetCatalog = Number(state.metadata.officialReportedRecords || 0);
    const coverage = savedCatalog && targetCatalog ? ` · 官方 ${savedCatalog}/${targetCatalog}` : "";
    const contentCount = Number(state.metadata.recordsWithAnyContent || 0);
    const contentCoverage = contentCount && savedCatalog ? ` · 内容 ${contentCount}/${savedCatalog}` : "";
    const memberAuditSummary = state.memberAudit?.summary || {};
    const memberRecords = Number(memberAuditSummary.memberRecords || 0);
    const verifiedMemberBodies = Number(
      memberAuditSummary.recordsWithVerifiedCanonicalMemberBody || 0
    );
    const viewerReady = Number(memberAuditSummary.recordsWithViewerCompatiblePostUrl || 0);
    const memberAuditText = memberRecords
      ? `会员 canonical 正文已验证 ${verifiedMemberBodies}/${memberRecords}；可复制给第三方工具的帖子 URL ${viewerReady}/${memberRecords}，当前邀请码配额 250/250。`
      : "";
    setSnapshotStatus("ready", `本地索引 · ${state.questions.length} 条${coverage}${contentCoverage}`);
    if (failures.length) {
      const missingNames = failures.map((failure) => failure.path.split("/").pop()).join("、");
      showNotice(`当前已加载可用资料；${missingNames} 未找到或无法读取。你仍可导入自己的 JSON。`);
    } else if (savedCatalog && targetCatalog && savedCatalog < targetCatalog) {
      const canonicalBodies = Number(state.metadata.canonicalSourceBodyRecords || 0);
      const directTopics = Number(state.metadata.qbankDirectTopicContentRecords || 0);
      const research = Number(state.metadata.qbankResearchSummaryRecords || 0);
      const family = Number(state.metadata.ojRecordsWithSameTopicLocalContent || 0);
      const ojResearch = Number(state.metadata.ojRecordsWithLocalResearchContent || 0);
      const outlines = Number(state.metadata.recordsWithTitleDerivedOutline || 0);
      const ojPublic = Number(state.metadata.ojRecordsWithPublicOrExternalSummary || 0);
      const originalGuides = Number(
        state.metadata.recordsWithOriginalPreparationGuide
        || state.metadata.ojRecordsWithOriginalPreparationGuide
        || 0
      );
      showNotice(
        `官方目录已逐项识别 ${savedCatalog}/${targetCatalog} 条；已枚举条目均有内容。内容层级：公开 canonical 正文 ${canonicalBodies}、直接同题材料 ${directTopics}、qbank 研究重构 ${research}、OJ 同题家族 ${family}、OJ 研究重构 ${ojResearch}、公开/外部 OJ 摘要 ${ojPublic}、原创中文准备指南 ${originalGuides}、仅标题提纲 ${outlines}。${memberAuditText} 剩余 ${targetCatalog - savedCatalog} 条分页 OJ 尚未枚举。`
      );
    } else if (savedCatalog && targetCatalog) {
      const canonicalBodies = Number(state.metadata.canonicalSourceBodyRecords || 0);
      const directTopics = Number(state.metadata.qbankDirectTopicContentRecords || 0);
      const research = Number(state.metadata.qbankResearchSummaryRecords || 0);
      const family = Number(state.metadata.ojRecordsWithSameTopicLocalContent || 0);
      const ojResearch = Number(state.metadata.ojRecordsWithLocalResearchContent || 0);
      const outlines = Number(state.metadata.recordsWithTitleDerivedOutline || 0);
      const ojPublic = Number(state.metadata.ojRecordsWithPublicOrExternalSummary || 0);
      const originalGuides = Number(
        state.metadata.recordsWithOriginalPreparationGuide
        || state.metadata.ojRecordsWithOriginalPreparationGuide
        || 0
      );
      showNotice(
        `官方目录已逐项识别 ${savedCatalog}/${targetCatalog} 条。内容层级：公开 canonical 正文 ${canonicalBodies}、直接同题材料 ${directTopics}、qbank 研究重构 ${research}、OJ 同题家族 ${family}、OJ 研究重构 ${ojResearch}、公开/外部 OJ 摘要 ${ojPublic}、原创中文准备指南 ${originalGuides}、仅标题提纲 ${outlines}。${memberAuditText} 原创指南和标题提纲都不是官方题面，请通过卡片内官方链接核对。`
      );
    } else {
      hideNotice();
    }
    openQuestionFromHash();
  } else {
    setSnapshotStatus("error", "尚无本地资料");
    showNotice("未找到可展示的数据。请生成 supplemental.json，或导入你自己的 JSON 文件。", "error");
    renderNoDataState();
  }
}

function normalizeSourceCatalog(payload) {
  const rows = Array.isArray(payload)
    ? payload
    : payload?.sources || payload?.official || payload?.links || payload?.companies || [];
  const normalized = rawList(rows)
    .map((entry) => {
      if (typeof entry === "string") return { name: "原始来源", url: safeExternalUrl(entry) };
      return {
        name: plainText(pick(entry, "name", "title", "label", "displayName", "display_name")) ||
          "原始来源",
        url: safeExternalUrl(
          pick(entry, "url", "href", "link", "questionBankUrl", "question_bank_url")
        ),
      };
    })
    .filter((entry) => entry.url);

  const combined = [...DEFAULT_SOURCES, ...normalized];
  const seen = new Set();
  return combined.filter((entry) => {
    if (seen.has(entry.url)) return false;
    seen.add(entry.url);
    return true;
  });
}

function renderSourceCatalog() {
  dom.officialLinks.replaceChildren();
  state.sources.forEach((source) => {
    const link = document.createElement("a");
    link.href = source.url;
    link.target = "_blank";
    link.rel = "noreferrer noopener";
    link.append(document.createTextNode(`${source.name} `));
    const arrow = document.createElement("span");
    arrow.setAttribute("aria-hidden", "true");
    arrow.textContent = "↗";
    link.append(arrow);
    dom.officialLinks.append(link);
  });
}

function setSnapshotStatus(status, label) {
  dom.snapshotBadge.classList.remove("ready", "error");
  if (status !== "loading") dom.snapshotBadge.classList.add(status);
  dom.snapshotLabel.textContent = label;
}

function showNotice(message, type = "warning") {
  dom.notice.textContent = message;
  dom.notice.className = `notice${type === "error" ? " error" : ""}`;
  dom.notice.hidden = false;
}

function hideNotice() {
  dom.notice.hidden = true;
  dom.notice.textContent = "";
}

function renderLoading() {
  dom.grid.replaceChildren();
  for (let index = 0; index < 6; index += 1) {
    const card = document.createElement("div");
    card.className = "skeleton-card";
    card.setAttribute("aria-hidden", "true");
    dom.grid.append(card);
  }
  dom.resultCount.textContent = "正在载入…";
}

function dimensionCounts(field) {
  const counts = new Map();
  state.questions.forEach((question) => {
    const source = field === "access" ? question.access.code : question[field];
    const values = Array.isArray(source) ? source : [source];
    [...new Set(values.filter(Boolean))].forEach((value) => counts.set(value, (counts.get(value) || 0) + 1));
  });
  return [...counts.entries()].map(([value, count]) => ({ value, count }));
}

function preferredSort(entries, order = []) {
  const rank = new Map(order.map((value, index) => [value, index]));
  return [...entries].sort((left, right) => {
    const leftRank = rank.has(left.value) ? rank.get(left.value) : Number.MAX_SAFE_INTEGER;
    const rightRank = rank.has(right.value) ? rank.get(right.value) : Number.MAX_SAFE_INTEGER;
    return leftRank - rightRank || right.count - left.count || left.value.localeCompare(right.value, "zh-CN");
  });
}

function renderFilterOptions() {
  const companies = preferredSort(dimensionCounts("company"), ["OpenAI", "Anthropic"]);
  const categories = preferredSort(dimensionCounts("category"), [
    "编程",
    "ML 编程",
    "系统设计",
    "ML 系统设计",
    "ML 理论",
    "行为 / 文化",
    "面试流程",
    "其他",
  ]);
  const roles = preferredSort(dimensionCounts("roles"));
  const access = preferredSort(
    dimensionCounts("access").map((entry) => ({
      value: entry.value,
      count: entry.count,
      label: ACCESS_LABELS[entry.value],
    })),
    ["public", "summary", "locked", "external", "unknown"]
  );

  renderOptionList(dom.companyOptions, "company", companies);
  renderOptionList(dom.categoryOptions, "category", categories);
  renderOptionList(dom.roleOptions, "role", roles);
  renderOptionList(dom.accessOptions, "access", access, (entry) => entry.label || ACCESS_LABELS[entry.value]);
  renderTagOptions();
}

function renderOptionList(container, dimension, entries, labelFor = (entry) => entry.value) {
  container.replaceChildren();
  entries.forEach((entry) => container.append(createCheckOption(dimension, entry.value, labelFor(entry), entry.count)));
  if (!entries.length) {
    const empty = document.createElement("p");
    empty.className = "filter-empty";
    empty.textContent = "暂无选项";
    container.append(empty);
  }
}

function createCheckOption(dimension, value, label, count) {
  const option = document.createElement("label");
  option.className = "check-option";

  const input = document.createElement("input");
  input.type = "checkbox";
  input.dataset.dimension = dimension;
  input.value = value;
  input.checked = state.filters[dimension].has(value);

  const box = document.createElement("span");
  box.className = "check-box";
  box.setAttribute("aria-hidden", "true");

  const copy = document.createElement("span");
  copy.className = "check-label";
  copy.textContent = label;
  copy.title = label;

  const countNode = document.createElement("span");
  countNode.className = "check-count";
  countNode.textContent = count;

  option.append(input, box, copy, countNode);
  return option;
}

function renderTagOptions() {
  const entries = preferredSort(dimensionCounts("tags"));
  const query = state.tagQuery.trim().toLocaleLowerCase("zh-CN");
  let matching = query
    ? entries.filter((entry) => entry.value.toLocaleLowerCase("zh-CN").includes(query))
    : entries;
  const selected = matching.filter((entry) => state.filters.tag.has(entry.value));
  if (!state.showAllTags && !query) {
    matching = [...selected, ...matching.filter((entry) => !state.filters.tag.has(entry.value))].slice(0, 18);
  }

  renderOptionList(dom.tagOptions, "tag", matching);
  dom.showAllTags.hidden = Boolean(query) || entries.length <= 18;
  dom.showAllTags.textContent = state.showAllTags ? "收起标签" : `显示全部 ${entries.length} 个标签`;
}

function syncFilterInputs() {
  dom.filtersPanel.querySelectorAll("input[data-dimension]").forEach((input) => {
    const dimension = input.dataset.dimension;
    input.checked = Boolean(state.filters[dimension]?.has(input.value));
  });
}

function questionValues(question, dimension) {
  if (dimension === "company") return [question.company];
  if (dimension === "category") return [question.category];
  if (dimension === "role") return question.roles;
  if (dimension === "tag") return question.tags;
  if (dimension === "access") return [question.access.code];
  return [];
}

function matchesProgress(question, selected) {
  if (!selected.size) return true;
  return [...selected].some((filter) => {
    if (filter === "favorite") return state.favorites.has(question.id);
    if (filter === "completed") return state.completed.has(question.id);
    if (filter === "pending") return !state.completed.has(question.id);
    return true;
  });
}

function searchTokens(query) {
  return query
    .toLocaleLowerCase("zh-CN")
    .split(/\s+/)
    .map((token) => token.trim())
    .filter(Boolean);
}

function relevanceScore(question, tokens) {
  if (!tokens.length) return 0;
  const title = question.title.toLocaleLowerCase("zh-CN");
  const tags = question.tags.join(" ").toLocaleLowerCase("zh-CN");
  const summary = question.displaySummary.toLocaleLowerCase("zh-CN");
  return tokens.reduce((score, token) => {
    if (title === token) return score + 100;
    if (title.includes(token)) score += 45;
    if (tags.includes(token)) score += 24;
    if (summary.includes(token)) score += 10;
    if (question.searchText.includes(token)) score += 3;
    return score;
  }, 0);
}

function applyFilters() {
  if (state.loading) return;
  const tokens = searchTokens(state.query);
  state.filtered = state.questions.filter((question) => {
    for (const dimension of ["company", "category", "role", "tag", "access"]) {
      const selected = state.filters[dimension];
      if (selected.size && !questionValues(question, dimension).some((value) => selected.has(value))) return false;
    }
    if (!matchesProgress(question, state.filters.progress)) return false;
    if (tokens.length && !tokens.every((token) => question.searchText.includes(token))) return false;
    return true;
  });

  const sorters = {
    relevance: (left, right) =>
      relevanceScore(right, tokens) - relevanceScore(left, tokens) ||
      right.frequencyScore - left.frequencyScore ||
      right.lastAskedScore - left.lastAskedScore ||
      left.originalIndex - right.originalIndex,
    recent: (left, right) =>
      right.lastAskedScore - left.lastAskedScore || right.frequencyScore - left.frequencyScore,
    frequency: (left, right) =>
      right.frequencyScore - left.frequencyScore || right.lastAskedScore - left.lastAskedScore,
    title: (left, right) => left.title.localeCompare(right.title, "zh-CN"),
    company: (left, right) =>
      left.company.localeCompare(right.company, "en") || left.title.localeCompare(right.title, "zh-CN"),
  };
  state.filtered.sort(sorters[state.sort] || sorters.relevance);

  renderActiveFilters();
  renderQuestions();
  renderStats();
  updateFilterControls();
}

function updateFilterControls() {
  const selectedCount = Object.values(state.filters).reduce((total, values) => total + values.size, 0);
  const hasChanges = selectedCount > 0 || Boolean(state.query);
  dom.resetFilters.disabled = !hasChanges;
  dom.mobileFilterCount.hidden = selectedCount === 0;
  dom.mobileFilterCount.textContent = selectedCount;
  dom.clearSearch.hidden = !state.query;
}

function renderActiveFilters() {
  dom.activeFilters.replaceChildren();
  const chips = [];
  Object.entries(state.filters).forEach(([dimension, values]) => {
    values.forEach((value) => {
      let label = value;
      if (dimension === "access") label = ACCESS_LABELS[value] || value;
      if (dimension === "progress") label = PROGRESS_LABELS[value] || value;
      chips.push({ dimension, value, label });
    });
  });

  chips.forEach((chip) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "filter-chip";
    button.dataset.dimension = chip.dimension;
    button.dataset.value = chip.value;
    button.title = `移除筛选：${chip.label}`;
    const label = document.createElement("span");
    label.textContent = chip.label;
    const close = document.createElement("span");
    close.setAttribute("aria-hidden", "true");
    close.textContent = "×";
    button.append(label, close);
    dom.activeFilters.append(button);
  });
  dom.activeFilters.hidden = chips.length === 0;
}

function renderQuestions() {
  dom.grid.replaceChildren();
  const totalPages = Math.max(1, Math.ceil(state.filtered.length / state.pageSize));
  state.currentPage = Math.min(Math.max(1, state.currentPage), totalPages);
  const start = (state.currentPage - 1) * state.pageSize;
  const end = Math.min(start + state.pageSize, state.filtered.length);
  const visible = state.filtered.slice(start, end);
  visible.forEach((question, index) => dom.grid.append(createQuestionCard(question, start + index + 1)));

  if (!state.filtered.length) renderEmptyFilterState();

  dom.resultCount.textContent = state.filtered.length
    ? `第 ${start + 1}–${end} 条 · 共 ${state.filtered.length} 条 / 全部 ${state.questions.length} 条`
    : `0 条 / 全部 ${state.questions.length} 条`;
  dom.resultsHeading.textContent = hasActiveFilters() ? "筛选结果" : "全部资料";
  renderPagination(totalPages);
}

function paginationItems(currentPage, totalPages) {
  if (totalPages <= 7) return Array.from({ length: totalPages }, (_, index) => index + 1);
  const pages = new Set([1, totalPages, currentPage - 1, currentPage, currentPage + 1]);
  if (currentPage <= 4) [2, 3, 4, 5].forEach((page) => pages.add(page));
  if (currentPage >= totalPages - 3) {
    [totalPages - 4, totalPages - 3, totalPages - 2, totalPages - 1].forEach((page) => pages.add(page));
  }
  const sorted = [...pages].filter((page) => page >= 1 && page <= totalPages).sort((a, b) => a - b);
  const items = [];
  sorted.forEach((page, index) => {
    if (index && page - sorted[index - 1] > 1) items.push("ellipsis");
    items.push(page);
  });
  return items;
}

function renderPagination(totalPages) {
  const hasResults = state.filtered.length > 0;
  dom.pagination.hidden = !hasResults;
  dom.pagePrev.disabled = state.currentPage <= 1;
  dom.pageNext.disabled = state.currentPage >= totalPages;
  dom.pageNumbers.replaceChildren();

  paginationItems(state.currentPage, totalPages).forEach((item) => {
    if (item === "ellipsis") {
      const ellipsis = document.createElement("span");
      ellipsis.className = "pagination-ellipsis";
      ellipsis.textContent = "…";
      ellipsis.setAttribute("aria-hidden", "true");
      dom.pageNumbers.append(ellipsis);
      return;
    }
    const button = document.createElement("button");
    button.type = "button";
    button.className = `pagination-page${item === state.currentPage ? " active" : ""}`;
    button.textContent = item;
    button.dataset.page = item;
    button.setAttribute("aria-label", `第 ${item} 页`);
    if (item === state.currentPage) button.setAttribute("aria-current", "page");
    dom.pageNumbers.append(button);
  });
}

function goToPage(page) {
  const totalPages = Math.max(1, Math.ceil(state.filtered.length / state.pageSize));
  const nextPage = Math.min(Math.max(1, Number(page) || 1), totalPages);
  if (nextPage === state.currentPage) return;
  state.currentPage = nextPage;
  renderQuestions();
  document.querySelector("#question-list")?.scrollIntoView({ behavior: "smooth", block: "start" });
}

function hasActiveFilters() {
  return Boolean(state.query) || Object.values(state.filters).some((values) => values.size);
}

function createQuestionCard(question, position) {
  const card = document.createElement("article");
  card.className = `question-card${state.completed.has(question.id) ? " is-completed" : ""}`;
  card.dataset.questionId = question.id;

  const number = document.createElement("span");
  number.className = "row-number";
  number.textContent = String(position).padStart(2, "0");

  const main = document.createElement("div");
  main.className = "row-main";

  const titleLine = document.createElement("div");
  titleLine.className = "row-title-line";
  titleLine.append(createPill(question.company, `company-pill ${canonicalKey(question.company)}`));
  titleLine.append(createPill(question.category, "category-pill"));
  if (question.isNew) titleLine.append(createPill("NEW", "new-pill"));

  const heading = document.createElement("h3");
  const openButton = document.createElement("button");
  openButton.type = "button";
  openButton.className = "card-title-button";
  openButton.textContent = question.title;
  openButton.addEventListener("click", () => openQuestion(question));
  heading.append(openButton);

  const summary = document.createElement("p");
  summary.className = "card-summary";
  summary.textContent = question.displaySummary;
  main.append(titleLine, heading, summary);

  const taxonomy = document.createElement("div");
  taxonomy.className = "row-taxonomy";
  const tags = document.createElement("div");
  tags.className = "card-tags";
  question.tags.slice(0, 4).forEach((tag) => tags.append(createPill(tag, "tag-pill")));
  if (question.tags.length > 4) {
    const more = document.createElement("span");
    more.className = "tag-more";
    more.textContent = `+${question.tags.length - 4}`;
    tags.append(more);
  }
  taxonomy.append(tags);
  const stage = document.createElement("span");
  stage.className = "row-stage";
  stage.textContent = question.stages[0] || question.roles[0] || question.access.label;
  taxonomy.append(stage);

  const meta = document.createElement("div");
  meta.className = "row-meta";
  [question.frequency, question.difficulty, formatDate(question.lastAsked), contentKindLabel(question.contentKind)]
    .filter(Boolean)
    .slice(0, 4)
    .forEach((value) => {
      const item = document.createElement("span");
      item.textContent = value;
      item.title = value;
      meta.append(item);
    });

  const actions = document.createElement("div");
  actions.className = "row-actions";
  const favorite = createCardAction(
    state.favorites.has(question.id) ? "★" : "☆",
    "favorite-action",
    "收藏",
    state.favorites.has(question.id)
  );
  favorite.addEventListener("click", (event) => {
    event.stopPropagation();
    toggleFavorite(question.id);
  });
  const completed = createCardAction(
    state.completed.has(question.id) ? "✓" : "○",
    "complete-action",
    "标记完成",
    state.completed.has(question.id)
  );
  completed.addEventListener("click", (event) => {
    event.stopPropagation();
    toggleCompleted(question.id);
  });
  actions.append(favorite, completed);
  if (question.sources[0]) {
    const sourceLink = document.createElement("a");
    sourceLink.className = "card-source-link";
    sourceLink.href = question.sources[0].url;
    sourceLink.target = "_blank";
    sourceLink.rel = "noreferrer noopener";
    sourceLink.textContent = "来源 ↗";
    sourceLink.addEventListener("click", (event) => event.stopPropagation());
    actions.append(sourceLink);
  }
  const detailButton = document.createElement("button");
  detailButton.type = "button";
  detailButton.className = "row-open-button";
  detailButton.textContent = "查看";
  detailButton.addEventListener("click", () => openQuestion(question));
  actions.append(detailButton);

  card.append(number, main, taxonomy, meta, actions);
  card.addEventListener("click", (event) => {
    if (!event.target.closest("button, a")) openQuestion(question);
  });
  return card;
}

function createCardAction(symbol, extraClass, label, active) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = `card-action ${extraClass}${active ? " active" : ""}`;
  button.textContent = symbol;
  button.title = label;
  button.setAttribute("aria-label", label);
  button.setAttribute("aria-pressed", String(active));
  return button;
}

function createPill(text, className) {
  const pill = document.createElement("span");
  pill.className = className;
  pill.textContent = text;
  pill.title = text;
  return pill;
}

function renderEmptyFilterState() {
  const empty = createEmptyState(
    "没有匹配的资料",
    "试试缩短搜索词，或移除一两个筛选条件。",
    "重置搜索与筛选",
    resetAllFilters
  );
  dom.grid.append(empty);
}

function renderNoDataState() {
  dom.grid.replaceChildren();
  dom.grid.append(
    createEmptyState(
      "资料文件尚未就绪",
      "将用户自有数据放入 data/questions.json，或使用下方按钮导入 JSON。页面也会自动合并 data/supplemental.json。",
      "导入 JSON",
      () => dom.importFile.click(),
      "重新读取",
      loadAllData
    )
  );
  dom.resultCount.textContent = "0 条";
  dom.pagination.hidden = true;
}

function createEmptyState(title, message, primaryLabel, primaryAction, secondaryLabel, secondaryAction) {
  const wrapper = document.createElement("div");
  wrapper.className = "empty-state";
  const inner = document.createElement("div");
  inner.className = "empty-state-inner";
  const icon = document.createElement("div");
  icon.className = "empty-icon";
  icon.setAttribute("aria-hidden", "true");
  icon.textContent = "⌕";
  const heading = document.createElement("h3");
  heading.textContent = title;
  const copy = document.createElement("p");
  copy.textContent = message;
  const actions = document.createElement("div");
  actions.className = "empty-actions";
  const primary = document.createElement("button");
  primary.type = "button";
  primary.className = "primary-button";
  primary.textContent = primaryLabel;
  primary.addEventListener("click", primaryAction);
  actions.append(primary);
  if (secondaryLabel && secondaryAction) {
    const secondary = document.createElement("button");
    secondary.type = "button";
    secondary.className = "secondary-button";
    secondary.textContent = secondaryLabel;
    secondary.addEventListener("click", secondaryAction);
    actions.append(secondary);
  }
  inner.append(icon, heading, copy, actions);
  wrapper.append(inner);
  return wrapper;
}

function renderStats() {
  const validIds = new Set(state.questions.map((question) => question.id));
  const favoriteCount = [...state.favorites].filter((id) => validIds.has(id)).length;
  const completedCount = [...state.completed].filter((id) => validIds.has(id)).length;
  const savedCatalog = Number(state.metadata.canonicalCatalogRecords || 0);
  const targetCatalog = Number(state.metadata.officialReportedRecords || 0);
  dom.statTotal.textContent = savedCatalog && targetCatalog
    ? `${savedCatalog}/${targetCatalog}`
    : state.questions.length || "—";
  dom.statCompanies.textContent = new Set(state.questions.map((question) => question.company)).size || "—";
  dom.statFavorites.textContent = favoriteCount;
  dom.statCompleted.textContent = completedCount;
  dom.favoriteCount.textContent = favoriteCount;
  dom.completedCount.textContent = completedCount;
  dom.pendingCount.textContent = Math.max(0, state.questions.length - completedCount);

  const updated = formatDate(state.metadata.generatedAt);
  dom.snapshotDate.textContent = `资料更新时间：${updated || "未标注"}`;
}

function formatDate(value) {
  const text = plainText(value);
  if (!text) return "";
  if (/^\d{4}-\d{1,2}-\d{1,2}(?:T|\s|$)/.test(text)) {
    const parsed = new Date(text);
    if (!Number.isNaN(parsed.getTime())) {
      return new Intl.DateTimeFormat("zh-CN", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
      }).format(parsed);
    }
  }
  return text;
}

function formatDuration(value) {
  const text = plainText(value);
  if (!text) return "";
  if (/^\d+(?:\.\d+)?$/.test(text)) return `${text} 分钟`;
  return text;
}

function toggleFavorite(id) {
  if (state.favorites.has(id)) state.favorites.delete(id);
  else state.favorites.add(id);
  saveStoredSet(STORAGE.favorites, state.favorites);
  applyFilters();
  updateDetailActions();
}

function toggleCompleted(id) {
  if (state.completed.has(id)) state.completed.delete(id);
  else state.completed.add(id);
  saveStoredSet(STORAGE.completed, state.completed);
  applyFilters();
  updateDetailActions();
}

function openQuestion(question, updateHash = true) {
  state.activeQuestion = question;
  dom.detailCompany.textContent = question.company;
  dom.detailCompany.className = `company-pill ${canonicalKey(question.company)}`;
  dom.detailAccess.textContent = question.access.label;
  dom.detailAccess.className = `access-pill ${question.access.code}`;
  dom.detailTitle.textContent = question.title;
  renderDetailTags(question);
  renderDetailMeta(question);
  renderDetailContent(question);
  updateDetailActions();

  if (!dom.dialog.open) {
    if (typeof dom.dialog.showModal === "function") dom.dialog.showModal();
    else dom.dialog.setAttribute("open", "");
  }
  if (updateHash) {
    const url = new URL(window.location.href);
    url.hash = `q=${encodeURIComponent(question.id)}`;
    history.replaceState(null, "", url);
  }
}

function renderDetailTags(question) {
  dom.detailTags.replaceChildren();
  const tags = [...question.tags];
  if (!tags.length) tags.push(question.category);
  tags.forEach((tag) => dom.detailTags.append(createPill(tag, "tag-pill")));
}

function renderDetailMeta(question) {
  dom.detailMeta.replaceChildren();
  const fields = [
    ["分类", question.category],
    ["岗位", question.roles.join("、") || "未标注"],
    ["轮次", question.stages.join("、") || "未标注"],
    ["难度", question.difficulty || "未标注"],
    ["时长", formatDuration(question.duration) || "未标注"],
    ["最近出现", formatDate(question.lastAsked) || "未标注"],
    ["频率", question.frequency || "未标注"],
    ["正文", question.contentKind ? contentKindLabel(question.contentKind) : question.content ? "研究资料正文" : "未保存正文"],
    ["来源", `${Math.max(question.sourceCount, question.sources.length)} 个来源`],
  ];
  fields.forEach(([label, value]) => {
    const item = document.createElement("div");
    const term = document.createElement("dt");
    term.textContent = label;
    const detail = document.createElement("dd");
    detail.textContent = value;
    detail.title = value;
    item.append(term, detail);
    dom.detailMeta.append(item);
  });
}

function renderDetailContent(question) {
  dom.detailContent.replaceChildren();
  if (question.summary) addDetailTextSection("资料概览", question.summary);
  const disclosure = contentDisclosure(question);
  if (disclosure) addDetailTextSection("正文来源说明", disclosure);
  if (question.content && question.content !== question.summary) {
    addDetailTextSection(contentSectionTitle(question.contentKind), question.content);
  }
  if (question.solutionHint) addDetailTextSection("解题线索", question.solutionHint);
  if (question.sourceMatchNote) addDetailTextSection("来源匹配说明", question.sourceMatchNote);

  if (!question.summary && !question.content && !question.solutionHint && !question.sourceMatchNote) {
    const empty = document.createElement("div");
    empty.className = "detail-empty";
    empty.textContent = "当前本地索引只保存了条目元数据。请通过下方来源链接查看原始页面。";
    dom.detailContent.append(empty);
  }
  addSourceSection(question.sources);
  void addLocalMaterialsSection(question);
}

function contentKindLabel(value) {
  const labels = {
    "locally-saved-public-canonical-body": "公开 canonical 正文",
    "locally-saved-topic-editorial": "本地同题材料",
    "locally-saved-same-problem-prompt-and-hints": "同题题面与提示",
    "locally-saved-research-summary": "本地研究重构",
    "locally-saved-oj-research-summary": "OJ 研究重构",
    "same-topic-local-preparation-reference": "同题家族资料",
    "original-structured-preparation-guide": "原创中文准备指南",
    "title-derived-preparation-outline": "标题准备提纲",
    "locally-saved-public-oj-summary": "公开 OJ 摘要",
    "external-concept-guide": "外部概念指南",
    "supplemental-research-note": "补充研究资料",
  };
  return labels[plainText(value)] || (value ? humanize(value) : "未保存正文");
}

function contentSectionTitle(value) {
  const labels = {
    "locally-saved-public-canonical-body": "公开题面",
    "locally-saved-topic-editorial": "本地已保存同题材料",
    "locally-saved-same-problem-prompt-and-hints": "本地已保存同题题面与提示",
    "locally-saved-research-summary": "研究摘要与解题提示",
    "locally-saved-oj-research-summary": "OJ 研究摘要与解题提示",
    "same-topic-local-preparation-reference": "同题家族准备资料",
    "original-structured-preparation-guide": "原创中文题解与准备指南",
    "title-derived-preparation-outline": "准备提纲",
    "locally-saved-public-oj-summary": "公开 OJ 题面摘要",
    "external-concept-guide": "外部概念准备指南",
    "supplemental-research-note": "补充研究正文",
  };
  return labels[plainText(value)] || "已保存内容";
}

function contentDisclosure(question) {
  const kind = plainText(question.contentKind);
  const matchKind = plainText(question.contentMatch);
  const disclosures = {
    "locally-saved-public-canonical-body": "来自工作区中已保存的公开 canonical 题面。",
    "locally-saved-topic-editorial": "来自你工作区中已有的同题题面、题解或设计指南；不是当前会员 canonical 页的逐字正文。",
    "locally-saved-same-problem-prompt-and-hints": "来自本地保存的外站同题题面与提示；没有参考实现，也不是 canonical 会员页正文。",
    "locally-saved-research-summary": "由你本地已有研究摘要和解题提示整理；不是原页面逐字复制。",
    "locally-saved-oj-research-summary": "由本地已有研究摘要重构；不是当前 UUID 页面的逐字题面。",
    "same-topic-local-preparation-reference": "这是与当前 OJ 高度相关的同题家族资料；当前 UUID 的精确约束仍以官方页面为准。",
    "original-structured-preparation-guide": "这是根据公开标题、可核实摘要和通用工程知识编写的原创中文准备指南；它提供题意模型、解法、复杂度和边界，但不是当前 UUID 的逐字原题或官方答案。",
    "title-derived-preparation-outline": "本地没有该条目的可靠题面；这里只显示根据官方标题生成的准备方向，不代表原题内容。",
    "locally-saved-public-oj-summary": "根据公开 canonical OJ 页面转述；会员示例与测试未复制。",
    "external-concept-guide": "这是外部概念资料整理，不是当前 UUID 的精确题面。",
    "supplemental-research-note": "这是工作区中的补充研究记录，可能汇总公开预览、面经和外站材料；请按下方来源核对，不要把它当作 canonical 逐字题面或官方答案。",
  };
  let base = disclosures[kind] || "";
  if (matchKind.startsWith("exact-uuid-public-oj-description")) {
    base = "题意依据与当前 UUID 精确绑定的公开 OJ 描述重新表述；解法和代码为原创准备材料，不是会员区逐字正文或官方答案。";
  } else if (matchKind.startsWith("public-same-problem")) {
    base = "已找到公开同题或明确的公开基础子题；本页题意按该公开证据核对，扩展部分与原创解法仍需以当前 UUID 页面为准。";
  } else if (matchKind === "related-stack-trace-variant-not-canonical") {
    base = "相关变体提醒：公开 overview 描述的是根据 enter/exit 事件重建调用栈；本地材料描述的是根据调用栈快照生成 start/end 事件。两者方向相反，因此这里只按相关变体展示，不把本地材料当作 canonical 原题。";
  } else if (matchKind === "unresolved-source-only") {
    base = "尚未识别：公开资料只有条目和关联帖子 URL，没有足够题面信息，因此本页不编造题意或答案。";
  } else if (matchKind === "source-conflict-related-practice-only") {
    base = "来源冲突：标题与关联帖摘要不一致。本页只提供明确标注的同题家族练习，不能视为当前 UUID 的原题答案。";
  } else if (matchKind === "public-description-conflict-unresolved") {
    base = "公开描述存在矛盾：本页会逐项说明冲突与可确认范围，不会伪造一个无法验证的标准答案。";
  } else if (matchKind === "public-interview-round-not-specific-problem") {
    base = "这是一轮面试形式说明，不是具有固定输入输出的单题；正文中的练习均为同方向原创准备材料。";
  }
  const quality = plainText(question.contentQuality);
  const confidence = plainText(question.contentMatchConfidence);
  const meta = [quality ? `质量：${contentQualityLabel(quality)}` : "", confidence ? `匹配：${confidenceLabel(confidence)}` : ""]
    .filter(Boolean)
    .join("；");
  return [base, meta].filter(Boolean).join("\n");
}

function contentQualityLabel(value) {
  const labels = {
    "public-canonical-problem-body": "公开 canonical 题面",
    "problem-and-solution": "题面与完整解法",
    "problem-and-discussion": "题面与讨论",
    "requirements-examples-and-discussion": "需求、示例与讨论",
    "problem-and-hints-no-reference-solution": "题面与提示（无参考实现）",
    "design-guide": "系统设计指南",
    "question-set-and-advice": "问题集与准备建议",
    "brief-topic-summary": "简要主题摘要",
    "research-summary-and-solution-hints": "研究摘要与解题提示",
    "related-family-preparation": "同题家族准备资料",
    "public-requirements-summary": "公开需求摘要",
    "external-concept-preparation-guide": "外部概念准备指南",
    "structured-chinese-problem-and-solution-guide": "结构化中文题意与解法",
    "title-derived-outline-only": "仅标题准备提纲",
    "supplemental-research-note": "补充研究记录",
  };
  return labels[plainText(value).toLowerCase()] || humanize(value);
}

function addDetailTextSection(title, text) {
  const section = document.createElement("section");
  section.className = "detail-section";
  const heading = document.createElement("h3");
  heading.textContent = title;
  const content = document.createElement("div");
  content.className = "detail-prose detail-rich-text";
  appendStructuredText(content, text);
  section.append(heading, content);
  dom.detailContent.append(section);
}

function improveProseSpacing(value) {
  return String(value || "")
    .replace(/([\p{Script=Han}])([A-Za-z0-9])/gu, "$1 $2")
    .replace(/([A-Za-z0-9])([\p{Script=Han}])/gu, "$1 $2")
    .replace(/([\p{Script=Han}]),(?=[\p{Script=Han}])/gu, "$1，")
    .replace(/([\p{Script=Han}]);(?=[\p{Script=Han}])/gu, "$1；")
    .replace(/([\p{Script=Han}]):(?=[\p{Script=Han}])/gu, "$1：");
}

function appendInlineRichText(parent, value) {
  const source = String(value || "");
  const tokenPattern = /(\[[^\]\n]+\]\(https?:\/\/[^)\n]+\)|https?:\/\/[^\s<>()]+|`[^`\n]+`|\*\*[^*\n]+\*\*|(?<!\*)\*[^*\n]+\*(?!\*))/g;
  let cursor = 0;
  let match;
  while ((match = tokenPattern.exec(source))) {
    if (match.index > cursor) {
      parent.append(document.createTextNode(improveProseSpacing(source.slice(cursor, match.index))));
    }
    const token = match[0];
    if (token.startsWith("`")) {
      const code = document.createElement("code");
      code.textContent = token.slice(1, -1);
      parent.append(code);
    } else if (/^https?:\/\//i.test(token)) {
      const url = safeExternalUrl(token);
      if (url) {
        const link = document.createElement("a");
        link.href = url;
        link.target = "_blank";
        link.rel = "noreferrer noopener";
        link.textContent = token;
        parent.append(link);
      } else {
        parent.append(document.createTextNode(token));
      }
    } else if (token.startsWith("[")) {
      const linkParts = token.match(/^\[([^\]]+)\]\((https?:\/\/[^)]+)\)$/);
      const url = linkParts ? safeExternalUrl(linkParts[2]) : "";
      if (linkParts && url) {
        const link = document.createElement("a");
        link.href = url;
        link.target = "_blank";
        link.rel = "noreferrer noopener";
        link.textContent = improveProseSpacing(linkParts[1]);
        parent.append(link);
      } else {
        parent.append(document.createTextNode(improveProseSpacing(token)));
      }
    } else if (token.startsWith("**")) {
      const strong = document.createElement("strong");
      strong.textContent = improveProseSpacing(token.slice(2, -2));
      parent.append(strong);
    } else {
      const emphasis = document.createElement("em");
      appendInlineRichText(emphasis, token.slice(1, -1));
      parent.append(emphasis);
    }
    cursor = match.index + token.length;
  }
  if (cursor < source.length) {
    parent.append(document.createTextNode(improveProseSpacing(source.slice(cursor))));
  }
}

function prepareStructuredText(value) {
  const source = String(value || "").replace(/\r\n?/g, "\n").trim();
  if (!source) return "";

  const output = [];
  let paragraphLines = [];
  let inCodeFence = false;

  const flushParagraph = () => {
    if (!paragraphLines.length) return;
    const paragraph = paragraphLines.join(" ").trim();
    output.push(splitDenseProse(paragraph));
    paragraphLines = [];
  };

  source.split("\n").forEach((line) => {
    if (/^\s*`{3,}/.test(line)) {
      flushParagraph();
      output.push(line);
      inCodeFence = !inCodeFence;
      return;
    }
    if (inCodeFence) {
      output.push(line);
      return;
    }
    if (!line.trim()) {
      flushParagraph();
      if (output.at(-1) !== "") output.push("");
      return;
    }

    const structural = /^\s*(?:#{1,6}\s+|>\s?|[-*+]\s+|\d+[.)]\s+|\|.*\|\s*$|---+\s*$|___+\s*$|\*\*\*+\s*$)/.test(line);
    if (structural) {
      flushParagraph();
      output.push(line.trimEnd());
      return;
    }
    paragraphLines.push(line.trim());
  });
  flushParagraph();
  return output.join("\n").replace(/\n{3,}/g, "\n\n").trim();
}

function splitDenseProse(value) {
  const text = String(value || "").trim();
  if (text.length < 220 || text.includes("\n") || text.includes("```")) return text;

  const prepared = text
    .replace(/\s+\((\d+)\)\s+/g, "\n\n$1. ")
    .replace(/\s+(?=(?:part|level|stage|step)\s+\d+\b)/gi, "\n\n")
    .replace(
      /\s+(?=(?:hard gating|timeline|site follow-ups?|what they (?:do|don't) test|edge cases?|requirements?|complexity):)/gi,
      "\n\n"
    );

  const closingBrackets = { "(": ")", "（": "）", "[": "]", "【": "】", "{": "}" };
  const closingQuotes = { "“": "”", "‘": "’", "\"": "\"" };
  const sentences = [];

  prepared.split(/\n{2,}/).forEach((segment) => {
    const bracketStack = [];
    let quote = "";
    let escaped = false;
    let buffer = "";
    const characters = [...segment.trim()];

    characters.forEach((character, index) => {
      buffer += character;
      if (escaped) {
        escaped = false;
        return;
      }
      if (character === "\\") {
        escaped = true;
        return;
      }
      if (quote) {
        if (character === quote) quote = "";
        return;
      }
      if (closingQuotes[character]) {
        quote = closingQuotes[character];
        return;
      }
      if (closingBrackets[character]) {
        bracketStack.push(closingBrackets[character]);
        return;
      }
      if (bracketStack.length && character === bracketStack[bracketStack.length - 1]) {
        bracketStack.pop();
        return;
      }
      if (bracketStack.length) return;

      const next = characters[index + 1] || "";
      const chineseStop = /[。！？]/.test(character);
      const asciiStop = /[.!?;]/.test(character)
        && (!next || /\s/.test(next))
        && buffer.trim().length >= 30
        && !/(?:e\.g|i\.e|etc|incl|approx)\.$/i.test(buffer.trim());
      if (chineseStop || asciiStop) {
        sentences.push(buffer.trim());
        buffer = "";
      }
    });

    if (buffer.trim()) sentences.push(buffer.trim());
  });
  return sentences.length > 1 ? sentences.join("\n\n") : prepared;
}

function looksLikeStandaloneHeading(value) {
  const line = String(value || "").trim();
  if (!line || line.length > 90) return false;
  if (/^\*\*[^*]+\*\*(?:\s*\([^)]*\))?:?$/.test(line)) return true;
  return /^(?:the problem|problem(?: statement| overview)?|example(?: scenario)?|key rules|function signature|important hints?|solution(?: approach| explanation)?|reference implementation|follow[- ]?up(?: questions?)?(?::.*)?|edge cases?(?: warning)?|system design(?: questions?| discussion)?|requirements?|input(?: format| samples?)?|expected output|output format|constraints?|discussion points?|complexity|test cases?|题目(?:说明|描述|概述|背景)|输入格式|输出格式|规则与约束|事件生成规则|函数签名|示例|解题思路|参考实现|复杂度|边界情况|常见追问|来源说明)[:：]?$/i.test(line);
}

function appendStructuredText(container, value) {
  const text = prepareStructuredText(value);
  if (!text) return;

  const lines = text.split("\n");
  let paragraphLines = [];
  let activeList = null;
  let inCodeFence = false;
  let codeFenceLength = 0;
  let codeLanguage = "";
  let codeLines = [];
  let activeTable = null;

  const flushParagraph = () => {
    if (!paragraphLines.length) return;
    const paragraph = document.createElement("p");
    appendInlineRichText(paragraph, paragraphLines.join("\n"));
    container.append(paragraph);
    paragraphLines = [];
  };

  const flushList = () => {
    activeList = null;
  };

  const flushTable = () => {
    activeTable = null;
  };

  const parseTableCells = (line) => line
    .trim()
    .replace(/^\|/, "")
    .replace(/\|$/, "")
    .split("|")
    .map((cell) => cell.trim());

  const appendTableRow = (parent, cells, cellTag) => {
    const row = document.createElement("tr");
    cells.forEach((cell) => {
      const element = document.createElement(cellTag);
      appendInlineRichText(element, cell);
      row.append(element);
    });
    parent.append(row);
  };

  const appendCodeBlock = () => {
    const pre = document.createElement("pre");
    const code = document.createElement("code");
    if (codeLanguage) code.dataset.language = codeLanguage;
    code.textContent = codeLines.join("\n").replace(/\n+$/, "");
    pre.append(code);
    container.append(pre);
    codeLanguage = "";
    codeLines = [];
  };

  lines.forEach((line, lineIndex) => {
    const fence = line.match(/^\s*(`{3,})\s*([^\s`]*)\s*$/);
    if (fence) {
      if (inCodeFence && fence[1].length >= codeFenceLength) {
        appendCodeBlock();
        inCodeFence = false;
        codeFenceLength = 0;
      } else if (!inCodeFence) {
        flushParagraph();
        flushList();
        flushTable();
        inCodeFence = true;
        codeFenceLength = fence[1].length;
        codeLanguage = fence[2] || "";
      } else {
        codeLines.push(line);
      }
      return;
    }
    if (inCodeFence) {
      codeLines.push(line);
      return;
    }

    if (!line.trim()) {
      flushParagraph();
      flushList();
      flushTable();
      return;
    }

    const tableRow = /^\s*\|.*\|\s*$/.test(line);
    const tableDivider = /^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(line);
    const nextLineIsDivider = lineIndex + 1 < lines.length
      && /^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(lines[lineIndex + 1]);
    if (tableRow && nextLineIsDivider) {
      flushParagraph();
      flushList();
      const wrapper = document.createElement("div");
      wrapper.className = "detail-table-wrap";
      const table = document.createElement("table");
      const head = document.createElement("thead");
      const body = document.createElement("tbody");
      appendTableRow(head, parseTableCells(line), "th");
      table.append(head, body);
      wrapper.append(table);
      container.append(wrapper);
      activeTable = { body };
      return;
    }
    if (activeTable && tableDivider) return;
    if (activeTable && tableRow) {
      appendTableRow(activeTable.body, parseTableCells(line), "td");
      return;
    }
    flushTable();

    const heading = line.match(/^\s*#{1,6}\s+(.+?)\s*$/);
    if (heading) {
      flushParagraph();
      flushList();
      const internalHeading = document.createElement("h4");
      appendInlineRichText(internalHeading, heading[1]);
      container.append(internalHeading);
      return;
    }

    if (looksLikeStandaloneHeading(line)) {
      flushParagraph();
      flushList();
      const internalHeading = document.createElement("h4");
      appendInlineRichText(internalHeading, line.replace(/[:：]\s*$/, ""));
      container.append(internalHeading);
      return;
    }

    if (/^\s*(?:---+|___+|\*\*\*+)\s*$/.test(line)) {
      flushParagraph();
      flushList();
      container.append(document.createElement("hr"));
      return;
    }

    const quote = line.match(/^\s*>\s?(.*)$/);
    if (quote) {
      flushParagraph();
      flushList();
      const blockquote = document.createElement("blockquote");
      appendInlineRichText(blockquote, quote[1]);
      container.append(blockquote);
      return;
    }

    const unordered = line.match(/^\s*[-*+]\s+(.+)$/);
    const ordered = line.match(/^\s*(\d+)[.)]\s+(.+)$/);
    if (unordered || ordered) {
      flushParagraph();
      const tag = ordered ? "ol" : "ul";
      if (!activeList || activeList.tagName.toLowerCase() !== tag) {
        activeList = document.createElement(tag);
        container.append(activeList);
      }
      const item = document.createElement("li");
      if (ordered) item.value = Number(ordered[1]);
      let itemText = ordered ? ordered[2] : unordered[1];
      const task = !ordered ? itemText.match(/^\[([ xX])\]\s+(.+)$/) : null;
      if (task) itemText = `${task[1].trim() ? "☑" : "☐"} ${task[2]}`;
      appendInlineRichText(item, itemText);
      activeList.append(item);
      return;
    }

    flushList();
    paragraphLines.push(line.trim());
  });

  if (inCodeFence) appendCodeBlock();
  flushParagraph();
}

function addSourceSection(sources) {
  const section = document.createElement("section");
  section.className = "detail-section";
  const heading = document.createElement("h3");
  heading.textContent = "来源链接 / 原帖与同题资料";
  section.append(heading);

  if (!sources.length) {
    const empty = document.createElement("div");
    empty.className = "detail-empty";
    empty.textContent = "这条资料尚未附带原始链接。可从页面底部的官方入口继续查找。";
    section.append(empty);
  } else {
    const list = document.createElement("ul");
    list.className = "source-list";
    sources.forEach((source, index) => {
      const item = document.createElement("li");
      const link = document.createElement("a");
      link.className = "source-link";
      link.href = source.url;
      link.target = "_blank";
      link.rel = "noreferrer noopener";
      const number = document.createElement("span");
      number.className = "source-number";
      number.textContent = index + 1;
      const copy = document.createElement("span");
      copy.className = "source-copy";
      const title = document.createElement("strong");
      title.textContent = source.title || "原始来源";
      const host = document.createElement("small");
      host.textContent = new URL(source.url).hostname;
      copy.append(title);
      const metadata = [
        source.relationship ? relationshipLabel(source.relationship) : "",
        source.confidence ? confidenceLabel(source.confidence) : "",
        host.textContent,
      ].filter(Boolean);
      host.textContent = metadata.join(" · ");
      copy.append(host);
      if (source.note) {
        const note = document.createElement("span");
        note.className = "source-note";
        note.textContent = source.note;
        copy.append(note);
      }
      const arrow = document.createElement("span");
      arrow.className = "source-arrow";
      arrow.setAttribute("aria-hidden", "true");
      arrow.textContent = "↗";
      link.append(number, copy, arrow);
      item.append(link);
      list.append(item);
    });
    section.append(list);

    const onePointThreeAcresThread = sources.find((source) => {
      try {
        const parsed = new URL(source.url);
        if (!/(^|\.)1point3acres\.com$/i.test(parsed.hostname)) return false;
        return (
          /(?:^|\/)(?:thread-|thread\/|post\/|pins\/)(\d+)/i.test(parsed.pathname)
          || /^\d+$/.test(parsed.searchParams.get("tid") || "")
        );
      } catch (_) {
        return false;
      }
    });
    if (onePointThreeAcresThread) {
      const tools = document.createElement("div");
      tools.className = "source-tools";
      const copyThread = document.createElement("button");
      copyThread.type = "button";
      copyThread.className = "source-tool-link source-copy-button";
      copyThread.textContent = "复制原帖 URL";
      copyThread.addEventListener("click", async () => {
        try {
          await navigator.clipboard.writeText(onePointThreeAcresThread.url);
          copyThread.textContent = "已复制 ✓";
          window.setTimeout(() => { copyThread.textContent = "复制原帖 URL"; }, 1600);
        } catch (_) {
          window.prompt("复制下面的原帖 URL：", onePointThreeAcresThread.url);
        }
      });
      const viewer = document.createElement("a");
      viewer.className = "source-tool-link";
      viewer.href = USER_PROVIDED_THREAD_VIEWER_URL;
      viewer.target = "_blank";
      viewer.rel = "noreferrer noopener";
      viewer.textContent = "打开你提供的第三方看帖工具 ↗";
      const note = document.createElement("small");
      note.textContent = "先复制原帖，再打开工具粘贴；工具不支持通过 URL 参数自动预填。2026-07-11 实测该邀请码已使用 250/250 次，配额重置后可继续尝试。";
      tools.append(copyThread, viewer, note);
      section.append(tools);
    }
  }
  dom.detailContent.append(section);
}

async function loadLocalMaterialsByQuestion() {
  if (!state.localMaterialsPromise) {
    state.localMaterialsPromise = fetch(LOCAL_MATERIALS_FILE, { cache: "no-store" })
      .then((response) => {
        if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
        return response.json();
      })
      .then((payload) => {
        const index = new Map();
        rawList(payload?.materials).forEach((material) => {
          rawList(material?.relatedQuestions).forEach((relation) => {
            const company = canonicalKey(relation?.company || "");
            const id = plainText(relation?.id);
            if (!company || !id) return;
            const key = `${company}:${id}`;
            if (!index.has(key)) index.set(key, []);
            index.get(key).push({
              id: plainText(material.id),
              title: plainText(material.title) || "本地资料",
              kind: plainText(material.kind) || "本地资料",
              summary: plainText(material.summary),
              sourceFiles: rawList(material.sourceFiles).map(plainText).filter(Boolean),
              score: Number(relation?.score || 0),
            });
          });
        });
        index.forEach((materials) => materials.sort((left, right) => right.score - left.score || left.title.localeCompare(right.title, "zh-CN")));
        return index;
      })
      .catch(() => new Map());
  }
  return state.localMaterialsPromise;
}

async function addLocalMaterialsSection(question) {
  const index = await loadLocalMaterialsByQuestion();
  if (state.activeQuestion?.id !== question.id) return;
  const materials = index.get(question.id) || [];
  if (!materials.length) return;

  const section = document.createElement("section");
  section.className = "detail-section";
  const heading = document.createElement("h3");
  heading.textContent = `my_interview_prep 关联资料（${materials.length}）`;
  const list = document.createElement("div");
  list.className = "question-local-materials";
  materials.slice(0, 10).forEach((material) => {
    const link = document.createElement("a");
    link.href = `./materials.html?material=${encodeURIComponent(material.id)}`;
    link.target = "_blank";
    link.rel = "noreferrer noopener";
    const copy = document.createElement("span");
    const title = document.createElement("strong");
    title.textContent = material.title;
    const meta = document.createElement("small");
    const score = material.score ? ` · 自动匹配 ${Math.round(material.score * 100)}%` : "";
    meta.textContent = `${material.kind}${score}${material.sourceFiles[0] ? ` · ${material.sourceFiles[0]}` : ""}`;
    copy.append(title, meta);
    const arrow = document.createElement("span");
    arrow.setAttribute("aria-hidden", "true");
    arrow.textContent = "↗";
    link.append(copy, arrow);
    list.append(link);
  });
  section.append(heading, list);
  dom.detailContent.append(section);
}

function relationshipLabel(value) {
  const labels = {
    "official-entry": "官方条目",
    "same-problem": "同题页",
    "direct-interview-report": "直接面经",
    "related-interview-report": "相关面经",
    "referenced-report": "被引用来源",
    "related-discussion": "相关讨论",
    "external-same-problem": "外站同题",
    "external-solution": "外站解法",
    "external-interview-report": "外站面经",
    "mapping-corroboration": "编号佐证",
    "same-report-mirror": "同帖摘要",
    "external-related-guide": "外站相关指南",
    "official-public-material": "官方公开材料",
    "official-related-material": "官方相关材料",
    "local-saved-editorial": "本地已保存同题材料",
    "same-topic-local-editorial": "本地同题家族资料",
    "related-variant-editorial": "本地相关变体材料",
    "local-research-note": "本地研究笔记",
    "local-practice-solution": "本地练习实现",
    "original-preparation-guide": "原创准备指南参考",
    "original-interview-thread": "原始面经帖",
    "conflicting-associated-thread": "待核对的关联帖",
    "external-same-problem-summary": "外站同题摘要",
    "external-related-problem-description": "外站相关题意",
    "external-related-practice": "外站同方向练习",
    "public-background": "公开背景资料",
    "implementation-reference": "实现参考文档",
    "official-related-entry": "站内相关题目入口",
    "local-evidence": "本地题库佐证",
    "local-interview-evidence": "本地面经佐证",
    "local-corroborating-note": "本地交叉佐证",
    "local-corroborating-summary": "本地汇总佐证",
    "local-related-topic-note": "本地相关主题笔记",
    "local-related-executable-practice": "本地可运行同族练习",
    "local-interview-note": "本地面经笔记",
    "external-related-problem": "外站相关练习",
    "local-preparation-note": "本地准备笔记",
    "local-detailed-preparation-note": "本地详细准备材料",
    "local-detailed-problem-summary": "本地详细题目整理",
    "local-detailed-problem-note": "本地详细题目笔记",
    "local-detailed-editorial": "本地详细题解",
    "local-same-family-editorial": "本地同题族材料",
    "local-related-interview-evidence": "本地相关面经佐证",
    "direct-local-interview-evidence": "本地直接面经佐证",
    "local-saved-same-family-nonmember-verbatim": "本地同题族非会员材料",
    "external-related-practice-page": "外站相关练习页",
  };
  return labels[plainText(value).toLowerCase()] || humanize(value);
}

function confidenceLabel(value) {
  const labels = {
    high: "高置信",
    "medium-high": "中高置信",
    medium: "中置信",
    low: "低置信",
    none: "尚无法匹配",
    unverified: "未验证",
  };
  return labels[plainText(value).toLowerCase()] || humanize(value);
}

function updateDetailActions() {
  const question = state.activeQuestion;
  if (!question) return;
  const favorite = state.favorites.has(question.id);
  const completed = state.completed.has(question.id);
  dom.detailFavorite.classList.toggle("active", favorite);
  dom.detailFavorite.setAttribute("aria-pressed", String(favorite));
  dom.detailFavorite.children[0].textContent = favorite ? "★" : "☆";
  dom.detailFavorite.children[1].textContent = favorite ? "已收藏" : "收藏";
  dom.detailComplete.classList.toggle("active", completed);
  dom.detailComplete.setAttribute("aria-pressed", String(completed));
  dom.detailComplete.children[0].textContent = completed ? "✓" : "○";
  dom.detailComplete.children[1].textContent = completed ? "已经完成" : "标记完成";
}

function closeQuestion() {
  if (dom.dialog.open && typeof dom.dialog.close === "function") dom.dialog.close();
  else dom.dialog.removeAttribute("open");
}

function clearQuestionHash() {
  const url = new URL(window.location.href);
  if (url.hash.startsWith("#q=")) {
    url.hash = "";
    history.replaceState(null, "", url);
  }
}

function openQuestionFromHash() {
  const match = window.location.hash.match(/^#q=(.+)$/);
  if (!match) return;
  const id = decodeURIComponent(match[1]);
  const question = state.questions.find((candidate) => candidate.id === id);
  if (question) openQuestion(question, false);
}

function resetAllFilters() {
  Object.values(state.filters).forEach((values) => values.clear());
  state.query = "";
  state.tagQuery = "";
  state.showAllTags = false;
  state.currentPage = 1;
  dom.mainSearch.value = "";
  dom.tagSearch.value = "";
  renderTagOptions();
  syncFilterInputs();
  applyFilters();
}

function updateImportState() {
  const hasImported = Boolean(readImportedPayload());
  dom.clearImported.hidden = !hasImported;
  if (hasImported) {
    const importedCount = extractRecords(readImportedPayload()).length;
    const importedAt = localStorage.getItem(STORAGE.importedAt);
    const time = importedAt ? formatDate(importedAt) : "本次会话";
    dom.importStatus.textContent = `浏览器中已导入 ${importedCount} 条 · ${time}`;
  } else {
    dom.importStatus.textContent = "导入内容仅存于当前浏览器";
  }
}

async function importJsonFile(file) {
  if (!file) return;
  try {
    const text = await file.text();
    const payload = JSON.parse(text);
    const rows = extractRecords(payload);
    if (!rows.length) {
      throw new Error("没有找到 questions、items、problems、entries 或 records 数组");
    }
    localStorage.setItem(STORAGE.imported, JSON.stringify(payload));
    localStorage.setItem(STORAGE.importedAt, new Date().toISOString());
    dom.importStatus.textContent = `正在载入 ${rows.length} 条导入资料…`;
    await loadAllData();
    showNotice(`已从 ${file.name} 导入 ${rows.length} 条资料；内容只保存在当前浏览器。`);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    showNotice(`导入失败：${message}`, "error");
    dom.importStatus.textContent = "导入失败；请检查 JSON 格式或浏览器存储空间";
  } finally {
    dom.importFile.value = "";
  }
}

function clearImportedData() {
  if (!window.confirm("清除当前浏览器中导入的资料？收藏与完成状态会保留。")) return;
  localStorage.removeItem(STORAGE.imported);
  localStorage.removeItem(STORAGE.importedAt);
  loadAllData();
}

function setTheme(theme) {
  document.documentElement.dataset.theme = theme;
  try {
    localStorage.setItem(STORAGE.theme, theme);
  } catch (_) {
    // Theme persistence is optional.
  }
  dom.themeToggle.title = theme === "dark" ? "切换到浅色主题" : "切换到深色主题";
}

function openFilters() {
  document.body.classList.add("filters-open");
  dom.filtersClose.focus();
}

function closeFilters() {
  document.body.classList.remove("filters-open");
}

function bindEvents() {
  dom.pageSize.value = String(state.pageSize);
  dom.mainSearch.addEventListener("input", () => {
    state.query = dom.mainSearch.value.trim();
    state.currentPage = 1;
    applyFilters();
  });
  dom.clearSearch.addEventListener("click", () => {
    state.query = "";
    dom.mainSearch.value = "";
    state.currentPage = 1;
    applyFilters();
    dom.mainSearch.focus();
  });
  dom.sortSelect.addEventListener("change", () => {
    state.sort = dom.sortSelect.value;
    state.currentPage = 1;
    applyFilters();
  });
  dom.tagSearch.addEventListener("input", () => {
    state.tagQuery = dom.tagSearch.value;
    renderTagOptions();
  });
  dom.showAllTags.addEventListener("click", () => {
    state.showAllTags = !state.showAllTags;
    renderTagOptions();
  });
  dom.filtersPanel.addEventListener("change", (event) => {
    const input = event.target.closest("input[data-dimension]");
    if (!input) return;
    const values = state.filters[input.dataset.dimension];
    if (input.checked) values.add(input.value);
    else values.delete(input.value);
    state.currentPage = 1;
    applyFilters();
  });
  dom.activeFilters.addEventListener("click", (event) => {
    const chip = event.target.closest(".filter-chip");
    if (!chip) return;
    state.filters[chip.dataset.dimension].delete(chip.dataset.value);
    syncFilterInputs();
    state.currentPage = 1;
    applyFilters();
  });
  dom.resetFilters.addEventListener("click", resetAllFilters);
  dom.pageSize.addEventListener("change", () => {
    const nextSize = Number(dom.pageSize.value);
    state.pageSize = PAGE_SIZE_OPTIONS.has(nextSize) ? nextSize : DEFAULT_PAGE_SIZE;
    state.currentPage = 1;
    try {
      localStorage.setItem(STORAGE.pageSize, String(state.pageSize));
    } catch (_) {
      // Page-size persistence is optional.
    }
    renderQuestions();
  });
  dom.pagePrev.addEventListener("click", () => goToPage(state.currentPage - 1));
  dom.pageNext.addEventListener("click", () => goToPage(state.currentPage + 1));
  dom.pageNumbers.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-page]");
    if (button) goToPage(button.dataset.page);
  });

  document.querySelectorAll(".filter-group-title").forEach((button) => {
    button.addEventListener("click", () => {
      button.setAttribute("aria-expanded", String(button.getAttribute("aria-expanded") !== "true"));
    });
  });

  dom.filtersOpen.addEventListener("click", openFilters);
  dom.filtersClose.addEventListener("click", closeFilters);
  dom.filterOverlay.addEventListener("click", closeFilters);
  dom.themeToggle.addEventListener("click", () => {
    setTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark");
  });

  dom.detailClose.addEventListener("click", closeQuestion);
  dom.detailFavorite.addEventListener("click", () => {
    if (state.activeQuestion) toggleFavorite(state.activeQuestion.id);
  });
  dom.detailComplete.addEventListener("click", () => {
    if (state.activeQuestion) toggleCompleted(state.activeQuestion.id);
  });
  dom.dialog.addEventListener("click", (event) => {
    if (event.target === dom.dialog) closeQuestion();
  });
  dom.dialog.addEventListener("close", () => {
    state.activeQuestion = null;
    clearQuestionHash();
  });

  const openImport = () => dom.importFile.click();
  dom.importData.addEventListener("click", openImport);
  dom.headerImport.addEventListener("click", openImport);
  dom.importFile.addEventListener("change", () => importJsonFile(dom.importFile.files?.[0]));
  dom.clearImported.addEventListener("click", clearImportedData);

  document.addEventListener("keydown", (event) => {
    const target = event.target;
    const isTyping = target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement || target instanceof HTMLSelectElement;
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      dom.mainSearch.focus();
      dom.mainSearch.select();
    } else if (event.key === "/" && !isTyping && !dom.dialog.open) {
      event.preventDefault();
      dom.mainSearch.focus();
    } else if (event.key === "Escape" && document.body.classList.contains("filters-open")) {
      closeFilters();
      dom.filtersOpen.focus();
    }
  });
}

bindEvents();
setTheme(document.documentElement.dataset.theme || "light");
loadAllData();
