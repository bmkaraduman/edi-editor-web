// SegmentDetailView.swift -> web karşılığı
// analyzeElement: segment/element bazlı "akıllı" etiket + değer üretimi (1:1 port)
import { loc, L, Lf } from './i18n.js';
import { EDIParser, segmentDescription } from './parser.js';
import { REFERENCE_SEGMENTS } from './referenceIndex.js';

// --- TARİH FORMATLAYICI ---
export function formatEDIDate(value, formatCode) {
  // Format 102: YYYYMMDD -> 01.06.2025
  if (formatCode === '102' && value.length === 8) {
    return `${value.slice(6, 8)}.${value.slice(4, 6)}.${value.slice(0, 4)}`;
  }
  // Format 203: YYYYMMDDHHMM -> 01.06.2025 14:30
  if (formatCode === '203' && value.length === 12) {
    return `${value.slice(6, 8)}.${value.slice(4, 6)}.${value.slice(0, 4)} ${value.slice(8, 10)}:${value.slice(10, 12)}`;
  }
  // UNB Formatı: YYMMDD:HHMM
  if (formatCode === 'UNB' && value.includes(':')) {
    const parts = value.split(':').filter((p) => p.length > 0);
    if (parts.length === 2) {
      const dPart = parts[0];
      const tPart = parts[1];
      if (dPart.length === 6 && tPart.length === 4) {
        const y = '20' + dPart.slice(0, 2);
        return `${dPart.slice(4, 6)}.${dPart.slice(2, 4)}.${y} ${tPart.slice(0, 2)}:${tPart.slice(2, 4)}`;
      }
    }
  }
  // Fallback
  if (value.length === 8 && (value.startsWith('20') || value.startsWith('19'))) {
    return `${value.slice(6, 8)}.${value.slice(4, 6)}.${value.slice(0, 4)}`;
  }
  return value;
}

export function getSegmentDescription(tag) {
  // Sözlükte anahtarlar hem `seg_UNB` hem `seg_unz` biçiminde; tek yazımla
  // arayınca bazı segmentlerde ham anahtar görünüyordu (bkz. parser.js).
  return segmentDescription(tag) || tag;
}

/** elem_%@_%02d biçimli anahtar */
function elemKeyFor(tag, index) {
  return `elem_${tag}_${String(index).padStart(2, '0')}`;
}

/**
 * --- ANA ANALİZ MOTORU ---
 * @returns {{label: string, value: string}}
 */
export function analyzeElement(tag, rawElement, index, currentCurrency) {
  if (index === 0) return { label: '', value: rawElement };

  const parts = rawElement.split(':');
  const part1 = parts[0] ?? '';
  const part2 = parts.length > 1 ? parts[1] : '';
  const part3 = parts.length > 2 ? parts[2] : '';

  let friendlyLabel = '';
  let friendlyValue = rawElement;

  // Çeviri varsa döner, yoksa null
  const tr = (key) => {
    const v = L(key);
    return v !== key ? v : null;
  };

  // ---------------------------------------------------------
  // 1. UNB (ZARF BAŞLIĞI / INTERCHANGE HEADER)
  // ---------------------------------------------------------
  if (tag === 'UNB') {
    if (index === 1) {
      const v = tr(`code_UNB_${part1}`);
      friendlyLabel = L('lbl_syntax');
      const charsetName = v ?? part1;
      friendlyValue = part2 !== '' ? `${charsetName} (v${part2})` : charsetName;
    } else if (index === 2 || index === 3) {
      friendlyLabel = index === 2 ? L('lbl_sender_id') : L('lbl_recipient_id');
      if (part2 === '14') friendlyValue = `${part1} (GLN)`;
      else if (part2 === 'ZZZ') friendlyValue = `${part1} (${L('lbl_mutually_defined')})`;
      else if (part2 !== '') friendlyValue = `${part1} (${L('lbl_type')}: ${part2})`;
      else friendlyValue = part1;
    } else if (index === 4) {
      friendlyLabel = L('lbl_date');
      friendlyValue = formatEDIDate(rawElement, 'UNB');
    } else if (index === 5) {
      friendlyLabel = L('lbl_env_ref');
      friendlyValue = rawElement;
    } else if (index === 7) {
      friendlyLabel = L('lbl_app_ref');
      friendlyValue = rawElement;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // PIA (EK ÜRÜN TANIMLAMA)
  // ---------------------------------------------------------
  if (tag === 'PIA') {
    if (index === 1) {
      friendlyLabel = L('lbl_id_type');
      friendlyValue = rawElement === '1' ? L('lbl_additional_id') : rawElement;
    } else if (index >= 2) {
      if (part2 !== '') {
        const v = tr(`code_PIA_${part2}`);
        if (v) {
          friendlyLabel = v;
          friendlyValue = part1;
        } else {
          friendlyLabel = Lf('lbl_prod_code_with_type', part2);
          friendlyValue = part1;
        }
      } else {
        friendlyLabel = L('lbl_additional_prod_code');
        friendlyValue = part1;
      }
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // HAN (ELLEÇLEME / TAŞIMA TALİMATI)
  // ---------------------------------------------------------
  if (tag === 'HAN') {
    if (index === 1) {
      const code = part1;
      const k = `code_HAN_${code}`;
      const v = L(k);
      friendlyLabel = L('lbl_handling_instr');
      if (code === 'FRO') friendlyValue = `❄️ ${v}`;
      else if (code === 'FRG') friendlyValue = `🍷 ${v}`;
      else if (code === 'NST') friendlyValue = `⛔️ ${v}`;
      else if (code === 'KEP') friendlyValue = `⬆️ ${v}`;
      else if (code === 'DGS') friendlyValue = `☢️ ${v}`;
      else friendlyValue = v !== k ? v : code;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // --- TSR (TAŞIMA HİZMET KOŞULLARI) ---
  if (tag === 'TSR') {
    if (index === 1) {
      friendlyLabel = L('lbl_condition_type');
      friendlyValue = tr(`code_TSR_${rawElement}`) ?? rawElement;
    } else if (index === 2) {
      friendlyLabel = L('lbl_service_type');
      friendlyValue = tr(`code_TSR_${part1}`) ?? part1;
    } else if (index === 3) {
      const code = part1 === '' ? rawElement : part1;
      friendlyLabel = L('lbl_service_scope');
      friendlyValue = tr(`code_TSR_${code}`) ?? code;
    } else if (index === 4) {
      friendlyLabel = L('lbl_priority');
      friendlyValue = tr(`code_TSR_${part1}`) ?? part1;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // --- EQD (EKİPMAN DETAYI) ---
  if (tag === 'EQD') {
    if (index === 1) {
      friendlyLabel = L('lbl_equipment_type');
      friendlyValue = tr(`code_EQD_${rawElement}`) ?? rawElement;
    } else if (index === 2) {
      friendlyLabel = L('lbl_container_no');
      friendlyValue = rawElement === '' ? '-' : rawElement;
    } else if (index === 3) {
      friendlyLabel = L('lbl_dimension_type');
      const isoCode = part1; // 42G1
      if (isoCode.length === 4) {
        const lengthChar = isoCode[0];
        const heightChar = isoCode[1];
        const typeChar = isoCode[2];

        let sizeStr = '';
        let typeStr = '';

        if (lengthChar === '2') sizeStr = "20'";
        else if (lengthChar === '4') sizeStr = "40'";
        else if (lengthChar === 'L') sizeStr = "45'";

        if (heightChar === '5') sizeStr += ' ' + L('lbl_high_cube');

        if (typeChar === 'G') typeStr = L('code_EQD_TYPE_G');
        else if (typeChar === 'R') typeStr = L('code_EQD_TYPE_R');
        else if (typeChar === 'U') typeStr = L('code_EQD_TYPE_U');
        else if (typeChar === 'T') typeStr = L('code_EQD_TYPE_T');

        friendlyValue = sizeStr !== '' ? `${sizeStr} ${typeStr} [${isoCode}]` : isoCode;
      } else {
        friendlyValue = isoCode;
      }
    } else if (index === 5) {
      friendlyLabel = L('lbl_status');
      if (rawElement === '1') friendlyValue = L('lbl_continental');
      else if (rawElement === '2') friendlyValue = L('lbl_export_import');
      else friendlyValue = rawElement;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 6. INV (ENVANTER YÖNETİMİ / HAREKET TİPİ)
  // ---------------------------------------------------------
  if (tag === 'INV') {
    if (index === 1) {
      friendlyLabel = L('lbl_inventory_type');
      switch (part1) {
        case '1': friendlyValue = L('code_INV_1'); break;
        case '2': friendlyValue = L('code_INV_2'); break;
        case '3': friendlyValue = L('code_INV_3'); break;
        default: friendlyValue = L('lbl_code') + `: ${part1}`;
      }
    } else if (index === 2) {
      friendlyLabel = L('lbl_method');
      friendlyValue = rawElement;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 7. ALI (MENŞEİ / ÜLKE)
  // ---------------------------------------------------------
  if (tag === 'ALI') {
    if (index === 1) {
      friendlyLabel = L('lbl_origin_country');
      friendlyValue = tr(`code_COUNTRY_${rawElement}`) ?? rawElement;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 8. STS (DURUM / STATUS)
  // ---------------------------------------------------------
  if (tag === 'STS') {
    if (index === 1) {
      friendlyLabel = L('lbl_status_type');
      friendlyValue = tr(`code_STS_TYPE_${rawElement}`) ?? rawElement;
    } else if (index === 2) {
      friendlyLabel = L('lbl_status_event');
      const eventCode = part2;
      if (eventCode !== '') {
        friendlyValue = tr(`code_STS_EVENT_${eventCode}`) ?? Lf('lbl_code_with_cat', eventCode, part1);
      } else {
        friendlyValue = rawElement;
      }
    } else if (index === 4) {
      friendlyLabel = L('lbl_reason_code');
      friendlyValue = rawElement;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 9. TMP (SICAKLIK BİLGİSİ)
  // ---------------------------------------------------------
  if (tag === 'TMP') {
    if (index === 1) {
      friendlyLabel = L('lbl_temp_type');
      friendlyValue = tr(`code_TMP_${rawElement}`) ?? Lf('lbl_type_code', rawElement);
    } else if (index === 2) {
      friendlyLabel = L('lbl_temp_val');
      const degree = part1;
      const rawUnit = part2;
      let displayUnit = rawUnit;
      if (rawUnit === 'CEL') displayUnit = '°C';
      else if (rawUnit === 'FAH') displayUnit = '°F';
      else if (rawUnit === 'KEL') displayUnit = 'K';
      friendlyValue = displayUnit !== '' ? `${degree} ${displayUnit}` : degree;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 1. DGS (TEHLİKELİ MADDE DETAYLARI)
  // ---------------------------------------------------------
  if (tag === 'DGS') {
    if (index === 1) {
      friendlyLabel = L('lbl_danger_reg');
      friendlyValue = tr(`code_DGS_REG_${rawElement}`) ?? rawElement;
    } else if (index === 2) {
      friendlyLabel = L('lbl_danger_class');
      friendlyValue = tr(`code_DGS_CLASS_${rawElement}`) ?? Lf('lbl_class_code', rawElement);
    } else if (index === 3) {
      friendlyLabel = L('lbl_un_code');
      const v = tr(`code_UN_${rawElement}`);
      friendlyValue = v ? `${rawElement} (${v})` : rawElement;
    } else if (index === 4) {
      friendlyLabel = L('lbl_flash_point');
      const temp = part1;
      const unit = part2;
      if (unit === 'CEL') friendlyValue = `${temp}°C`;
      else if (unit === 'FAH') friendlyValue = `${temp}°F`;
      else friendlyValue = rawElement;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 2. MOA (PARASAL TUTARLAR)
  // ---------------------------------------------------------
  if (tag === 'MOA') {
    if (index === 1) {
      friendlyLabel = tr(`code_MOA_${part1}`) ?? Lf('lbl_amount_type_code', part1);
      if (part2 !== '') {
        friendlyValue = part2;
        const currency = part3 !== '' ? part3 : currentCurrency;
        if (currency !== '') friendlyValue += ` ${currency}`;
      } else {
        friendlyValue = rawElement;
      }
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 13. ALC (MASRAF VEYA İNDİRİM)
  // ---------------------------------------------------------
  if (tag === 'ALC') {
    if (index === 1) {
      friendlyLabel = L('lbl_action_type');
      friendlyValue = tr(`code_ALC_${part1}`) ?? (part1 === 'C' ? L('lbl_charge') : L('lbl_allowance'));
    } else if (index === 2) {
      friendlyLabel = L('lbl_code_no');
      friendlyValue = tr(`code_ALC_ID_${rawElement}`) ?? rawElement;
    } else if (index === 4) {
      friendlyLabel = L('lbl_calc_status');
      friendlyValue = tr(`code_ALC_LEVEL_${rawElement}`) ?? Lf('lbl_order_step', rawElement);
    } else if (index === 5) {
      friendlyLabel = L('lbl_service_reason');
      friendlyValue = tr(`code_ALC_REASON_${part1}`) ?? Lf('lbl_code_val', part1);
    } else if (index === 6 && rawElement !== '') {
      friendlyLabel = L('pdf_col_total');
      friendlyValue = rawElement;
      if (currentCurrency !== '') friendlyValue += ` ${currentCurrency}`;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 14. IMD (EŞYA TANIMI)
  // ---------------------------------------------------------
  if (tag === 'IMD') {
    if (index === 1) {
      friendlyLabel = L('lbl_format');
      friendlyValue = tr(`code_IMD_${rawElement}`) ?? rawElement;
    } else if (index === 3) {
      friendlyLabel = L('lbl_prod_desc');
      const descParts = rawElement.split(':').filter((p) => p.length > 0);
      friendlyValue = descParts.length > 0 ? descParts[descParts.length - 1] : rawElement;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 15. PGI (ÜRÜN GRUBU / DURUM BİLGİSİ)
  // ---------------------------------------------------------
  if (tag === 'PGI') {
    if (index === 1) {
      const k = `code_PGI_${rawElement}`;
      const v = L(k);
      friendlyLabel = L('lbl_prod_status');
      if (rawElement === '1') friendlyValue = `🟢 ${v}`;
      else if (rawElement === '2') friendlyValue = `🔴 ${v}`;
      else if (rawElement === '3') friendlyValue = `🔵 ${v}`;
      else friendlyValue = v !== k ? v : rawElement;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 16. NAD (ADRES / TARAF BİLGİSİ)
  // ---------------------------------------------------------
  if (tag === 'NAD') {
    if (index === 1) {
      friendlyLabel = L('lbl_party_role');
      friendlyValue = tr(`code_NAD_${rawElement}`) ?? rawElement;
    } else if (index === 2) {
      friendlyLabel = L('lbl_firm_id');
      if (part3 === '9') {
        friendlyValue = `${part1} (${L('code_NAD_9')})`;
      } else {
        friendlyValue = part1;
      }
    } else if (index === 4) {
      friendlyLabel = L('lbl_company_name');
      friendlyValue = rawElement;
    } else if (index === 5) {
      friendlyLabel = L('lbl_address_street');
      friendlyValue = rawElement;
    } else if (index === 6) {
      friendlyLabel = L('lbl_city');
      friendlyValue = rawElement;
    } else if (index >= 7) {
      // --- AKILLI AYRIŞTIRMA ---
      const isCountryCode = rawElement.length === 2 && !/^\d+$/.test(rawElement);
      if (isCountryCode) {
        friendlyLabel = L('lbl_country');
      } else {
        friendlyLabel = L('lbl_zip_region');
      }
      friendlyValue = rawElement;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 17. PAI (ÖDEME YÖNTEMİ)
  // ---------------------------------------------------------
  if (tag === 'PAI') {
    let code = part1;
    if (code === '' && part3 !== '') code = part3;
    friendlyLabel = L('lbl_payment_method');
    friendlyValue = tr(`code_PAI_${code}`) ?? code;
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 18. UNH (MESAJ BAŞLIĞI) & UCM (MESAJ CEVABI)
  // ---------------------------------------------------------
  if (tag === 'UNH' || tag === 'UCM') {
    if (index === 1) {
      friendlyLabel = L('lbl_msg_ref_no');
      friendlyValue = rawElement;
    } else if (index === 2) {
      friendlyLabel = L('lbl_msg_type');
      const typeCode = part1;
      const readableName = tr(`code_UNH_TYPE_${typeCode}`) ?? typeCode;

      let versionInfo = '';
      if (part2 !== '') {
        versionInfo = ` (v${part2}`;
        if (part3 !== '') versionInfo += `.${part3}`;
        versionInfo += ')';
      }
      if (parts.length > 4 && parts[4] !== '') {
        versionInfo += ` [${parts[4]}]`;
      }
      friendlyValue = `${readableName}${versionInfo}`;
    } else if (tag === 'UCM' && index === 3) {
      friendlyLabel = L('lbl_action_status');
      const key = `code_UCM_${rawElement}`;
      const val = L(key);
      if (rawElement === '7') friendlyValue = `✅ ${val}`;
      else if (rawElement === '4') friendlyValue = `❌ ${val}`;
      else if (rawElement === '8') friendlyValue = `⚠️ ${val}`;
      else friendlyValue = val !== key ? val : L('lbl_code_val') + `: ${rawElement}`;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 19. UCS (HATALI SEGMENT KONUMU)
  // ---------------------------------------------------------
  if (tag === 'UCS') {
    if (index === 1) {
      friendlyLabel = L('lbl_error_line');
      friendlyValue = Lf('lbl_segment_row', rawElement);
    } else if (index === 2) {
      friendlyLabel = L('lbl_error_pos_detail');
      friendlyValue = Lf('lbl_char_point', rawElement);
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 20. UCD (HATA DETAYI / HATA KODU)
  // ---------------------------------------------------------
  if (tag === 'UCD') {
    if (index === 1) {
      friendlyLabel = L('lbl_error_reason');
      const v = tr(`code_UCD_${rawElement}`);
      friendlyValue = v ? `⚠️ ${v}` : Lf('lbl_code_val', rawElement);
    } else if (index === 2) {
      friendlyLabel = L('lbl_faulty_segment');
      const segmentTag = rawElement;
      const description = tr(`seg_${segmentTag}`) ?? tr(`code_${segmentTag}`) ?? '';
      friendlyValue = description !== '' ? `${segmentTag} - ${description}` : segmentTag;
    } else if (index === 3) {
      friendlyLabel = L('lbl_data_element_seq');
      friendlyValue = rawElement;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 21. UCI (ZARF / INTERCHANGE CEVABI)
  // ---------------------------------------------------------
  if (tag === 'UCI') {
    if (index === 1) {
      friendlyLabel = L('lbl_env_ref_no');
      friendlyValue = rawElement;
    } else if (index === 2 || index === 3) {
      friendlyLabel = index === 2 ? L('lbl_sender') : L('lbl_receiver');
      const id = part1;
      const agencyCode = part2;
      let agencyName = '';
      if (agencyCode !== '') {
        agencyName = tr(`code_AGENCY_${agencyCode}`) ?? Lf('lbl_code_val', agencyCode);
      }
      friendlyValue = agencyName !== '' ? `${id} (${agencyName})` : id;
    } else if (index === 4) {
      const k = `code_UCI_${rawElement}`;
      const v = L(k);
      friendlyLabel = L('lbl_env_status');
      if (rawElement === '7') friendlyValue = `✅ ${v}`;
      else if (rawElement === '8') friendlyValue = `❌ ${v}`;
      else friendlyValue = v !== k ? v : rawElement;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 22. FII (FİNANSAL KURUM / BANKA HESAP BİLGİSİ)
  // ---------------------------------------------------------
  if (tag === 'FII') {
    if (index === 1) {
      friendlyLabel = L('lbl_acc_holder_type');
      friendlyValue = tr(`code_FII_${rawElement}`) ?? rawElement;
    } else if (index === 2) {
      friendlyLabel = L('lbl_bank_acc_detail');
      const accountNo = part1;
      const accountName = parts.length > 1 ? parts[1] : '';
      const bankName = parts.length > 4 ? parts[4] : '';

      let result = '';
      if (bankName !== '') result += `🏦 ${bankName}\n`;
      if (accountName !== '') result += `👤 ${accountName}\n`;
      result += '🔢 ' + L('lbl_no') + `: ${accountNo}`;
      friendlyValue = result;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 23. DTM (TARİH / ZAMAN / PERİYOD)
  // ---------------------------------------------------------
  if (tag === 'DTM') {
    // 1. Etiketi Belirle
    friendlyLabel = tr(`code_DTM_${part1}`) ?? L('lbl_date_time');

    // 2. Değeri Formatla
    if (part2 !== '') {
      const formatCode = part3 === '' ? '102' : part3;

      // --- Senaryo A: Tarih Aralığı (718) ---
      if (formatCode === '718' && part2.length === 16) {
        const startDate = formatEDIDate(part2.slice(0, 8), '102');
        const endDate = formatEDIDate(part2.slice(8), '102');
        friendlyValue = `${startDate} - ${endDate}`;
      }
      // --- Senaryo B: Hafta Formatı (616) ---
      else if (formatCode === '616' && part2.length === 6) {
        friendlyValue = Lf('lbl_year_week', part2.slice(0, 4), part2.slice(4));
      }
      // --- Senaryo C: Ay Formatı (610) ---
      else if (formatCode === '610' && part2.length === 6) {
        const year = part2.slice(0, 4);
        const month = part2.slice(4);
        const mInt = parseInt(month, 10);
        if (!isNaN(mInt) && mInt > 0 && mInt <= 12) {
          friendlyValue = `${year} ${L(`month_${mInt}`)}`;
        } else {
          friendlyValue = `${year}-${month}`;
        }
      }
      // --- Senaryo D: Standart Tek Tarih/Saat ---
      else {
        friendlyValue = formatEDIDate(part2, formatCode);
      }
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 24. GIS (İŞLEME GÖSTERGESİ / YÖNTEMİ)
  // ---------------------------------------------------------
  if (tag === 'GIS') {
    if (index === 1) {
      const code = part1;
      const k = `code_GIS_${code}`;
      const v = L(k);
      friendlyLabel = L('lbl_notification_type');
      if (code === '37') friendlyValue = `🔄 ${v}`;
      else if (code === '1') friendlyValue = `❌ ${v}`;
      else if (code === '4') friendlyValue = `✏️ ${v}`;
      else friendlyValue = v !== k ? v : Lf('lbl_code_val', code);
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 25. RFF (REFERANSLAR)
  // ---------------------------------------------------------
  if (tag === 'RFF') {
    if (index === 1) {
      friendlyLabel = tr(`code_RFF_${part1}`) ?? Lf('lbl_ref_with_code', part1);
      friendlyValue = part2 !== '' ? part2 : '-';
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 26. GIN (KİMLİKLER / BARKODLAR)
  // ---------------------------------------------------------
  if (tag === 'GIN') {
    if (index === 1) {
      friendlyLabel = L('lbl_id_type');
      friendlyValue = tr(`code_GIN_${part1}`) ?? part1;
    } else if (index >= 2) {
      friendlyLabel = L('lbl_id_val');
      friendlyValue = rawElement;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 27. UNT (MESAJ SONU)
  // ---------------------------------------------------------
  if (tag === 'UNT') {
    if (index === 1) {
      friendlyLabel = L('lbl_total_seg_count');
      friendlyValue = rawElement;
    } else if (index === 2) {
      friendlyLabel = L('lbl_msg_ref_no');
      friendlyValue = rawElement;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 23. GIR (İLGİLİ KİMLİK NUMARALARI)
  // ---------------------------------------------------------
  if (tag === 'GIR') {
    if (index === 1) {
      friendlyLabel = L('elem_GIR_01');
      friendlyValue = rawElement;
    } else if (part2 !== '') {
      const v = tr(`code_GIR_${part2}`);
      friendlyLabel = v ?? Lf('lbl_id_with_type', part2);
      friendlyValue = part1;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 24. SEQ (SIRALAMA BİLGİSİ)
  // ---------------------------------------------------------
  if (tag === 'SEQ') {
    if (index === 1) {
      const k = `code_SEQ_${rawElement}`;
      const v = L(k);
      friendlyLabel = L('lbl_sort_type');
      if (rawElement === '3') friendlyValue = `🔢 ${v}`;
      else friendlyValue = v !== k ? v : rawElement;
    } else if (index === 2) {
      friendlyLabel = L('lbl_sort_info');
      friendlyValue = rawElement;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 25. PAC (PAKETLEME DETAYLARI)
  // ---------------------------------------------------------
  if (tag === 'PAC') {
    if (index === 1) {
      friendlyLabel = L('lbl_pack_qty');
      friendlyValue = rawElement;
    } else if (index === 3 || (index === 2 && rawElement !== '')) {
      friendlyLabel = L('lbl_pack_type');
      const code = part1;
      if (code !== '') {
        const pacVal = tr(`code_PAC_${code}`);
        if (pacVal) {
          friendlyValue = pacVal;
        } else {
          friendlyValue = tr(`unit_${code}`) ?? Lf('lbl_code_val', code);
        }
      } else {
        friendlyValue = rawElement;
      }
    } else if (index === 4) {
      friendlyLabel = L('lbl_pack_level');
      friendlyValue = tr(`code_PAC_LEVEL_${part1}`) ?? part1;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 26. CNT (KONTROL TOPLAMI)
  // ---------------------------------------------------------
  if (tag === 'CNT') {
    if (index === 1) {
      friendlyLabel = tr(`code_CNT_${part1}`) ?? Lf('lbl_control_total_code', part1);

      if (part2 !== '') {
        friendlyValue = part2;
        // --- ÖZEL DURUM: Parasal Toplam (Qualifier: 1) ---
        if (part1 === '1') {
          if (currentCurrency !== '') friendlyValue += ` ${currentCurrency}`;
        } else if (part3 !== '') {
          friendlyValue += ` ${tr(`unit_${part3}`) ?? part3}`;
        }
      } else {
        friendlyValue = rawElement;
      }
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 12. CNI, DOC, UNS (REFERANS VE KONTROL SEGMENTLERİ)
  // ---------------------------------------------------------
  if (tag === 'CNI') {
    if (index === 1) {
      friendlyLabel = L('lbl_sequence_no');
      friendlyValue = tr(`code_CNI_${part1}`) ?? part1;
    } else if (index === 2) {
      friendlyLabel = L('lbl_ref_no');
      friendlyValue = rawElement;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  if (tag === 'DOC') {
    if (index === 1) {
      friendlyLabel = L('lbl_doc_type');
      friendlyValue = tr(`code_DOC_${part1}`) ?? part1;
    } else if (index === 2) {
      friendlyLabel = L('lbl_doc_no');
      friendlyValue = rawElement;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  if (tag === 'UNS') {
    friendlyLabel = L('lbl_section_control');
    friendlyValue = tr(`code_UNS_${rawElement}`) ?? rawElement;
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 13. SCC (PLANLAMA KOŞULU)
  // ---------------------------------------------------------
  if (tag === 'SCC') {
    if (index === 1) {
      const k = `code_SCC_${rawElement}`;
      const v = L(k);
      friendlyLabel = L('lbl_plan_status');
      if (rawElement === '1') friendlyValue = `🔴 ${v}`;
      else if (rawElement === '4') friendlyValue = `🟡 ${v}`;
      else friendlyValue = v !== k ? v : rawElement;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 14. CPS (PAKETLEME HİYERARŞİSİ)
  // ---------------------------------------------------------
  if (tag === 'CPS') {
    if (index === 1) {
      friendlyLabel = L('lbl_hierarchy_id');
      friendlyValue = rawElement;
    } else if (index === 2) {
      friendlyLabel = L('lbl_parent_id');
      friendlyValue = Lf('lbl_inside_package', rawElement);
    } else if (index === 3) {
      friendlyLabel = L('lbl_level_type');
      friendlyValue = tr(`code_CPS_LEVEL_${rawElement}`) ?? rawElement;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 15. MEA (ÖLÇÜMLER)
  // ---------------------------------------------------------
  if (tag === 'MEA') {
    if (index === 1) {
      friendlyLabel = L('lbl_measure_scope');
      friendlyValue = tr(`code_MEA_SCOPE_${rawElement}`) ?? rawElement;
    } else if (index === 2) {
      friendlyLabel = L('lbl_measure_type');
      friendlyValue = tr(`code_MEA_TYPE_${rawElement}`) ?? rawElement;
    } else if (index === 3) {
      friendlyLabel = L('lbl_measure_val');
      const finalUnit = tr(`unit_${part1}`) ?? part1;
      const value = part2;
      friendlyValue = value !== '' ? `${value} ${finalUnit}` : rawElement;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 16. PCD (YÜZDELER)
  // ---------------------------------------------------------
  if (tag === 'PCD') {
    if (index === 1) {
      friendlyLabel = tr(`code_PCD_${part1}`) ?? L('lbl_rate_type');
      friendlyValue = part2 !== '' ? `%${part2}` : rawElement;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 17. TDT (NAKLİYE VE ARAÇ DETAYLARI)
  // ---------------------------------------------------------
  if (tag === 'TDT') {
    if (index === 1) {
      friendlyLabel = L('lbl_transport_stage');
      friendlyValue = tr(`code_TDT_STAGE_${rawElement}`) ?? rawElement;
    } else if (index === 2) {
      friendlyLabel = L('lbl_voyage_no');
      friendlyValue = rawElement;
    } else if (index === 3) {
      const code = part1 === '' ? rawElement : part1;
      friendlyLabel = L('lbl_transport_mode');
      friendlyValue = tr(`code_TDT_MODE_${code}`) ?? code;
    } else if (index === 4) {
      const code = part1 === '' ? rawElement : part1;
      friendlyLabel = L('lbl_vehicle_type');
      friendlyValue = tr(`code_TDT_VEHICLE_${code}`) ?? code;
    } else if (index === 5) {
      friendlyLabel = L('lbl_carrier_firm');
      friendlyValue = parts.length >= 4 && parts[3] !== '' ? parts[3] : (part1 !== '' ? part1 : rawElement);
    } else if (index === 8) {
      let cleanText = rawElement;
      const upper = cleanText.toUpperCase();
      if (upper.includes('PLAKA') || upper.includes('PLATE')) {
        friendlyLabel = L('lbl_vehicle_plate');
        cleanText = cleanText.replace(/PLAKA/gi, '').replace(/PLATE/gi, '');
      } else if (upper.includes('GEMI') || upper.includes('VESSEL')) {
        friendlyLabel = L('lbl_vessel_name');
        cleanText = cleanText.replace(/GEMI/gi, '').replace(/VESSEL/gi, '');
      } else {
        friendlyLabel = L('lbl_vehicle_id');
      }
      cleanText = cleanText.replace(/:/g, '').trim();
      const split = cleanText.split(':').filter((p) => p.length > 0);
      friendlyValue = split.length > 0 ? split[0] : cleanText;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 6. BGM (BELGE BAŞLANGICI)
  // ---------------------------------------------------------
  if (tag === 'BGM') {
    if (index === 1) {
      friendlyLabel = L('lbl_doc_type');
      friendlyValue = tr(`code_BGM_${part1}`) ?? part1;
    } else if (index === 2) {
      friendlyLabel = L('lbl_doc_no');
      friendlyValue = rawElement;
    } else if (index === 3) {
      friendlyLabel = L('lbl_msg_purpose');
      friendlyValue = tr(`code_BGM_FUNC_${rawElement}`) ?? rawElement;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 7. LOC (YER / LOKASYON)
  // ---------------------------------------------------------
  if (tag === 'LOC') {
    if (index === 1) {
      friendlyLabel = L('lbl_loc_type');
      friendlyValue = tr(`code_LOC_${rawElement}`) ?? rawElement;
    } else if (index === 2) {
      friendlyLabel = L('lbl_loc_name_code');
      friendlyValue = parts.length > 3 && parts[3] !== '' ? parts[3] : rawElement;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 8. LIN (SATIR / ÜRÜN)
  // ---------------------------------------------------------
  if (tag === 'LIN') {
    if (index === 1) {
      friendlyLabel = L('lbl_line_no');
      friendlyValue = rawElement;
    } else if (index === 2) {
      friendlyLabel = L('lbl_line_status');
      friendlyValue = tr(`code_LIN_STATUS_${rawElement}`) ?? rawElement;
    } else if (index === 3) {
      friendlyLabel = L('lbl_prod_code');
      if (part2 !== '') {
        friendlyLabel = tr(`code_LIN_${part2}`) ?? Lf('lbl_prod_code_type', part2);
      }
      friendlyValue = part1;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 9. FTX (SERBEST METİN / NOTLAR)
  // ---------------------------------------------------------
  if (tag === 'FTX') {
    if (index === 1) {
      friendlyLabel = L('lbl_subject_header');
      friendlyValue = tr(`code_FTX_${rawElement}`) ?? rawElement;
    } else if (index === 4) {
      friendlyLabel = L('lbl_description_text');
      friendlyValue = rawElement.replace(/:/g, ' ');
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 10. QVR (MİKTAR FARKI / SAPMA)
  // ---------------------------------------------------------
  if (tag === 'QVR') {
    if (index === 1) {
      friendlyLabel = L('lbl_qty_variance');
      let finalText = part1;
      if (part2 !== '') {
        const v = tr(`code_QVR_${part2}`);
        finalText += v ? ` (${v})` : ` (${L('lbl_code')}: ${part2})`;
      }
      friendlyValue = finalText;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 11. PCI (PAKET İŞARETLEME)
  // ---------------------------------------------------------
  if (tag === 'PCI') {
    if (index === 1) {
      friendlyLabel = L('lbl_label_type');
      friendlyValue = tr(`code_PCI_${part1}`) ?? part1;
    } else if (index >= 2) {
      friendlyLabel = L('lbl_label_note');
      friendlyValue = rawElement;
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 12. TAX (VERGİ VE KDV)
  // ---------------------------------------------------------
  if (tag === 'TAX') {
    if (index === 1) {
      friendlyLabel = L('lbl_tax_status');
      friendlyValue = tr(`code_TAX_FUNC_${rawElement}`) ?? rawElement;
    } else if (index === 2) {
      friendlyLabel = L('lbl_tax_type');
      friendlyValue = tr(`code_TAX_TYPE_${part1}`) ?? part1;
    } else if (index === 5) {
      const nonEmpty = parts.filter((p) => p.length > 0);
      const rate = nonEmpty.length > 0 ? nonEmpty[nonEmpty.length - 1] : '';
      if (rate !== '') {
        friendlyLabel = L('lbl_tax_rate');
        friendlyValue = `%${rate}`;
      }
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // GID (MAL TANIMLAMA)
  // ---------------------------------------------------------
  if (tag === 'GID') {
    if (index === 1) {
      friendlyLabel = L('lbl_item_seq_no');
      friendlyValue = rawElement;
    } else if (index === 2) {
      friendlyLabel = L('lbl_packing_info');
      if (part2 !== '') {
        const typeName = tr(`unit_${part2}`) ?? part2;
        friendlyValue = `${part1} ${typeName}`;
      } else {
        friendlyValue = rawElement;
      }
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 28. CUX (PARA BİRİMİ)
  // ---------------------------------------------------------
  if (tag === 'CUX') {
    if (index === 1) {
      if (part2 !== '') {
        friendlyLabel = L('lbl_currency');
        friendlyValue = part2;
      }
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 29. AJT (KESİNTİ / AYARLAMA NEDENİ)
  // ---------------------------------------------------------
  if (tag === 'AJT') {
    if (index === 1) {
      friendlyLabel = L('lbl_adjustment_direction');
      if (rawElement === '1') friendlyValue = L('lbl_deduction');
      else if (rawElement === '2') friendlyValue = L('lbl_addition');
      else friendlyValue = rawElement;
    } else if (index === 2) {
      const k = `code_AJT_${rawElement}`;
      const v = L(k);
      friendlyLabel = L('lbl_reason_description');
      if (rawElement === '71') friendlyValue = `📦💥 ${v}`;
      else if (rawElement === '72') friendlyValue = `🔍🚫 ${v}`;
      else if (rawElement === '73') friendlyValue = `💰📉 ${v}`;
      else friendlyValue = v !== k ? v : Lf('lbl_code_val', rawElement);
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // ---------------------------------------------------------
  // 30. QTY & PRI (MİKTAR VE FİYAT)
  // ---------------------------------------------------------
  if (tag === 'QTY' || tag === 'PRI') {
    if (index === 1) {
      // Etiket Belirle
      const codeVal = tr(`code_${tag}_${part1}`);
      if (codeVal) {
        friendlyLabel = codeVal;
      } else {
        friendlyLabel = tr(elemKeyFor(tag, index)) ?? Lf('lbl_type_with_code', tag, part1);
      }

      // Değer ve Birim/Para Birimi Belirle
      if (part2 !== '') {
        friendlyValue = part2;
        if (tag === 'QTY' && part3 !== '') {
          friendlyValue += ` ${tr(`unit_${part3}`) ?? part3}`;
        } else if (tag === 'PRI') {
          if (currentCurrency !== '') friendlyValue += ` ${currentCurrency}`;
        }
      }
    }
    return { label: friendlyLabel, value: friendlyValue };
  }

  // 18. DEFAULT
  const elemLocalized = tr(elemKeyFor(tag, index));
  if (elemLocalized) friendlyLabel = elemLocalized;

  return { label: friendlyLabel, value: friendlyValue };
}

// =========================================================================
// MARK: - RENDER (SwiftUI body karşılığı)
// =========================================================================

function esc(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

/**
 * Detay panelini verilen konteynere çizer.
 * @param {HTMLElement} container
 * @param {string} rawLine seçili satır
 * @param {string} currentCurrency dosyadan tespit edilen para birimi (CUX)
 */
export function renderSegmentDetail(container, rawLine, currentCurrency) {
  const segment = EDIParser.parse(rawLine)[0];

  if (!segment) {
    container.innerHTML = `
      <div class="detail-placeholder">
        <svg viewBox="0 0 24 24" class="placeholder-icon" aria-hidden="true">
          <rect x="5" y="2" width="14" height="20" rx="2" fill="none" stroke="currentColor" stroke-width="1.5"/>
          <circle cx="9" cy="7" r="1" fill="currentColor"/><rect x="11.5" y="6.25" width="5" height="1.5" rx=".75" fill="currentColor"/>
          <circle cx="9" cy="12" r="1" fill="currentColor"/><rect x="11.5" y="11.25" width="5" height="1.5" rx=".75" fill="currentColor"/>
          <circle cx="9" cy="17" r="1" fill="currentColor"/><rect x="11.5" y="16.25" width="5" height="1.5" rx=".75" fill="currentColor"/>
        </svg>
        <div class="placeholder-text">${esc(L('detail_placeholder'))}</div>
      </div>`;
    return;
  }

  const rows = segment.elements
    .map((rawElement, index) => {
      const d = analyzeElement(segment.tag, rawElement, index, currentCurrency);
      const showLabel = d.label !== '';
      const showRaw = d.value !== rawElement && d.label !== '';
      return `
        <div class="detail-row${index % 2 === 0 ? '' : ' alt'}">
          <div class="detail-idx">${String(index).padStart(2, '0')}</div>
          <div class="detail-sep"></div>
          <div class="detail-main">
            ${showLabel ? `<div class="detail-label">${esc(d.label)}</div>` : ''}
            <div class="detail-value">${esc(d.value === '' ? '-' : d.value)}</div>
          </div>
          ${showRaw ? `<div class="detail-raw">${esc(rawElement)}</div>` : ''}
        </div>`;
    })
    .join('');

  container.innerHTML = `
    <div class="detail-header">
      <div class="detail-tag">${esc(segment.tag)}</div>
      <div class="detail-headinfo">
        <div class="detail-title">
          ${esc(getSegmentDescription(segment.tag))}
          ${referenceLink(segment.tag)}
        </div>
        <div class="detail-rawline">${esc(segment.rawLine)}</div>
      </div>
    </div>
    <div class="detail-list">${rows}</div>`;
}

/**
 * Segmentin referans sayfasına bağlantı.
 * Yalnızca sayfası üretilmiş segmentler için döner; aksi hâlde boş string.
 * Yeni sekmede açılır, böylece düzenlenen dosya ve sekmeler kaybolmaz.
 */
function referenceLink(tag) {
  if (!REFERENCE_SEGMENTS.has(tag)) return '';
  const dir = loc.currentLanguageCode === 'tr' ? 'edi/segment' : 'edi/en/segment';
  return `<a class="detail-doclink" href="${dir}/${tag.toLowerCase()}.html"
     target="_blank" rel="noopener" title="${esc(L('segment_docs'))}">
     <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.7"/><path d="M12 11v6" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/><circle cx="12" cy="7.6" r="1.15" fill="currentColor"/></svg>
     <span>${esc(L('segment_docs'))}</span></a>`;
}
