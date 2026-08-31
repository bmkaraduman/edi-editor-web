#!/usr/bin/env python3
"""locales/*.json dosyalarının anahtar paritesini denetler.

js/i18n.js önce İngilizceyi yükleyip seçili dili üzerine yazar (merge). Bu,
eksik bir anahtarın hataya değil sessizce İngilizce metne yol açması demektir —
Türkçe arayüzde İngilizce bir düğme, gözden kaçması en kolay hata türü.

Kullanım:
    python3 tools/check_locales.py

Çıkış kodu 0 = tüm diller aynı anahtar kümesine sahip.
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCALES = os.path.join(ROOT, 'locales')
REFERENCE = 'en'


def load(code):
    with io.open(os.path.join(LOCALES, f'{code}.json'), encoding='utf-8') as f:
        return json.load(f)


def main():
    codes = sorted(f[:-5] for f in os.listdir(LOCALES) if f.endswith('.json'))
    if REFERENCE not in codes:
        print(f'HATA: {REFERENCE}.json bulunamadı', file=sys.stderr)
        return 1

    reference = load(REFERENCE)
    expected = set(reference)
    problems = 0

    for code in codes:
        data = load(code)
        keys = set(data)
        missing = expected - keys
        extra = keys - expected
        # Değeri İngilizceyle birebir aynı olanlar: çoğu zaman çevrilmemiş
        untranslated = {
            k for k in keys & expected
            if code != REFERENCE and data[k] == reference[k] and not k.startswith('//')
        }

        status = 'OK ' if not missing and not extra else 'HATA'
        print(f'{status} {code:8s} {len(keys):4d} anahtar', end='')
        if untranslated:
            print(f'  ({len(untranslated)} tanesi İngilizceyle aynı)', end='')
        print()

        if missing:
            problems += 1
            print(f'     eksik : {sorted(missing)}')
        if extra:
            problems += 1
            print(f'     fazla : {sorted(extra)}')

    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
