// LogoManager.swift -> web karşılığı
// Diske yazmak yerine logo data URL olarak localStorage'da tutulur.

const STORAGE_KEY = 'company_logo_png';

class LogoManager extends EventTarget {
  constructor() {
    super();
    this.companyLogo = localStorage.getItem(STORAGE_KEY) || null;
  }

  // Logoyu Seç ve Kaydet
  selectAndSaveLogo() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/png,image/jpeg,image/tiff,image/*';
    input.addEventListener('change', () => {
      const file = input.files && input.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = () => {
        this.companyLogo = String(reader.result);
        this.saveLogoToStorage(this.companyLogo);
        this.dispatchEvent(new Event('change'));
      };
      reader.readAsDataURL(file);
    });
    input.click();
  }

  saveLogoToStorage(dataURL) {
    try {
      localStorage.setItem(STORAGE_KEY, dataURL);
    } catch (e) {
      console.warn('Logo kaydedilemedi (depolama sınırı):', e);
    }
  }

  clearLogo() {
    this.companyLogo = null;
    localStorage.removeItem(STORAGE_KEY);
    this.dispatchEvent(new Event('change'));
  }

  // PDF için Base64 String (HTML içine gömmek için)
  getLogoAsBase64() {
    if (!this.companyLogo) return null;
    const comma = this.companyLogo.indexOf(',');
    return comma >= 0 ? this.companyLogo.slice(comma + 1) : this.companyLogo;
  }
}

export const logoManager = new LogoManager();
