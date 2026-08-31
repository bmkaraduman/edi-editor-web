// SyntaxHighlightEditor.swift -> web karşılığı
// NSTextView + textStorage attribute'ları yerine:
// şeffaf <textarea> + altında birebir hizalı <pre> vurgu katmanı + satır no cetveli.

/** Tüm katmanlarda birebir aynı olmak zorunda (px). CSS ile senkron tutulur. */
const LINE_HEIGHT = 21;

export class SyntaxHighlightEditor {
  /**
   * @param {HTMLElement} root  .editor-wrap konteyneri
   * @param {{onInput:(text:string)=>void, onSelectLine:(line:string)=>void}} handlers
   */
  constructor(root, handlers) {
    this.root = root;
    this.handlers = handlers;
    this._activeLine = -1;
    /** 'edi' | 'json' | 'xml' — vurgulama kuralını seçer */
    this._language = 'edi';

    root.innerHTML = `
      <div class="editor-gutter" aria-hidden="true"><div class="editor-gutter-inner"></div></div>
      <div class="editor-scroll">
        <div class="editor-activeline" aria-hidden="true"></div>
        <pre class="editor-highlight" aria-hidden="true"><code></code></pre>
        <textarea class="editor-input" spellcheck="false" autocapitalize="off"
                  autocomplete="off" autocorrect="off" wrap="off"></textarea>
      </div>`;

    this.gutter = root.querySelector('.editor-gutter');
    this.gutterInner = root.querySelector('.editor-gutter-inner');
    this.activeLineEl = root.querySelector('.editor-activeline');
    this.pre = root.querySelector('.editor-highlight');
    this.code = this.pre.querySelector('code');
    this.textarea = root.querySelector('.editor-input');

    this.textarea.addEventListener('input', () => {
      this.highlightSyntax();
      this.handlers.onInput(this.textarea.value);
      this.emitSelectedLine();
    });

    this.textarea.addEventListener('scroll', () => this.syncScroll());

    // textViewDidChangeSelection karşılığı
    const onSel = () => this.emitSelectedLine();
    this.textarea.addEventListener('click', onSel);
    this.textarea.addEventListener('keyup', onSel);
    this.textarea.addEventListener('select', onSel);
    this.textarea.addEventListener('focus', onSel);
    document.addEventListener('selectionchange', () => {
      if (document.activeElement === this.textarea) this.emitSelectedLine();
    });
  }

  syncScroll() {
    const { scrollTop, scrollLeft } = this.textarea;
    this.pre.scrollTop = scrollTop;
    this.pre.scrollLeft = scrollLeft;
    this.gutterInner.style.transform = `translateY(${-scrollTop}px)`;
    this.updateActiveLineBand();
  }

  /** updateNSView karşılığı: dışarıdan gelen metni uygular (scroll korunur) */
  setText(text) {
    if (this.textarea.value === text) return;
    const scrollTop = this.textarea.scrollTop;
    this.textarea.value = text;
    this.highlightSyntax();
    this.textarea.scrollTop = scrollTop;
    this.syncScroll();
  }

  get text() {
    return this.textarea.value;
  }

  focus() {
    this.textarea.focus();
  }

  /** İmleci belirtilen satıra taşır (0 tabanlı) ve detay panelini tetikler */
  goToLine(index) {
    const lines = this.textarea.value.split('\n');
    if (index < 0 || index >= lines.length) return;
    let pos = 0;
    for (let i = 0; i < index; i++) pos += lines[i].length + 1;
    this.textarea.focus();
    this.textarea.setSelectionRange(pos, pos);
    this.emitSelectedLine();
  }

  /** Belge dilini değiştirir (dönüştürülmüş sekmelerde JSON/XML vurgusu için) */
  setLanguage(language) {
    const next = language || 'edi';
    if (this._language === next) return;
    this._language = next;
    this.highlightSyntax();
  }

  /** Dile göre vurgulama: EDI'de segment etiketi, JSON/XML'de token'lar */
  highlightSyntax() {
    const raw = this.textarea.value;
    const escaped = raw
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

    let html;
    if (this._language === 'json') html = highlightJSON(escaped);
    else if (this._language === 'xml') html = highlightXML(escaped);
    // Satır başındaki 3 büyük harf
    else html = escaped.replace(/^([A-Z]{3})/gm, '<span class="seg-tag">$1</span>');

    // Son satır boşsa yükseklik korunsun
    this.code.innerHTML = html + '\n';
    this.renderGutter();
  }

  renderGutter() {
    const count = this.textarea.value.split('\n').length;
    if (this._gutterCount === count) return;
    this._gutterCount = count;

    let html = '';
    for (let i = 1; i <= count; i++) html += `<div class="gl" data-line="${i}">${i}</div>`;
    this.gutterInner.innerHTML = html;
    this.markActiveGutterLine();
  }

  markActiveGutterLine() {
    const prev = this.gutterInner.querySelector('.gl.active');
    if (prev) prev.classList.remove('active');
    const el = this.gutterInner.children[this._activeLine];
    if (el) el.classList.add('active');
  }

  updateActiveLineBand() {
    if (this._activeLine < 0) {
      this.activeLineEl.style.display = 'none';
      return;
    }
    this.activeLineEl.style.display = 'block';
    this.activeLineEl.style.transform =
      `translateY(${this._activeLine * LINE_HEIGHT - this.textarea.scrollTop}px)`;
  }

  /** İmlecin bulunduğu satırın trim'lenmiş halini yayınlar */
  emitSelectedLine() {
    const value = this.textarea.value;
    const pos = this.textarea.selectionStart ?? 0;
    const start = value.lastIndexOf('\n', pos - 1) + 1;
    let end = value.indexOf('\n', pos);
    if (end === -1) end = value.length;

    const lineIndex = value.slice(0, start).split('\n').length - 1;
    if (lineIndex !== this._activeLine) {
      this._activeLine = lineIndex;
      this.markActiveGutterLine();
      this.updateActiveLineBand();
    }

    this.handlers.onSelectLine(value.slice(start, end).trim());
  }
}

// =========================================================================
// MARK: - JSON / XML VURGULAMA
// Tek geçişli regex kullanılır: replace, kendi ürettiği <span>'leri yeniden
// taramaz. Çok geçişli bir yaklaşım eklenen `class="..."` tırnaklarını metin
// sanıp iç içe geçmiş bozuk HTML üretirdi.
// =========================================================================

const JSON_TOKEN =
  /("(?:[^"\\]|\\.)*")(\s*:)?|\b(?:true|false|null)\b|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?/g;

function highlightJSON(escaped) {
  return escaped.replace(JSON_TOKEN, (m, str, colon) => {
    if (str) {
      return colon
        ? `<span class="tok-key">${str}</span>${colon}`
        : `<span class="tok-str">${str}</span>`;
    }
    if (m === 'true' || m === 'false' || m === 'null') return `<span class="tok-lit">${m}</span>`;
    return `<span class="tok-num">${m}</span>`;
  });
}

// Metin zaten kaçışlandığı için etiketler &lt; ile başlar; veri içindeki
// gerçek "&lt;" ise &amp;lt; olur ve bu kalıba takılmaz.
const XML_TOKEN = /(&lt;[?!/]*)([A-Za-z_][\w:.-]*)|([A-Za-z_][\w:.-]*)=("[^"]*")/g;

function highlightXML(escaped) {
  return escaped.replace(XML_TOKEN, (m, open, name, attr, value) => {
    if (open !== undefined) return `${open}<span class="tok-tag">${name}</span>`;
    return `<span class="tok-key">${attr}</span>=<span class="tok-str">${value}</span>`;
  });
}
