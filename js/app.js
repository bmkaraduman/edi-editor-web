// ContentView.swift + EditorApp.swift + CustomTabBar.swift + WelcomeView.swift
// -> web karşılığı (uygulama kabuğu ve yönlendirme)
import { loc, L, allLanguages } from './i18n.js';
import { EDIParser } from './parser.js';
import { DocumentManager, createDocument } from './documentManager.js';
import { SyntaxHighlightEditor } from './editor.js';
import { renderSegmentDetail } from './segmentDetail.js';
import { logoManager } from './logoManager.js';
import { SAMPLE_EDI, SAMPLE_FILE_NAME } from './sampleData.js';
import { initConsent, privacyURL, reopenConsent, consentUIAvailable } from './consent.js';

// =========================================================================
// MARK: - TEMA SEÇENEKLERİ (AppTheme)
// =========================================================================
const AppTheme = {
  system: 'system',
  light: 'light',
  dark: 'dark',
};

const themeLocalizedName = (t) => L(`theme_${t}`);

const THEME_KEY = 'selectedAppTheme';
let selectedTheme = localStorage.getItem(THEME_KEY) || AppTheme.system;

function applyTheme() {
  document.documentElement.setAttribute('data-theme', selectedTheme);
  const icons = {
    [AppTheme.system]: '<svg viewBox="0 0 24 24" class="ic"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M12 3a9 9 0 0 0 0 18z" fill="currentColor"/></svg>',
    [AppTheme.light]: '<svg viewBox="0 0 24 24" class="ic"><circle cx="12" cy="12" r="4.2" fill="currentColor"/><g stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><path d="M12 2.5v2.2M12 19.3v2.2M2.5 12h2.2M19.3 12h2.2M5.2 5.2l1.6 1.6M17.2 17.2l1.6 1.6M18.8 5.2l-1.6 1.6M6.8 17.2l-1.6 1.6"/></g></svg>',
    [AppTheme.dark]: '<svg viewBox="0 0 24 24" class="ic"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5z" fill="currentColor"/></svg>',
  };
  $('#theme-icon').innerHTML = icons[selectedTheme];
}

// =========================================================================
// MARK: - KISA YOLLAR
// =========================================================================
const $ = (sel) => document.querySelector(sel);
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

const docManager = new DocumentManager();

// Editör görünümü kalıcı tutulur (sekme değişiminde odak/scroll kaybı olmasın)
let editorView = null;
let editorNode = null;
let renderedDocID = null;

// =========================================================================
// MARK: - YARDIMCI FONKSİYONLAR (ContentView)
// =========================================================================

function isStartPageOrEmpty() {
  if (docManager.tabs.length === 0) return true;
  const doc = docManager.activeDocument;
  return doc ? doc.isStartPage : true;
}

function currentTitle() {
  const doc = docManager.activeDocument;
  if (doc) return (doc.hasUnsavedChanges ? '● ' : '') + doc.fileName;
  return L('default_window_title');
}

/** CUX segmentinden para birimini bulur */
function findCurrency(fullContent) {
  const lines = fullContent.split("'");
  const cuxLine = lines.find((l) => l.includes('CUX'));
  if (cuxLine) {
    const parts = cuxLine.split('+');
    if (parts.length > 1) {
      const subParts = parts[1].split(':');
      if (subParts.length > 1) return subParts[1];
    }
  }
  return '';
}

/** İçeriğe göre EDI standardı (EdiModels.swift EDIStandard.displayTitle karşılığı) */
function detectStandard(content) {
  if (content.includes('ISA*') || content.includes('GS*') || content.includes('ST*')) {
    return 'ANSI ASC X12';
  }
  if (content.includes('UNB') || content.includes('UNH+') || content.includes('UNA')) {
    return 'UN/EDIFACT';
  }
  return L('edi_std_unknown');
}

/** Banner alanlarını doldurur (hem ilk çizimde hem yazarken kullanılır) */
function updateBanner(doc) {
  if (!editorNode || !doc) return;
  const content = doc.content;

  editorNode.querySelector('.banner-title').textContent = EDIParser.detectMessageType(content);
  editorNode.querySelector('.pill.std').textContent = detectStandard(content);

  const statusEl = editorNode.querySelector('.banner-status');
  statusEl.textContent = L('status_edited');
  statusEl.hidden = !doc.hasUnsavedChanges;

  editorNode.querySelector('.banner-lines').textContent =
    `${content.split('\n').length}${L('line_count_suffix')}`;
}

/** EDI referans bölümünün dile göre adresi */
function referenceURL() {
  return loc.currentLanguageCode === 'tr' ? 'edi/index.html' : 'edi/en/index.html';
}

/** Mesaj tipine göre PDF / Excel izinleri */
function getExportPermissions() {
  const doc = docManager.activeDocument;
  if (!doc || doc.isStartPage) return { pdf: false, excel: false };

  const content = doc.content;
  if (content.includes('SLSRPT')) return { pdf: true, excel: true };
  if (content.includes('PRICAT')) return { pdf: false, excel: true };

  const pdfGroup = ['ORDERS', 'ORDRSP', 'ORDCHG', 'DESADV', 'RECADV', 'IFTMIN', 'INVOIC', 'REMADV', 'DELJIT'];
  for (const type of pdfGroup) {
    if (content.includes(type)) return { pdf: true, excel: false };
  }
  return { pdf: false, excel: false };
}

// =========================================================================
// MARK: - DİYALOGLAR (Alert / confirmationDialog karşılığı)
// =========================================================================
function showDialog({ icon = '⚠️', title, message = '', buttons }) {
  $('#dlg-icon').textContent = icon;
  $('#dlg-title').textContent = title;
  $('#dlg-msg').textContent = message;

  const box = $('#dlg-buttons');
  box.innerHTML = '';
  for (const b of buttons) {
    const el = document.createElement('button');
    el.className = 'dlg-btn' + (b.kind ? ` ${b.kind}` : '');
    el.textContent = b.label;
    el.addEventListener('click', () => {
      closeDialog();
      if (b.action) b.action();
    });
    box.appendChild(el);
  }
  $('#backdrop').hidden = false;
  const first = box.querySelector('.dlg-btn.default') || box.querySelector('.dlg-btn');
  if (first) first.focus();
}

function closeDialog() {
  $('#backdrop').hidden = true;
}

/** Diyaloğu Promise olarak sunar; seçilen butonun `value`'su döner. */
function askDialog(opts) {
  return new Promise((resolve) => {
    showDialog({
      ...opts,
      buttons: opts.buttons.map((b) => ({ ...b, action: () => resolve(b.value) })),
    });
  });
}

/** Sekme kapatma isteği (CustomTabBar -> ContentView akışı) */
async function requestCloseTab(id) {
  const tab = docManager.tabs.find((t) => t.id === id);
  if (!tab) return;

  // DEĞİŞİKLİK YOKSA -> DİREKT KAPAT
  if (!tab.hasUnsavedChanges) {
    docManager.closeTab(id);
    return;
  }

  // KAYDEDİLMEMİŞ DEĞİŞİKLİK VARSA -> SOR
  const choice = await askDialog({
    title: L('alert_unsaved_title'),
    message: L('alert_unsaved_msg'),
    buttons: [
      { label: L('btn_save'), kind: 'default', value: 'save' },
      { label: L('btn_discard'), kind: 'destructive', value: 'discard' },
      { label: L('btn_cancel'), value: 'cancel' },
    ],
  });

  if (choice === 'discard') {
    docManager.closeTab(id);
  } else if (choice === 'save') {
    docManager.activeTabID = id;
    // Kaydetme iptal edilirse sekme açık kalır (veri kaybı olmasın)
    const saved = await docManager.initiateSave();
    if (saved) docManager.closeTab(id);
    else docManager.changed();
  }
}

// DocumentManager'ın kaydetme akışındaki uyarıları (true = btn_yes)
docManager.presentAlert = (kind) => {
  if (kind === 'invalidFormat') {
    return askDialog({
      title: L('alert_format_title'),
      message: L('alert_format_msg'),
      buttons: [
        { label: L('btn_yes'), kind: 'default', value: true },
        { label: L('btn_cancel'), value: false },
      ],
    });
  }
  // txtConversion
  return askDialog({
    icon: '📄',
    title: 'Format',
    message: '.txt -> .edi',
    buttons: [
      { label: L('btn_yes'), kind: 'default', value: true },
      { label: L('btn_cancel'), value: false },
    ],
  });
};

// =========================================================================
// MARK: - RENDER
// =========================================================================

function render() {
  renderToolbar();
  renderTabBar();
  renderContent();

  updateTitle();
}

/** Ürün adı — marka olduğu için çevrilmez */
const APP_NAME = 'ediviewer';

/** Pencere başlığı + alt satır */
function updateTitle() {
  const doc = docManager.activeDocument;
  const hasDoc = !!doc && !doc.isStartPage;

  // Dosya açık değilken başlık alanı boş kalır; markayı logo zaten taşıyor
  $('#win-title').textContent = hasDoc ? currentTitle() : '';
  $('#win-sub').textContent = hasDoc ? detectStandard(doc.content) : '';
  $('#brand-sep').hidden = !hasDoc;
  $('#title-group').hidden = !hasDoc;

  // Sekme başlığında marka da görünsün
  document.title = hasDoc ? `${currentTitle()} — ${APP_NAME}` : APP_NAME;
}

// --- TOOLBAR ---
function renderToolbar() {
  // Statik metinler
  document.querySelectorAll('[data-i18n]').forEach((el) => {
    el.textContent = L(el.dataset.i18n);
  });

  $('#btn-open').title = L('open_file');
  $('#btn-save').title = L('save');
  $('#btn-about').title = L('menu_about');
  $('#btn-logo').title = L('add_logo');
  $('#menu-theme [data-menu-trigger]').title = L('help_theme_change');

  const startOrEmpty = isStartPageOrEmpty();
  const permissions = getExportPermissions();

  $('#btn-save').disabled = startOrEmpty;
  $('#btn-pdf').disabled = startOrEmpty || !permissions.pdf;
  $('#btn-excel').disabled = startOrEmpty || !permissions.excel;

  // Tema menüsü (Picker .inline karşılığı)
  $('#theme-popup').innerHTML =
    `<div class="menu-header">${esc(L('menu_theme'))}</div>` +
    Object.values(AppTheme)
      .map((t) => `
        <button class="menu-item" data-theme-opt="${t}">
          <span class="menu-check">${selectedTheme === t ? '✓' : ''}</span>
          <span>${esc(themeLocalizedName(t))}</span>
        </button>`)
      .join('');

  // Dil menüsü
  $('#lang-popup').innerHTML = allLanguages
    .map((lang) => `
      <button class="menu-item" data-lang-opt="${lang.code}">
        <span class="menu-check">${loc.currentLanguageCode === lang.code ? '✓' : ''}</span>
        <span>${esc(lang.name)}</span>
      </button>`)
    .join('');

  // Logo
  $('#logo-slot').innerHTML = logoManager.companyLogo
    ? `<img class="logo-img" src="${logoManager.companyLogo}" alt="logo">`
    : '<svg viewBox="0 0 24 24" class="ic"><rect x="3" y="5" width="14" height="12" rx="2" fill="none" stroke="currentColor" stroke-width="1.6"/><circle cx="8" cy="9.5" r="1.3" fill="currentColor"/><path d="m4.5 15 3.6-3.4 3 2.6 2.3-2 3.1 2.8" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/><path d="M19 15v6M16 18h6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>';
}

// --- TAB BAR ---
function renderTabBar() {
  const wrap = $('#tabbar-wrap');
  wrap.hidden = docManager.tabs.length === 0;
  if (wrap.hidden) return;

  const bar = $('#tabbar');
  bar.innerHTML =
    docManager.tabs
      .map((tab) => `
        <div class="tab${docManager.activeTabID === tab.id ? ' active' : ''}" data-tab="${tab.id}">
          <span class="tab-name" data-select="${tab.id}">${esc(tab.fileName)}</span>
          ${tab.hasUnsavedChanges ? '<span class="tab-dot"></span>' : ''}
          <button class="tab-close" data-close="${tab.id}" aria-label="close">✕</button>
        </div>`)
      .join('') + '<button class="tab-add" id="tab-add" aria-label="new tab">+</button>';
}

// --- ANA İÇERİK ---
function renderContent() {
  const content = $('#content');
  const doc = docManager.activeDocument;

  // Hiç sekme yoksa veya başlangıç sayfasıysa -> HOŞGELDİN EKRANI
  if (!doc || doc.isStartPage) {
    renderedDocID = null;
    content.innerHTML = `
      <div class="welcome">
        <div class="brand-logo xl"><span class="lg-a">edi</span><span class="lg-b">viewer</span></div>
        <div class="welcome-title">${esc(L('welcome_title'))}</div>
        <div class="welcome-sub">EDIFACT &amp; ANSI X12 &middot; ${esc(L('pdf_export'))} &middot; ${esc(L('btn_excel'))}</div>
        <div class="welcome-buttons">
          <button class="btn-large prominent" id="welcome-open">
            <svg viewBox="0 0 24 24" class="ic"><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></svg>
            <span>${esc(L('open_file'))}</span>
          </button>
          <button class="btn-large" id="welcome-new">
            <svg viewBox="0 0 24 24" class="ic"><rect x="4" y="4" width="16" height="16" rx="3" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M12 8.5v7M8.5 12h7" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>
            <span>${esc(L('new_file'))}</span>
          </button>
          <button class="btn-large" id="welcome-sample">
            <svg viewBox="0 0 24 24" class="ic"><path d="M6 3h8l4 4v14a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/><path d="M14 3v4h4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/><path d="M8 13h8M8 16.5h5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
            <span>${esc(L('sample_file'))}</span>
          </button>
        </div>
        <div class="welcome-hint">
          <span>${esc(L('welcome_hint'))}</span>
        </div>
        <div class="welcome-links">
          <a href="${referenceURL()}">${esc(L('edi_reference'))}</a>
        </div>
      </div>`;
    return;
  }

  // --- EDİTÖR GÖRÜNÜMÜ ---
  if (!editorNode) buildEditorNode();
  if (content.firstChild !== editorNode) {
    content.innerHTML = '';
    content.appendChild(editorNode);
  }

  // Sekme değiştiyse metni ve seçimi tazele
  if (renderedDocID !== doc.id) {
    renderedDocID = doc.id;
    editorView.setText(doc.content);
  } else {
    editorView.setText(doc.content);
  }

  // BANNER
  updateBanner(doc);

  // DETAY PANELİ
  renderSegmentDetail(
    editorNode.querySelector('.detail-panel'),
    doc.selectedLineContent,
    findCurrency(doc.content)
  );
}

function buildEditorNode() {
  editorNode = document.createElement('div');
  editorNode.className = 'editor-view';
  editorNode.style.cssText = 'display:flex; flex-direction:column; flex:1 1 auto; min-height:0;';
  editorNode.innerHTML = `
    <div class="banner">
      <div class="banner-badge">
        <svg viewBox="0 0 24 24" class="ic"><path d="M6 3h8l4 4v14a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/><path d="M14 3v4h4" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/><path d="M8.5 13h7M8.5 16.5h4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>
      </div>
      <div class="banner-text">
        <div class="banner-title"></div>
        <div class="banner-meta">
          <span class="pill std"></span>
          <span class="pill edited banner-status" hidden></span>
        </div>
      </div>
      <div class="banner-right">
        <span class="banner-lines"></span>
      </div>
    </div>
    <div class="split">
      <div class="split-top"><div class="editor-wrap"></div></div>
      <div class="splitter" title="Resize"></div>
      <div class="split-bottom"><div class="detail-panel"></div></div>
    </div>`;

  editorView = new SyntaxHighlightEditor(editorNode.querySelector('.editor-wrap'), {
    onInput: (text) => {
      const doc = docManager.activeDocument;
      if (!doc) return;
      doc.content = text;
      // Editörün kendi metnini geri yazmadan sadece çevre UI'ı tazele
      updateChromeOnly();
    },
    onSelectLine: (line) => {
      const doc = docManager.activeDocument;
      if (!doc || doc.selectedLineContent === line) return;
      doc.selectedLineContent = line;
      renderSegmentDetail(
        editorNode.querySelector('.detail-panel'),
        line,
        findCurrency(doc.content)
      );
    },
  });

  setupSplitter(editorNode.querySelector('.splitter'), editorNode.querySelector('.split-bottom'));
}

/** Yazarken editörün içeriğine dokunmadan başlık/sekme/buton durumlarını günceller */
function updateChromeOnly() {
  const doc = docManager.activeDocument;
  if (!doc || !editorNode) return;

  updateBanner(doc);
  renderToolbar();
  renderTabBar();
  updateTitle();
}

// --- VSplitView sürükleme ---
function setupSplitter(splitter, bottom) {
  let dragging = false;
  splitter.addEventListener('mousedown', (e) => {
    dragging = true;
    e.preventDefault();
    document.body.style.cursor = 'row-resize';
  });
  window.addEventListener('mousemove', (e) => {
    if (!dragging) return;
    const split = splitter.parentElement;
    const rect = split.getBoundingClientRect();
    const height = rect.bottom - e.clientY;
    const max = rect.height - 200; // split-top min-height
    bottom.style.flexBasis = `${Math.max(150, Math.min(height, max))}px`;
  });
  window.addEventListener('mouseup', () => {
    if (!dragging) return;
    dragging = false;
    document.body.style.cursor = '';
  });
}

// =========================================================================
// MARK: - OLAY BAĞLAMA
// =========================================================================

function wireEvents() {
  // --- Toolbar butonları ---
  $('#btn-open').addEventListener('click', () => docManager.openDocument());
  $('#btn-save').addEventListener('click', () => docManager.initiateSave());
  $('#btn-pdf').addEventListener('click', () => docManager.exportCurrentDocumentToPDF());
  $('#btn-excel').addEventListener('click', () => docManager.prepareCSVExport());
  $('#btn-logo').addEventListener('click', () => logoManager.selectAndSaveLogo());
  $('#btn-about').addEventListener('click', showAbout);

  // --- Menüler ---
  document.querySelectorAll('[data-menu-trigger]').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const menu = btn.closest('.menu');
      const wasOpen = menu.classList.contains('open');
      document.querySelectorAll('.menu.open').forEach((m) => m.classList.remove('open'));
      if (!wasOpen) menu.classList.add('open');
    });
  });
  document.addEventListener('click', () => {
    document.querySelectorAll('.menu.open').forEach((m) => m.classList.remove('open'));
  });

  $('#theme-popup').addEventListener('click', (e) => {
    const opt = e.target.closest('[data-theme-opt]');
    if (!opt) return;
    selectedTheme = opt.dataset.themeOpt;
    localStorage.setItem(THEME_KEY, selectedTheme);
    applyTheme();
    render();
  });

  $('#lang-popup').addEventListener('click', async (e) => {
    const opt = e.target.closest('[data-lang-opt]');
    if (!opt) return;
    await loc.setLanguage(opt.dataset.langOpt);
  });

  // --- Tab bar (delegasyon) ---
  $('#tabbar').addEventListener('click', (e) => {
    const close = e.target.closest('[data-close]');
    if (close) {
      requestCloseTab(close.dataset.close);
      return;
    }
    const add = e.target.closest('#tab-add');
    if (add) {
      docManager.addNewTab();
      return;
    }
    const tab = e.target.closest('[data-tab]');
    if (tab) {
      docManager.activeTabID = tab.dataset.tab;
      docManager.changed();
    }
  });

  // --- Hoşgeldin ekranı butonları (delegasyon) ---
  $('#content').addEventListener('click', (e) => {
    if (e.target.closest('#welcome-open')) docManager.openDocument();
    else if (e.target.closest('#welcome-new')) docManager.createNewEditorTab();
    else if (e.target.closest('#welcome-sample')) openSampleDocument();
  });

  // --- Klavye kısayolları (CommandGroup karşılığı) ---
  window.addEventListener('keydown', (e) => {
    const mod = e.metaKey || e.ctrlKey;
    if (!mod) {
      // Escape -> son buton (her diyalogda "İptal") tetiklenir
      if (e.key === 'Escape' && !$('#backdrop').hidden) {
        const btns = $('#dlg-buttons').querySelectorAll('.dlg-btn');
        if (btns.length) btns[btns.length - 1].click();
      }
      return;
    }
    const k = e.key.toLowerCase();
    if (k === 'n') { e.preventDefault(); docManager.addNewTab(); }
    else if (k === 'o') { e.preventDefault(); docManager.openDocument(); }
    else if (k === 's') {
      e.preventDefault();
      if (e.shiftKey) docManager.saveAsDocument();
      else docManager.initiateSave();
    }
    else if (k === 'w') {
      e.preventDefault();
      if (docManager.activeTabID) requestCloseTab(docManager.activeTabID);
    }
  });

  // --- Sürükle-bırak ile dosya açma ---
  const content = $('#content');
  ['dragenter', 'dragover'].forEach((ev) =>
    content.addEventListener(ev, (e) => {
      e.preventDefault();
      content.classList.add('drag-over');
    })
  );
  ['dragleave', 'drop'].forEach((ev) =>
    content.addEventListener(ev, (e) => {
      e.preventDefault();
      content.classList.remove('drag-over');
    })
  );
  content.addEventListener('drop', (e) => {
    const files = Array.from(e.dataTransfer?.files || []);
    if (files.length) docManager.openFiles(files);
  });

  // --- windowShouldClose karşılığı ---
  window.addEventListener('beforeunload', (e) => {
    if (docManager.hasUnsavedChanges) {
      e.preventDefault();
      e.returnValue = '';
    }
  });

  // --- Yeniden çizim tetikleyicileri ---
  docManager.addEventListener('change', render);
  logoManager.addEventListener('change', renderToolbar);
  loc.addEventListener('change', () => {
    document.documentElement.lang = loc.currentLanguageCode;
    render();
  });
}

function showAbout() {
  showDialog({
    icon: '📄',
    title: APP_NAME,
    message: 'EDIFACT / ANSI X12 viewer & editor',
    buttons: [
      { label: L('btn_cancel'), kind: 'default', action: () => {} },
      { label: L('edi_reference'), action: () => window.open(referenceURL(), '_blank', 'noopener') },
      { label: L('privacy_policy'), action: () => window.open(privacyURL(), '_blank', 'noopener') },
      // Rıza ekranı yalnızca Google'ın CMP'sinin yüklendiği bölgelerde vardır;
      // aksi hâlde düğme hiçbir şey yapmayacağı için hiç gösterilmez.
      ...(consentUIAvailable()
        ? [{ label: L('consent_manage'), action: () => reopenConsent() }]
        : []),
    ],
  });
}

// =========================================================================
// MARK: - ÖRNEK DOSYA
// =========================================================================

/** Örnek EDI dosyasını yeni bir sekmede açar ve ilk segmenti seçer. */
function openSampleDocument() {
  const doc = createDocument({
    content: SAMPLE_EDI,
    fileName: SAMPLE_FILE_NAME,
    isStartPage: false,
  });
  // İlk satır seçili gelsin ki detay paneli boş görünmesin
  doc.selectedLineContent = SAMPLE_EDI.split('\n')[0].trim();

  const active = docManager.activeDocument;
  if (active && active.isStartPage) {
    // Boş başlangıç sekmesi varsa onu kullan
    const i = docManager.activeDocumentIndex;
    docManager.tabs[i] = doc;
  } else {
    docManager.tabs.push(doc);
  }
  docManager.activeTabID = doc.id;
  docManager.changed();
}

// =========================================================================
// MARK: - BAŞLATMA
// =========================================================================
(async function main() {
  // Consent Mode varsayılanları gtag.js'ten önce tanımlanmalı, o yüzden en başta.
  // Editörde reklam yüklenmez: sayfa tam ekran ve kaydırmasız, Auto Ads'in
  // yerleştireceği akış yok. Reklamlar içerik sayfalarında (edi/**) çalışır.
  initConsent({ ads: false });

  applyTheme();
  await loc.loadTranslations();
  document.documentElement.lang = loc.currentLanguageCode;

  wireEvents();

  // Açılışta boş hoşgeldin ekranı yerine örnek dosya yüklü bir sekme
  openSampleDocument();
  render();
})();
