"""Dated gift occasions per country: which special day comes next?

Only occasions with a calendar date are listed; birthdays, weddings and the like
have none. Mother's and Father's Day move by country (Germany's Father's Day is
Ascension Day, France's Mother's Day is the last Sunday of May).
"""
import datetime as dt

from .config import COUNTRIES


def _nth_weekday(year, month, weekday, n):
    """n-th (1-based) weekday (0=Mon .. 6=Sun) of a month; n=-1 for the last one."""
    if n > 0:
        first = dt.date(year, month, 1)
        delta = (weekday - first.weekday()) % 7
        return first + dt.timedelta(days=delta + 7 * (n - 1))
    last = dt.date(year + (month == 12), month % 12 + 1, 1) - dt.timedelta(days=1)
    return last - dt.timedelta(days=(last.weekday() - weekday) % 7)


def easter(year):
    """Gregorian Easter Sunday (Anonymous/Meeus algorithm)."""
    a, b, c = year % 19, year // 100, year % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = (h + l - 7 * m + 114) % 31 + 1
    return dt.date(year, month, day)


def mothers_day(year, cc):
    if cc == "FR":
        d = _nth_weekday(year, 5, 6, -1)          # last Sunday of May ...
        if d == easter(year) + dt.timedelta(days=49):   # ... unless that is Pentecost
            d += dt.timedelta(days=7)
        return d
    if cc in ("GB", "IE"):
        return easter(year) - dt.timedelta(days=21)   # Mothering Sunday, 4th Sunday of Lent
    if cc == "PL":
        return dt.date(year, 5, 26)
    if cc in ("ES", "RO"):
        return _nth_weekday(year, 5, 6, 1)        # first Sunday of May
    if cc == "SE":
        return _nth_weekday(year, 5, 6, -1)       # last Sunday of May
    return _nth_weekday(year, 5, 6, 2)            # second Sunday of May (US, DE, NL, IT, AT, CH, BE, FI, DK, CA, AU, BR, TR)


def fathers_day(year, cc):
    if cc == "DE":
        return easter(year) + dt.timedelta(days=39)   # Ascension Day (Thursday)
    if cc in ("IT", "ES"):
        return dt.date(year, 3, 19)               # San Giuseppe / San José
    if cc == "PL":
        return dt.date(year, 6, 23)
    if cc == "DK":
        return dt.date(year, 6, 5)                # Constitution Day
    if cc in ("AT", "BE"):
        return _nth_weekday(year, 6, 6, 2)        # second Sunday of June
    if cc == "CH":
        return _nth_weekday(year, 6, 6, 1)        # first Sunday of June
    if cc in ("SE", "FI"):
        return _nth_weekday(year, 11, 6, 2)       # second Sunday of November
    if cc == "BR":
        return _nth_weekday(year, 8, 6, 2)        # second Sunday of August
    if cc == "AU":
        return _nth_weekday(year, 9, 6, 1)        # first Sunday of September
    if cc == "RO":
        return _nth_weekday(year, 5, 6, 2)        # second Sunday of May
    return _nth_weekday(year, 6, 6, 3)            # third Sunday of June (US, GB, IE, CA, NL, FR, TR)


def christmas(year, cc):
    if cc == "NL":                                # Sinterklaas (5 Dec) is the big gift day, Kerst follows
        return [dt.date(year, 12, 5), dt.date(year, 12, 24)]
    if cc == "BE":                                # Sint-Niklaas on 6 Dec
        return [dt.date(year, 12, 6), dt.date(year, 12, 24)]
    if cc == "ES":                                # Reyes Magos (6 Jan) after Navidad
        return [dt.date(year, 1, 6), dt.date(year, 12, 25)]
    if cc in ("DE", "AT", "CH", "FR", "TR", "PL", "SE", "FI", "DK", "BR"):
        return dt.date(year, 12, 24)              # gifts on Christmas Eve
    return dt.date(year, 12, 25)


def valentines(year, cc):
    if cc == "BR":
        return dt.date(year, 6, 12)               # Dia dos Namorados
    return dt.date(year, 2, 14)


DATED = {"valentines": valentines, "mothers_day": mothers_day, "fathers_day": fathers_day, "christmas": christmas}


def upcoming(cc, today=None, horizon_days=75):
    """Next dated occasion for a country: {"occasion", "date", "days"}.

    Returns the soonest occasion; `horizon_days` decides whether it is "upcoming"
    (shown on the home page) or merely next."""
    today = today or dt.date.today()
    best = None
    for occ, fn in DATED.items():
        for year in (today.year, today.year + 1):
            dates = fn(year, cc)
            for d in dates if isinstance(dates, list) else [dates]:
                if d >= today and (best is None or d < best[1]):
                    best = (occ, d)
    occ, d = best
    days = (d - today).days
    return {"occasion": occ, "date": d.isoformat(), "days": days, "soon": days <= horizon_days,
            "lang": COUNTRIES[cc]["lang"]}
