// ContentView.swift + EditorApp.swift + CustomTabBar.swift + WelcomeView.swift
// -> web karşılığı (uygulama kabuğu ve yönlendirme)
import { loc, L, allLanguages } from './i18n.js';
import { EDIParser } from './parser.js';
import { DocumentManager, createDocument } from './documentManager.js';
import { SyntaxHighlightEditor } from './editor.js';
import { renderSegmentDetail } from './segmentDetail.js';
import { logoManager } from './logoManager.js';
import { SAMPLE_CATALOG, sampleContent, sampleFileName } from './sampleData.js';
import { renderSamplePicker, lastSampleType, rememberSampleType } from './samplePicker.js';
import { initConsent, privacyURL, reopenConsent } from './consent.js';
import {
  convertMenuHTML, convertDocument, conversionErrorDialog,
  convertOptions, setConvertOption,
} from './convertPanel.js';
import { runSelfTest } from './convert.js';

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
  const isEDI = doc.language === 'edi';

  // EDI olmayan belgede mesaj tipi/standart tespiti anlamsız: EDIParser
  // JSON metnini de ayrıştırmaya çalışır ve "BİLİNMEYEN TÜR" der.
  editorNode.querySelector('.banner-title').textContent = isEDI
    ? EDIParser.detectMessageType(content)
    : L(`conv_lang_${doc.language}`);
  editorNode.querySelector('.pill.std').textContent = isEDI
    ? detectStandard(content)
    : doc.language.toUpperCase();

  const statusEl = editorNode.querySelector('.banner-status');
  statusEl.textContent = L('status_edited');
  statusEl.hidden = !doc.hasUnsavedChanges;

  // Round-trip rozeti — dönüşümle üretilmiş sekmelerde görünür
  const rtEl = editorNode.querySelector('.banner-roundtrip');
  if (doc.conversion) {
    rtEl.textContent = doc.conversion.ok ? L('conv_rt_ok') : L('conv_rt_warn');
    rtEl.className = `pill banner-roundtrip ${doc.conversion.ok ? 'ok' : 'warn'}`;
    rtEl.hidden = false;
  } else {
    rtEl.hidden = true;
  }

  editorNode.querySelector('.banner-lines').textContent =
    `${content.split('\n').length}${L('line_count_suffix')}`;
}

/** EDI referans bölümünün dile göre adresi */
function referenceURL() {
  return loc.currentLanguageCode === 'tr' ? 'edi/index.html' : 'edi/en/index.html';
}

/** Bilgi sayfalarının dile göre adresi (yalnızca TR ve EN sürümleri var) */
function aboutURL() {
  return loc.currentLanguageCode === 'tr' ? 'hakkinda.html' : 'about.html';
}

function contactURL() {
  return loc.currentLanguageCode === 'tr' ? 'iletisim.html' : 'contact.html';
}

function termsURL() {
  return loc.currentLanguageCode === 'tr' ? 'kosullar.html' : 'terms.html';
}

/** Mesaj tipine göre PDF / Excel izinleri */
function getExportPermissions() {
  const doc = docManager.activeDocument;
  if (!doc || doc.isStartPage) return { pdf: false, excel: false };
  // İçinde "ORDERS" geçen bir JSON metni de bu testlerden geçerdi; üreticiler
  // ise EDIParser çıktısı bekliyor. Dışa aktarma yalnızca EDI belgelerinde.
  if (doc.language !== 'edi') return { pdf: false, excel: false };

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
  // JSON çıktısı içinde "EDIFACT" dizgesi geçer; standardı içerikten tahmin
  // etmek yalnızca EDI belgelerinde doğru sonuç verir.
  $('#win-sub').textContent = !hasDoc
    ? ''
    : doc.language === 'edi'
      ? detectStandard(doc.content)
      : doc.language.toUpperCase();
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

  // Dönüşüm menüsü (EDI <-> JSON <-> XML)
  $('#btn-convert').title = L('conv_title');
  $('#convert-popup').innerHTML = convertMenuHTML(docManager.activeDocument);

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
          <a href="${aboutURL()}">${esc(L('menu_about_page'))}</a>
          <a href="${contactURL()}">${esc(L('contact_page'))}</a>
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
  renderedDocID = doc.id;
  editorView.setLanguage(doc.language);
  editorView.setText(doc.content);

  // BANNER
  updateBanner(doc);

  // DETAY PANELİ
  renderDetailFor(doc);
}

/**
 * Detay panelini çizer. Segment analizi yalnızca EDI belgelerinde anlamlıdır;
 * JSON/XML sekmelerinde seçili satır bir segment değildir.
 */
function renderDetailFor(doc) {
  const panel = editorNode.querySelector('.detail-panel');
  renderSegmentDetail(
    panel,
    doc.language === 'edi' ? doc.selectedLineContent : '',
    doc.language === 'edi' ? findCurrency(doc.content) : ''
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
          <span class="pill banner-roundtrip" hidden></span>
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
      renderDetailFor(doc);
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

  $('#convert-popup').addEventListener('click', (e) => {
    const opt = e.target.closest('[data-convert-opt]');
    if (opt) {
      // Seçenek değişince menü açık kalsın: kullanıcı genelde iki kutuyu da
      // ayarlayıp sonra hedefe basıyor.
      e.stopPropagation();
      const name = opt.dataset.convertOpt;
      setConvertOption(name, !convertOptions[name]);
      $('#convert-popup').innerHTML = convertMenuHTML(docManager.activeDocument);
      return;
    }
    const target = e.target.closest('[data-convert-to]');
    if (target) runConversion(target.dataset.convertTo);
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
    else if (e.target.closest('#welcome-sample')) openSamplePicker();
  });

  // --- Örnek seçim ekranı ---
  $('#sample-picker-cancel').addEventListener('click', closeSamplePicker);
  $('#sample-backdrop').addEventListener('click', (e) => {
    // Boşluğa tıklayınca kapansın, kartın üstüne tıklayınca değil
    if (e.target === $('#sample-backdrop')) {
      closeSamplePicker();
      return;
    }
    const card = e.target.closest('[data-sample-type]');
    if (!card) return;
    const type = card.dataset.sampleType;
    rememberSampleType(type);
    closeSamplePicker();
    openSampleDocument(type);
  });

  // --- Klavye kısayolları (CommandGroup karşılığı) ---
  window.addEventListener('keydown', (e) => {
    const mod = e.metaKey || e.ctrlKey;
    if (!mod) {
      if (e.key === 'Escape' && !$('#sample-backdrop').hidden) {
        closeSamplePicker();
        return;
      }
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
  docManager.addEventListener('change', () => {
    render();
    maybeOfferConversion();
  });
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
      { label: L('menu_about_page'), action: () => window.open(aboutURL(), '_blank', 'noopener') },
      { label: L('contact_page'), action: () => window.open(contactURL(), '_blank', 'noopener') },
      { label: L('terms_of_use'), action: () => window.open(termsURL(), '_blank', 'noopener') },
      { label: L('privacy_policy'), action: () => window.open(privacyURL(), '_blank', 'noopener') },
      // Rıza ekranı her zaman açılabilir: Google'ın CMP'si varsa o, yoksa
      // ölçüm izni soran yedek bant gösterilir.
      { label: L('consent_manage'), action: () => reopenConsent() },
    ],
  });
}

// =========================================================================
// MARK: - DÖNÜŞÜM
// =========================================================================

/** Aktif belgeyi hedef biçime çevirir ve sonucu yeni bir sekmede açar. */
function runConversion(target) {
  const doc = docManager.activeDocument;
  if (!doc || doc.isStartPage) return;

  let result;
  try {
    result = convertDocument(doc, target);
  } catch (e) {
    showDialog({
      ...conversionErrorDialog(e),
      buttons: [{ label: L('btn_cancel'), kind: 'default' }],
    });
    return;
  }

  const newDoc = createDocument({
    content: result.content,
    fileName: result.fileName,
    isStartPage: false,
    language: result.language,
    conversion: result.conversion,
  });
  // Sonuç yalnızca bellekte: sekme "kaydedilmemiş" görünsün ki kapatılırken
  // sorulsun ve kullanıcı çıktıyı diske almayı unutmasın.
  newDoc.originalContent = '';

  docManager.tabs.push(newDoc);
  docManager.activeTabID = newDoc.id;
  docManager.changed();

  // Kayıpsızlık doğrulanamadıysa sessiz geçme
  if (!result.conversion.ok) {
    showDialog({
      icon: '⚠️',
      title: L('conv_rt_warn_title'),
      message: L('conv_rt_warn_msg'),
      buttons: [{ label: L('btn_cancel'), kind: 'default' }],
    });
  }
}

/** Şemamıza ait bir JSON/XML açıldıysa EDI'ye çevirmeyi teklif eder. */
async function maybeOfferConversion() {
  const doc = docManager.pendingConvertOffer;
  if (!doc) return;
  docManager.pendingConvertOffer = null;

  const accepted = await askDialog({
    icon: '🔄',
    title: L('conv_open_title'),
    message: L('conv_open_msg'),
    buttons: [
      { label: L('conv_btn_convert'), kind: 'default', value: true },
      { label: L('btn_cancel'), value: false },
    ],
  });
  if (!accepted) return;

  // Diyalog açıkken sekme kapatılmış olabilir
  if (!docManager.tabs.some((t) => t.id === doc.id)) return;
  docManager.activeTabID = doc.id;
  runConversion('edi');
}

// =========================================================================
// MARK: - ÖRNEK DOSYA
// =========================================================================

/** Seçilen mesaj tipinin örneğini yeni bir sekmede açar ve ilk segmenti seçer. */
function openSampleDocument(type = lastSampleType()) {
  const content = sampleContent(type);
  const doc = createDocument({
    content,
    fileName: sampleFileName(type),
    isStartPage: false,
  });
  // İlk satır seçili gelsin ki detay paneli boş görünmesin
  doc.selectedLineContent = content.split('\n')[0].trim();

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

/** Örnek seçim ekranını açar. */
function openSamplePicker() {
  $('#sample-picker-title').textContent = L('sample_picker_title');
  $('#sample-picker-desc').textContent = L('sample_picker_desc');
  $('#sample-picker-cancel').textContent = L('btn_cancel');
  renderSamplePicker($('#sample-picker-body'), lastSampleType());
  $('#sample-backdrop').hidden = false;

  const body = $('#sample-picker-body');
  body.scrollTop = 0;

  // Panel `hidden` kalkar kalkmaz henüz yerleşmemiş oluyor; o anda ölçülen
  // geometri yanlış çıkar ve liste kendiliğinden kayar. Bu yüzden odaklanma
  // bir sonraki kareye bırakılır: `nearest` o noktada zaten görünen kartı
  // oynatmaz, aşağıda kalan kartı görünür yapar.
  const active = body.querySelector('.sample-card.active') || body.querySelector('.sample-card');
  if (!active) return;
  requestAnimationFrame(() => {
    body.scrollTop = 0;
    active.focus({ preventScroll: true });
    active.scrollIntoView({ block: 'nearest' });
  });
}

function closeSamplePicker() {
  $('#sample-backdrop').hidden = true;
}

// =========================================================================
// MARK: - BAŞLATMA
// =========================================================================
(async function main() {
  // Consent Mode varsayılanları gtag.js'ten önce tanımlanmalı, o yüzden en başta.
  initConsent({ ads: true });

  applyTheme();
  await loc.loadTranslations();
  document.documentElement.lang = loc.currentLanguageCode;

  wireEvents();

  // Açılışta boş hoşgeldin ekranı yerine örnek dosya yüklü bir sekme
  openSampleDocument();
  render();

  // Derleme adımı yok, bu yüzden test koşucusu da yok: dönüşüm modülünün
  // kayıpsızlık sınaması ?selftest=1 ile tarayıcıda çalışır.
  if (new URLSearchParams(location.search).has('selftest')) showSelfTest();
})();

/** ?selftest=1 — dönüşüm yollarını gömülü örneklerin TAMAMIYLA sınar. */
function showSelfTest() {
  const samples = Object.fromEntries(SAMPLE_CATALOG.map((s) => [s.type, s.content]));
  const results = runSelfTest(samples);
  const failed = results.filter((r) => !r.ok);

  console.table(results);
  showDialog({
    icon: failed.length ? '⚠️' : '✅',
    title: `Self-test: ${results.length - failed.length}/${results.length}`,
    message: failed.length
      ? failed.map((r) => `${r.name}: ${r.note}`).join('\n')
      : 'Tüm dönüşümler baytı baytına geri geldi.',
    buttons: [{ label: L('btn_cancel'), kind: 'default' }],
  });
}
