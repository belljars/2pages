const elLeft  = document.getElementById('page-left');
const elRight = document.getElementById('page-right');
const elInfo  = document.getElementById('page-info');
const btnPrev = document.getElementById('prev');
const btnNext = document.getElementById('next');

// types that get a full spread to themselves
const FULL_TYPES = new Set(['image', 'video']);

let total   = 0;
let current = 1; // page number shown on the left (or alone)

// entries currently on screen — go() reads these instead of re-fetching
const spread = { left: null, right: null };

const pageCache = new Map();

async function fetchPage(n) {
  if (n < 1 || n > total) return null;
  if (pageCache.has(n)) return pageCache.get(n);
  const res = await fetch(`/api/page/${n}`);
  if (!res.ok) return null;
  const data = await res.json();
  pageCache.set(n, data);
  return data;
}

function fmt(iso) {
  return new Date(iso).toLocaleString(undefined, {
    year: 'numeric', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

function buildEntry(entry) {
  const wrap = document.createElement('div');

  const meta = document.createElement('div');
  meta.className = 'entry-meta';
  meta.textContent = fmt(entry.added_at);
  wrap.appendChild(meta);

  const body = document.createElement('div');

  switch (entry.type) {
    case 'text': {
      body.className = 'entry-text';
      body.textContent = entry.content;
      break;
    }
    case 'code': {
      body.className = 'entry-code';
      body.textContent = entry.content;
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
      body.className = 'entry-image';
      const img = document.createElement('img');
      img.src = entry.content;
      img.alt = entry.filename || '';
      body.appendChild(img);
      break;
    }
    case 'video': {
      body.className = 'entry-video';
      const video = document.createElement('video');
      video.src = entry.content;
      video.controls = true;
      body.appendChild(video);
      break;
    }
    case 'file': {
      body.className = 'entry-file';
      const a = document.createElement('a');
      a.href = entry.content;
      a.download = entry.filename || 'file';
      a.textContent = `[file] ${entry.filename || 'download'}`;
      body.appendChild(a);
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

function prefetch() {
  fetchPage(current - 1);
  fetchPage(current + 2);
  fetchPage(current + 3);
}

async function render() {
  const left = await fetchPage(current);

  // full-page type: occupy full spread
  if (left && FULL_TYPES.has(left.type)) {
    elLeft.className  = 'page full';
    elRight.className = 'page';
    elLeft.style.display  = '';
    elRight.style.display = 'none';

    elLeft.replaceChildren(buildEntry(left));
    elInfo.textContent = current;

    btnPrev.disabled = current <= 1;
    btnNext.disabled = current >= total;

    spread.left  = left;
    spread.right = null;
    prefetch();
    return;
  }

  // normal: show left + right side by side
  elLeft.className  = 'page';
  elRight.className = 'page';
  elLeft.style.display  = '';
  elRight.style.display = '';

  if (left) {
    elLeft.replaceChildren(buildEntry(left));
  } else {
    elLeft.replaceChildren(emptyEl('nothing here'));
  }

  const right = await fetchPage(current + 1);

  if (!right) {
    elRight.style.display = 'none';
    elInfo.textContent = current;
  } else if (FULL_TYPES.has(right.type)) {
    // right is full-type — it will render alone when navigated to
    elRight.replaceChildren(emptyEl('→'));
    elInfo.textContent = current;
  } else {
    elRight.replaceChildren(buildEntry(right));
    elInfo.textContent = `${current} ${current + 1}`;
  }

  btnPrev.disabled = current <= 1;
  btnNext.disabled = current >= total;

  spread.left  = left;
  spread.right = right;
  prefetch();
}

async function go(dir) {
  const isFull = spread.left && FULL_TYPES.has(spread.left.type);

  if (dir > 0) {
    if (isFull) {
      current = Math.min(total, current + 1);
    } else {
      if (!spread.right) return;
      current = FULL_TYPES.has(spread.right.type)
        ? current + 1
        : Math.min(total, current + 2);
    }
  } else {
    if (current <= 1) return;
    if (isFull) {
      current = current - 1;
    } else {
      const prev = await fetchPage(current - 1);
      if (!prev) return;
      current = FULL_TYPES.has(prev.type) ? current - 1 : Math.max(1, current - 2);
    }
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
  const res = await fetch('/api/count');
  const { count } = await res.json();
  total = count;

  if (total === 0) {
    elLeft.replaceChildren(emptyEl('archive is empty\nadd something:\n2p "your text"'));
    elRight.style.display = 'none';
    elInfo.textContent = '0';
    btnPrev.disabled = true;
    btnNext.disabled = true;
    return;
  }

  await render();
}

init();
