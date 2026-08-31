// DocumentManager.swift -> web karşılığı
// NSOpenPanel/NSSavePanel yerine File System Access API (destekleyen tarayıcılarda),
// desteklenmiyorsa <input type=file> + indirme (download) kullanılır.
import { L } from './i18n.js';
import { EDIParser } from './parser.js';
import { PDFExportManager } from './pdfExport.js';
import { CSVExportManager, csvBlob } from './csvExport.js';
import { detectFormat, isConversionDocument } from './convert.js';

let uid = 0;
const nextID = () => `doc-${++uid}`;

export const supportsFS = typeof window.showOpenFilePicker === 'function';

// MARK: - EDIDocumentModel karşılığı
export function createDocument({
  content = '',
  fileHandle = null,
  fileName = null,
  isStartPage = false,
  language = 'edi',
  conversion = null,
}) {
  return {
    id: nextID(),
    content,
    originalContent: content, // Başlangıçta içerik ve orijinal aynıdır
    selectedLineContent: '',
    fileHandle,
    fileName: fileName ?? L('default_new_filename'),
    isStartPage,

    /**
     * 'edi' | 'json' | 'xml' — belgenin biçimi.
     * PDF/Excel dışa aktarma, banner, detay paneli ve söz dizimi vurgusu buna
     * bakar: EDI olmayan bir belgeyi EDIParser'a vermek anlamsız çıktı üretir.
     */
    language,
    /** Dönüşümle üretildiyse round-trip doğrulamasının sonucu */
    conversion,

    // Hesaplanmış özellik: İçerik orijinal halinden farklı mı?
    get hasUnsavedChanges() {
      if (this.isStartPage) return false;
      return this.content !== this.originalContent;
    },

    markAsSaved() {
      this.originalContent = this.content;
    },
  };
}

// MARK: - Document Manager
export class DocumentManager extends EventTarget {
  constructor() {
    super();
    this.tabs = [];
    this.activeTabID = null;
    /** Kaydetme akışında beklenen uyarı: 'invalidFormat' | 'txtConversion' | null */
    this.activeAlert = null;
    /** UI'ın diyalog göstermesi için kanca (app.js atar) */
    this.presentAlert = null;
    /** Açılışta EDI'ye dönüştürme teklif edilecek belge (app.js tüketir) */
    this.pendingConvertOffer = null;
  }

  changed() {
    this.dispatchEvent(new Event('change'));
  }

  // Aktif sekmenin dizindeki sırasını bulur
  get activeDocumentIndex() {
    const i = this.tabs.findIndex((t) => t.id === this.activeTabID);
    return i >= 0 ? i : null;
  }

  get activeDocument() {
    const i = this.activeDocumentIndex;
    return i === null ? null : this.tabs[i];
  }

  /** Herhangi bir sekmede kaydedilmemiş değişiklik var mı? */
  get hasUnsavedChanges() {
    return this.tabs.some((t) => !t.isStartPage && t.content !== t.originalContent);
  }

  // MARK: - PDF DIŞA AKTAR
  exportCurrentDocumentToPDF() {
    const doc = this.activeDocument;
    if (!doc || doc.language !== 'edi') return;
    const segments = EDIParser.parse(doc.content);
    PDFExportManager.exportToPDF(segments);
  }

  // MARK: - EXCEL (CSV) DIŞA AKTAR
  async prepareCSVExport() {
    const doc = this.activeDocument;
    if (!doc || doc.language !== 'edi') return;
    const segments = EDIParser.parse(doc.content);
    const csvString = CSVExportManager.generateCSV(segments);
    const blob = csvBlob(csvString);
    const defaultFilename = 'EDI_Export.csv';

    if (supportsFS && typeof window.showSaveFilePicker === 'function') {
      try {
        const handle = await window.showSaveFilePicker({
          suggestedName: defaultFilename,
          types: [{ description: 'CSV', accept: { 'text/csv': ['.csv'] } }],
        });
        const w = await handle.createWritable();
        await w.write(blob);
        await w.close();
        console.log('Excel kaydedildi:', handle.name);
        return;
      } catch (e) {
        if (e && e.name === 'AbortError') return;
        console.warn('Hata:', e);
      }
    }
    downloadBlob(blob, defaultFilename);
  }

  // MARK: - SEKME YÖNETİMİ

  addNewTab() {
    const newDoc = createDocument({ content: '', isStartPage: true });
    this.tabs.push(newDoc);
    this.activeTabID = newDoc.id;
    this.changed();
  }

  // Başlangıç sayfasındayken "Yeni Dosya Oluştur" denirse
  createNewFileInCurrentTab() {
    const doc = this.activeDocument;
    if (!doc) return;
    doc.isStartPage = false;
    doc.content = '';
    doc.originalContent = '';
    doc.fileHandle = null;
    this.changed();
  }

  // Menüden veya butondan "Yeni Dosya" denirse
  createNewEditorTab() {
    const defaultName = L('default_new_filename');
    const doc = this.activeDocument;

    if (doc && doc.isStartPage) {
      doc.isStartPage = false;
      doc.content = '';
      doc.originalContent = '';
      doc.fileName = defaultName;
      doc.fileHandle = null;
    } else {
      const newDoc = createDocument({ content: '', isStartPage: false, fileName: defaultName });
      this.tabs.push(newDoc);
      this.activeTabID = newDoc.id;
    }
    this.changed();
  }

  closeTab(id) {
    const index = this.tabs.findIndex((t) => t.id === id);
    if (index < 0) return;

    const isClosingActive = this.activeTabID === id;
    this.tabs.splice(index, 1);

    if (this.tabs.length === 0) {
      // Hiç sekme kalmadıysa -> Hoşgeldin ekranı
      this.activeTabID = null;
    } else if (isClosingActive) {
      const newIndex = Math.min(index, this.tabs.length - 1);
      this.activeTabID = this.tabs[newIndex] ? this.tabs[newIndex].id : this.tabs[0].id;
    }
    this.changed();
  }

  // MARK: - DOSYA AÇMA (Open)
  async openDocument() {
    if (supportsFS) {
      let handles;
      try {
        handles = await window.showOpenFilePicker({
          multiple: true,
          types: [{
            description: 'EDI / JSON / XML',
            accept: {
              'text/plain': ['.edi', '.txt', '.dat', '.x12', '.edifact'],
              'application/json': ['.json'],
              'application/xml': ['.xml'],
            },
          }],
          excludeAcceptAllOption: false,
        });
      } catch (e) {
        if (e && e.name === 'AbortError') return;
        console.warn('Okuma hatası:', e);
        return;
      }
      for (const handle of handles) {
        try {
          const file = await handle.getFile();
          const data = await file.text();
          this._acceptOpenedFile(data, file.name, handle);
        } catch (e) {
          console.error('Okuma hatası:', e);
        }
      }
      this.changed();
      return;
    }

    // Fallback: klasik dosya seçici
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.accept = '.edi,.txt,.dat,.x12,.json,.xml,text/plain';
    input.addEventListener('change', async () => {
      for (const file of Array.from(input.files || [])) {
        try {
          const data = await file.text();
          this._acceptOpenedFile(data, file.name, null);
        } catch (e) {
          console.error('Okuma hatası:', e);
        }
      }
      this.changed();
    });
    input.click();
  }

  /** Açılan içeriği aktif başlangıç sekmesine yerleştirir veya yeni sekme açar */
  _acceptOpenedFile(data, name, handle) {
    const language = detectFormat(data, name);
    const doc = this.activeDocument;
    if (doc && doc.isStartPage) {
      doc.content = data;
      doc.originalContent = data;
      doc.fileHandle = handle;
      doc.fileName = name;
      doc.isStartPage = false;
      doc.language = language;
      doc.conversion = null;
    } else {
      const newDoc = createDocument({
        content: data, fileHandle: handle, fileName: name, isStartPage: false, language,
      });
      this.tabs.push(newDoc);
      this.activeTabID = newDoc.id;
    }
    // Şemamıza ait bir JSON/XML açıldıysa arayüz EDI'ye çevirmeyi teklif eder
    if (language !== 'edi' && isConversionDocument(data)) {
      this.pendingConvertOffer = this.activeDocument;
    }
  }

  /** Sürükle-bırak ile açma */
  async openFiles(files) {
    for (const file of files) {
      try {
        const data = await file.text();
        this._acceptOpenedFile(data, file.name, null);
      } catch (e) {
        console.error('Okuma hatası:', e);
      }
    }
    this.changed();
  }

  // MARK: - KAYDETME (Save)

  /** @returns {Promise<boolean>} kaydedildi mi */
  async initiateSave() {
    const doc = this.activeDocument;
    if (!doc || doc.isStartPage) return false;

    if (!doc.fileHandle) {
      return await this.saveAsDocument();
    }

    // Biçim uyarısı yalnızca EDI belgeleri için anlamlı; dönüştürülmüş bir
    // JSON/XML sekmesinde her kaydetmede uyarmak yanlış olurdu.
    if (doc.language === 'edi' && !EDIParser.isProbablyEDI(doc.content)) {
      this.activeAlert = 'invalidFormat';
      const proceed = this.presentAlert ? await this.presentAlert('invalidFormat') : true;
      this.activeAlert = null;
      if (!proceed) return false;
    }
    return await this.checkExtensionAndSave();
  }

  /** @returns {Promise<boolean>} */
  async checkExtensionAndSave() {
    const doc = this.activeDocument;
    if (!doc || !doc.fileHandle) return false;

    if (extensionOf(doc.fileName).toLowerCase() === 'txt') {
      this.activeAlert = 'txtConversion';
      const convert = this.presentAlert ? await this.presentAlert('txtConversion') : false;
      this.activeAlert = null;
      if (!convert) return false;
      return await this.performFinalSave(true);
    }
    return await this.performFinalSave(false);
  }

  /** @returns {Promise<boolean>} */
  async performFinalSave(changeExtension) {
    const doc = this.activeDocument;
    if (!doc || !doc.fileHandle) return false;

    // Web'de var olan bir dosyanın uzantısını yerinde değiştiremeyiz;
    // uzantı değişimi istendiğinde "Farklı Kaydet" akışına düşülür.
    if (changeExtension) {
      const newName = stripExtension(doc.fileName) + '.edi';
      return await this.saveAsDocument(newName);
    }

    try {
      const w = await doc.fileHandle.createWritable();
      await w.write(new Blob([doc.content], { type: 'text/plain;charset=utf-8' }));
      await w.close();
      doc.markAsSaved();
      this.changed();
      return true;
    } catch (e) {
      console.warn('Kayıt hatası, Farklı Kaydet açılıyor:', e);
      return await this.saveAsDocument(doc.fileName);
    }
  }

  // MARK: - FARKLI KAYDET (Save As)
  /** @returns {Promise<boolean>} */
  async saveAsDocument(suggestedName) {
    const doc = this.activeDocument;
    if (!doc) return false;

    const nameToUse = suggestedName ?? doc.fileName;
    const kind = SAVE_KINDS[doc.language] ?? SAVE_KINDS.edi;
    const blob = new Blob([doc.content], { type: `${kind.mime};charset=utf-8` });

    if (supportsFS && typeof window.showSaveFilePicker === 'function') {
      try {
        const handle = await window.showSaveFilePicker({
          suggestedName: nameToUse,
          types: [{ description: kind.description, accept: { [kind.mime]: kind.extensions } }],
        });
        const w = await handle.createWritable();
        await w.write(blob);
        await w.close();

        doc.fileHandle = handle;
        doc.fileName = handle.name;
        doc.markAsSaved();
        doc.isStartPage = false;
        this.changed();
        return true;
      } catch (e) {
        if (e && e.name === 'AbortError') return false;
        console.error('Kayıt hatası:', e);
        return false;
      }
    }

    // Fallback: indirme
    let finalName = nameToUse;
    if (extensionOf(finalName) === '') finalName += kind.extensions[0];
    downloadBlob(blob, finalName);
    doc.fileName = finalName;
    doc.markAsSaved();
    doc.isStartPage = false;
    this.changed();
    return true;
  }
}

// =========================================================================
// MARK: - YARDIMCILAR
// =========================================================================

/** Belge diline göre kaydetme diyaloğunun dosya türü */
const SAVE_KINDS = {
  edi: { description: 'EDI', mime: 'text/plain', extensions: ['.edi', '.txt'] },
  json: { description: 'JSON', mime: 'application/json', extensions: ['.json'] },
  xml: { description: 'XML', mime: 'application/xml', extensions: ['.xml'] },
};

export function extensionOf(name) {
  const i = String(name).lastIndexOf('.');
  return i > 0 ? name.slice(i + 1) : '';
}

export function stripExtension(name) {
  const i = String(name).lastIndexOf('.');
  return i > 0 ? name.slice(0, i) : name;
}

export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
