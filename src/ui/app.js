const elLeft  = document.getElementById('page-left');
const elRight = document.getElementById('page-right');
const elInfo  = document.getElementById('page-info');
const btnPrev = document.getElementById('prev');
const btnNext = document.getElementById('next');

// types that get a full page to themselves
const FULL_TYPES = new Set(['empty_page']);

let entries = [];
let total = 0;
let current = 0; // first entry index on the current spread

// track first/last entry indexes of the current spread
const spread  = { firstIndex: null, lastIndex: null };
// history of first entry indexes for each spread, for back-navigation
const history = [];

const TEXT_FILE_MIME_PREFIXES = ['text/'];
const TEXT_FILE_MIME_TYPES = new Set([
  'application/json',
  'application/javascript',
  'text/markdown',
  'application/xml',
  'application/x-sh',
]);

const MARKDOWN_MIME_TYPES = new Set([
  'text/markdown',
  'text/x-markdown',
  'application/markdown',
  'application/x-markdown',
]);

async function fetchEntries() {
  const res = await fetch('/api/entries');
  if (!res.ok) return [];
  const data = await res.json();
  return data.entries || [];
}

async function fetchSettings() {
  const res = await fetch('/api/settings');
  if (!res.ok) return { ui_mode: 'light' };
  return res.json();
}

function getEntry(index) {
  if (index < 0 || index >= total) return null;
  return entries[index];
}

function isTextFile(entry) {
  const mimetype = entry.mimetype || '';
  return TEXT_FILE_MIME_PREFIXES.some((prefix) => mimetype.startsWith(prefix))
    || TEXT_FILE_MIME_TYPES.has(mimetype);
}

function isMarkdownFile(entry) {
  const mimetype = (entry.mimetype || '').toLowerCase();
  const filename = (entry.filename || '').toLowerCase();
  return MARKDOWN_MIME_TYPES.has(mimetype) || filename.endsWith('.md') || filename.endsWith('.markdown');
}

function decodeDataUrlText(dataUrl) {
  const match = dataUrl.match(/^data:([^;,]+)?;base64,(.*)$/s);
  if (!match) return null;
  try {
    return atob(match[2]);
  } catch {
    return null;
  }
}

function escapeHtml(text) {
  return text
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function parseInlineMarkdown(text) {
  const escaped = escapeHtml(text);
  return escaped
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/__([^_]+)__/g, '<strong>$1</strong>')
    .replace(/(^|[\s(])\*([^*]+)\*(?=[\s).,!?:;]|$)/g, '$1<em>$2</em>')
    .replace(/(^|[\s(])_([^_]+)_(?=[\s).,!?:;]|$)/g, '$1<em>$2</em>');
}

function looksLikeMarkdown(text) {
  const lines = text.replace(/\r\n?/g, '\n').split('\n');
  let score = 0;

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    if (/^#{1,6}\s+/.test(trimmed)) score += 2;
    if (/^[-*]\s+/.test(trimmed)) score += 2;
    if (/```/.test(trimmed)) score += 2;
    if (/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/.test(trimmed)) score += 2;
    if (/\*\*[^*]+\*\*/.test(trimmed) || /__[^_]+__/.test(trimmed)) score += 1;
    if (/(^|[\s(])\*[^*]+\*(?=[\s).,!?:;]|$)/.test(trimmed) || /(^|[\s(])_[^_]+_(?=[\s).,!?:;]|$)/.test(trimmed)) score += 1;
  }

  return score >= 2;
}

function renderMarkdown(markdown) {
  const lines = markdown.replace(/\r\n?/g, '\n').split('\n');
  const parts = [];
  let paragraph = [];
  let listItems = [];
  let codeLines = [];
  let inCodeBlock = false;

  function flushParagraph() {
    if (!paragraph.length) return;
    parts.push(`<p>${parseInlineMarkdown(paragraph.join(' '))}</p>`);
    paragraph = [];
  }

  function flushList() {
    if (!listItems.length) return;
    parts.push(`<ul>${listItems.map((item) => `<li>${parseInlineMarkdown(item)}</li>`).join('')}</ul>`);
    listItems = [];
  }

  function flushCodeBlock() {
    if (!codeLines.length) return;
    parts.push(`<pre><code>${escapeHtml(codeLines.join('\n'))}</code></pre>`);
    codeLines = [];
  }

  for (const line of lines) {
    if (line.startsWith('```')) {
      flushParagraph();
      flushList();
      if (inCodeBlock) {
        flushCodeBlock();
      }
      inCodeBlock = !inCodeBlock;
      continue;
    }

    if (inCodeBlock) {
      codeLines.push(line);
      continue;
    }

    const headingMatch = line.match(/^(#{1,6})\s+(.*)$/);
    if (headingMatch) {
      flushParagraph();
      flushList();
      const level = headingMatch[1].length;
      parts.push(`<h${level}>${parseInlineMarkdown(headingMatch[2].trim())}</h${level}>`);
      continue;
    }

    const listMatch = line.match(/^[-*]\s+(.*)$/);
    if (listMatch) {
      flushParagraph();
      listItems.push(listMatch[1].trim());
      continue;
    }

    if (!line.trim()) {
      flushParagraph();
      flushList();
      continue;
    }

    flushList();
    paragraph.push(line.trim());
  }

  flushParagraph();
  flushList();
  if (inCodeBlock) {
    flushCodeBlock();
  }

  return parts.join('');
}

function buildEntry(entry) {
  const wrap = document.createElement('div');
  wrap.className = 'entry';
  wrap.dataset.type = entry.type;
  wrap.classList.toggle('entry-full-page', FULL_TYPES.has(entry.type));

  const body = document.createElement('div');

  switch (entry.type) {
    case 'text': {
      if (looksLikeMarkdown(entry.content)) {
        body.className = 'entry-text entry-file-markdown';
        body.innerHTML = renderMarkdown(entry.content);
      } else {
        body.className = 'entry-text';
        body.textContent = entry.content;
      }
      break;
    }
    case 'quote': {
      body.className = 'entry-quote';
      body.textContent = entry.content;
      break;
    }
    case 'code': {
      body.className = 'entry-file entry-file-text';

      const header = document.createElement('div');
      header.className = 'entry-file-header';

      const name = document.createElement('div');
      name.className = 'entry-file-name';
      name.textContent = entry.filename || 'code';
      header.appendChild(name);

      body.appendChild(header);

      const preview = document.createElement('pre');
      preview.className = 'entry-code';
      preview.textContent = entry.content;
      body.appendChild(preview);
      break;
    }
    case 'link': {
      body.className = 'entry-link';
      const a = document.createElement('a');
      a.href = entry.content;
      a.target = '_blank';
      a.rel = 'noopener noreferrer';
      a.textContent = entry.content;
      body.appendChild(a);
      break;
    }
    case 'image': {
      const imgSize = entry.size || 'medium';
      body.className = `entry-image media-${imgSize}`;
      const img = document.createElement('img');
      img.src = entry.content;
      img.alt = entry.filename || '';
      body.appendChild(img);
      break;
    }
    case 'video': {
      const videoSize = entry.size || 'medium';
      body.className = `entry-video media-${videoSize}`;
      const video = document.createElement('video');
      video.src = entry.content;
      video.controls = true;
      body.appendChild(video);
      break;
    }
    case 'empty_page': {
      body.className = 'entry-empty-page';
      break;
    }
    case 'file': {
      if (isTextFile(entry)) {
        body.className = 'entry-file entry-file-text';

        const header = document.createElement('div');
        header.className = 'entry-file-header';

        const name = document.createElement('div');
        name.className = 'entry-file-name';
        name.textContent = entry.filename || 'file';
        header.appendChild(name);

        body.appendChild(header);

        const text = decodeDataUrlText(entry.content);
        if (text === null) {
          const preview = document.createElement('pre');
          preview.className = 'entry-file-preview';
          preview.textContent = '[unable to preview file]';
          body.appendChild(preview);
        } else if (isMarkdownFile(entry)) {
          const preview = document.createElement('div');
          preview.className = 'entry-file-preview entry-file-markdown';
          preview.innerHTML = renderMarkdown(text);
          body.appendChild(preview);
        } else {
          const preview = document.createElement('pre');
          preview.className = 'entry-file-preview';
          preview.textContent = text;
          body.appendChild(preview);
        }
      } else {
        body.className = 'entry-file';
        const a = document.createElement('a');
        a.href = entry.content;
        a.download = entry.filename || 'file';
        a.textContent = `[file] ${entry.filename || 'download'}`;
        body.appendChild(a);
      }
      break;
    }
  }

  wrap.appendChild(body);
  return wrap;
}

function emptyEl(msg) {
  const el = document.createElement('div');
  el.className = 'empty';
  el.textContent = msg;
  return el;
}

function setPageNumber(el, pageNumber) {
  if (pageNumber == null) {
    delete el.dataset.pageNumber;
    return;
  }
  el.dataset.pageNumber = String(pageNumber);
}

// Add a gap class to entries that follow an entry of a different type.
function applyBreaks(el) {
  let prevType = null;
  for (const entry of el.querySelectorAll('.entry')) {
    const t = entry.dataset.type;
    entry.classList.toggle('entry-break', prevType !== null && t !== prevType);
    entry.classList.toggle('entry-code-break', prevType === 'code' && t === 'code');
    entry.classList.toggle('entry-file-break', prevType === 'file' && t === 'file');
    prevType = t;
  }
}

// Greedily fill el with entries starting at startIndex.
// Full-page entries can only occupy an empty page by themselves.
// Returns the next index to place (first entry not placed on this page).
async function fillPage(el, startIndex) {
  el.replaceChildren();
  let index = startIndex;
  let placed = 0;

  while (index >= 0 && index < total) {
    const entry = getEntry(index);
    if (!entry) break;
    if (entry.type === 'page_break') {
      index++;
      if (placed > 0) break;
      continue;
    }
    if (FULL_TYPES.has(entry.type) && placed > 0) break;

    const node = buildEntry(entry);
    el.appendChild(node);

    // Reading scrollHeight forces a layout flush — detects overflow immediately
    if (el.scrollHeight > el.clientHeight) {
      el.removeChild(node);
      break;
    }

    placed++;
    index++;
    if (FULL_TYPES.has(entry.type)) break;
  }

  // If nothing fit (entry too tall to measure), force-show it anyway
  if (placed === 0 && index >= 0 && index < total) {
    const entry = getEntry(index);
    if (entry) {
      el.appendChild(buildEntry(entry));
      index++;
    }
  }

  return index; // first entry not placed on this page
}

function prefetch() {
  return;
}

async function render() {
  spread.firstIndex = current;

  const first = getEntry(current);

  // normal: fill left page then right page with as many entries as fit
  elLeft.className      = 'page';
  elRight.className     = 'page';
  elLeft.style.display  = '';
  elRight.style.display = '';
  elInfo.textContent = '';

  if (!first) {
    elLeft.replaceChildren(emptyEl('nothing here'));
    elRight.style.display = 'none';
    spread.lastIndex = current;
    setPageNumber(elLeft, history.length * 2 + 1);
    setPageNumber(elRight, null);
    btnPrev.disabled = history.length === 0;
    btnNext.disabled = true;
    return;
  }

  const leftPageNumber = history.length * 2 + 1;
  const rightPageNumber = leftPageNumber + 1;
  setPageNumber(elLeft, leftPageNumber);
  setPageNumber(elRight, rightPageNumber);

  const rightStart   = await fillPage(elLeft, current);
  applyBreaks(elLeft);
  const rightFirst   = getEntry(rightStart);

  if (!rightFirst) {
    elRight.replaceChildren();
    spread.lastIndex = rightStart - 1;
  } else {
    const afterRight = await fillPage(elRight, rightStart);
    applyBreaks(elRight);
    spread.lastIndex = afterRight - 1;
  }

  btnPrev.disabled = history.length === 0;
  btnNext.disabled = spread.lastIndex >= total - 1;

  prefetch();
}

async function go(dir) {
  if (dir > 0) {
    if (spread.lastIndex >= total - 1) return;
    history.push(current);
    current = spread.lastIndex + 1;
  } else {
    if (history.length === 0) return;
    current = history.pop();
  }
  await render();
}

btnPrev.addEventListener('click', () => go(-1));
btnNext.addEventListener('click', () => go(1));

document.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowLeft'  || e.key === 'ArrowUp')    go(-1);
  if (e.key === 'ArrowRight' || e.key === 'ArrowDown')  go(1);
});

async function init() {
  const settings = await fetchSettings();
  document.body.dataset.theme = settings.ui_mode || 'light';

  entries = await fetchEntries();
  total = entries.length;

  if (total === 0) {
    elLeft.replaceChildren(emptyEl('archive is empty\nadd something:\n2p "your text"'));
    elRight.style.display = 'none';
    setPageNumber(elLeft, null);
    setPageNumber(elRight, null);
    elInfo.textContent = '';
    btnPrev.disabled = true;
    btnNext.disabled = true;
    return;
  }

  await render();
}

init();
