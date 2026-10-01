/* global window, document, marked, hljs, renderMathInElement */
(function () {
  "use strict";

  var DOCS = window.A2_DOCS || [];
  var LS_KEY = "a2viewer_read";
  var GROUP_LABELS = {
    "README": "总览",
    "00_day_plan": "00 · Day Plan",
    "01_core": "01 · Core",
    "02_playbook": "02 · Playbook",
    "03_gaps": "03 · Gaps",
    "04_benchmarks": "04 · Benchmarks",
    "05_questions": "05 · Questions",
    "06_company_briefs": "06 · Company Briefs",
    "07_labs_guide": "07 · Labs Guide",
    "08_cheatsheet": "08 · Cheatsheet",
    "other": "其他"
  };

  var nav = document.getElementById("nav");
  var content = document.getElementById("content");
  var current = -1;

  /* ---------- read-state (localStorage) ---------- */
  function loadRead() {
    try { return JSON.parse(localStorage.getItem(LS_KEY) || "{}"); }
    catch (e) { return {}; }
  }
  function saveRead(m) {
    try { localStorage.setItem(LS_KEY, JSON.stringify(m)); } catch (e) { /* file:// private mode */ }
  }
  var readMap = loadRead();

  function setRead(path, on) {
    if (on) readMap[path] = true; else delete readMap[path];
    saveRead(readMap);
    renderNavState();
  }

  /* ---------- sidebar ---------- */
  function buildNav() {
    var html = [];
    var lastGroup = null;
    DOCS.forEach(function (d, i) {
      if (d.group !== lastGroup) {
        html.push('<div class="grp">' + esc(GROUP_LABELS[d.group] || d.group) + "</div>");
        lastGroup = d.group;
      }
      html.push(
        '<div class="item" data-i="' + i + '" title="' + esc(d.path) + '">' +
        '<span class="mark"></span><span class="t">' + esc(d.title) + "</span></div>"
      );
    });
    nav.innerHTML = html.join("");
    nav.addEventListener("click", function (e) {
      var it = e.target.closest(".item");
      if (it) show(parseInt(it.dataset.i, 10));
    });
    renderNavState();
  }

  function renderNavState() {
    var n = 0;
    nav.querySelectorAll(".item").forEach(function (it) {
      var d = DOCS[parseInt(it.dataset.i, 10)];
      var read = !!readMap[d.path];
      if (read) n++;
      it.classList.toggle("read", read);
      it.classList.toggle("sel", parseInt(it.dataset.i, 10) === current);
      it.querySelector(".mark").textContent = read ? "✓" : "";
    });
    var pct = DOCS.length ? Math.round(100 * n / DOCS.length) : 0;
    document.getElementById("progfill").style.width = pct + "%";
    document.getElementById("progtext").textContent = n + "/" + DOCS.length + " 已读";
  }

  /* ---------- doc rendering ---------- */
  function show(i) {
    if (i < 0 || i >= DOCS.length) return;
    current = i;
    var d = DOCS[i];
    var prev = i > 0 ? DOCS[i - 1] : null;
    var next = i < DOCS.length - 1 ? DOCS[i + 1] : null;

    content.innerHTML =
      '<div class="doc">' +
      '<div class="doc-top"><span class="path">' + esc(d.path) + "</span>" +
      '<label class="readbox"><input type="checkbox" id="readck"' +
      (readMap[d.path] ? " checked" : "") + "> 标记已读</label></div>" +
      '<div class="md" id="mdbody"></div>' +
      '<div class="pager">' +
      '<button id="prevbtn"' + (prev ? "" : " disabled") + ">" +
      '<span class="dir">← 上一篇</span>' + (prev ? esc(prev.title) : "—") + "</button>" +
      '<button id="nextbtn"' + (next ? "" : " disabled") + ">" +
      '<span class="dir">下一篇 →</span>' + (next ? esc(next.title) : "—") + "</button>" +
      "</div></div>";

    var body = document.getElementById("mdbody");
    body.innerHTML = marked.parse(d.content);

    // syntax highlight (scoped to this doc so re-renders never double-highlight)
    if (window.hljs) {
      body.querySelectorAll("pre code").forEach(function (el) { hljs.highlightElement(el); });
    }
    // KaTeX auto-render; skip silently if the local vendor copy failed to load
    if (typeof renderMathInElement === "function") {
      try {
        renderMathInElement(body, {
          delimiters: [
            { left: "$$", right: "$$", display: true },
            { left: "$", right: "$", display: false }
          ],
          throwOnError: false,
          ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code"]
        });
      } catch (e) { /* keep raw TeX */ }
    }

    document.getElementById("readck").addEventListener("change", function () {
      setRead(d.path, this.checked);
    });
    if (prev) document.getElementById("prevbtn").addEventListener("click", function () { show(i - 1); });
    if (next) document.getElementById("nextbtn").addEventListener("click", function () { show(i + 1); });

    interceptMdLinks(body, d.path);
    renderNavState();
    content.scrollTop = 0;
  }

  /* intercept relative .md links -> in-app navigation */
  function interceptMdLinks(container, fromPath) {
    container.querySelectorAll("a[href]").forEach(function (a) {
      var href = a.getAttribute("href");
      if (/^(https?:|mailto:|#)/i.test(href)) {
        if (/^https?:/i.test(href)) a.target = "_blank";
        return;
      }
      var clean = href.split("#")[0];
      if (!/\.md$/i.test(clean)) return;
      var target = resolvePath(fromPath, clean);
      var idx = DOCS.findIndex(function (d) { return d.path === target; });
      a.addEventListener("click", function (e) {
        e.preventDefault();
        if (idx >= 0) show(idx);
      });
      if (idx < 0) a.style.opacity = ".5"; // link target not in bundle
    });
  }

  function resolvePath(fromPath, rel) {
    var parts = fromPath.split("/").slice(0, -1); // dir of current doc
    rel.split("/").forEach(function (seg) {
      if (seg === "" || seg === ".") return;
      if (seg === "..") parts.pop();
      else parts.push(seg);
    });
    return parts.join("/");
  }

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  /* ---------- boot ---------- */
  marked.setOptions({ gfm: true, breaks: false });
  buildNav();
  if (DOCS.length) show(0);
})();
