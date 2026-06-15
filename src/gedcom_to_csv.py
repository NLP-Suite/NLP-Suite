"""GEDCOM to CSV Converter for Family Archive Viewer.

Converts a GEDCOM (.ged) file exported from Ancestry (or any genealogy
software) into the three CSV files needed by the Family Archive Viewer:
  - Points.csv  — people (ID, Name, Gen, Born, Died, Photo URL, Details...)
  - Links.csv   — relationships (Source, Target, Relationship)
  - Migration.csv — location events (person_id, year, county, state, lat, lng, event, details)

Usage (source):  python gedcom_to_csv.py
Usage (exe):     GedcomConverter.exe
"""

import os
import sys
import re
import time
import tkinter as tk
from tkinter import filedialog, messagebox

import pandas as pd


# ---- US state name ↔ abbreviation ----------------------------------------

_STATE_ABBR = {
    'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR',
    'california': 'CA', 'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE',
    'district of columbia': 'DC', 'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI',
    'idaho': 'ID', 'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA',
    'kansas': 'KS', 'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME',
    'maryland': 'MD', 'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN',
    'mississippi': 'MS', 'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE',
    'nevada': 'NV', 'new hampshire': 'NH', 'new jersey': 'NJ', 'new mexico': 'NM',
    'new york': 'NY', 'north carolina': 'NC', 'north dakota': 'ND', 'ohio': 'OH',
    'oklahoma': 'OK', 'oregon': 'OR', 'pennsylvania': 'PA', 'rhode island': 'RI',
    'south carolina': 'SC', 'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX',
    'utah': 'UT', 'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA',
    'west virginia': 'WV', 'wisconsin': 'WI', 'wyoming': 'WY',
}
_ABBR_SET = set(_STATE_ABBR.values())

_STATE_COORDS = {
    'AL': (32.32, -86.90), 'AK': (63.59, -154.49), 'AZ': (34.05, -111.09),
    'AR': (34.97, -92.37), 'CA': (36.78, -119.42), 'CO': (39.55, -105.78),
    'CT': (41.60, -72.76), 'DC': (38.91, -77.04), 'DE': (38.91, -75.53),
    'FL': (27.66, -81.52), 'GA': (32.16, -82.90), 'HI': (19.90, -155.58),
    'ID': (44.07, -114.74), 'IL': (40.63, -89.40), 'IN': (40.27, -86.13),
    'IA': (41.88, -93.10), 'KS': (39.01, -98.48), 'KY': (37.84, -84.27),
    'LA': (30.98, -91.96), 'ME': (45.25, -69.45), 'MD': (39.05, -76.64),
    'MA': (42.41, -71.38), 'MI': (44.31, -85.60), 'MN': (46.73, -94.69),
    'MS': (32.35, -89.40), 'MO': (37.96, -91.83), 'MT': (46.88, -110.36),
    'NE': (41.49, -99.90), 'NV': (38.80, -116.42), 'NH': (43.19, -71.57),
    'NJ': (40.06, -74.41), 'NM': (34.52, -105.87), 'NY': (43.30, -74.22),
    'NC': (35.76, -79.02), 'ND': (47.55, -101.00), 'OH': (40.42, -82.91),
    'OK': (35.47, -97.52), 'OR': (43.80, -120.55), 'PA': (41.20, -77.19),
    'RI': (41.58, -71.48), 'SC': (33.84, -81.16), 'SD': (43.97, -99.90),
    'TN': (35.52, -86.58), 'TX': (31.97, -99.90), 'UT': (39.32, -111.09),
    'VT': (44.56, -72.58), 'VA': (37.43, -78.66), 'WA': (47.75, -120.74),
    'WV': (38.60, -80.45), 'WI': (43.78, -88.79), 'WY': (43.08, -107.29),
}

_MONTH_MAP = {
    'JAN': 'January', 'FEB': 'February', 'MAR': 'March', 'APR': 'April',
    'MAY': 'May', 'JUN': 'June', 'JUL': 'July', 'AUG': 'August',
    'SEP': 'September', 'OCT': 'October', 'NOV': 'November', 'DEC': 'December',
}


# ---- GEDCOM line parsing --------------------------------------------------

def _read_gedcom(filepath):
    for enc in ('utf-8-sig', 'utf-8', 'latin-1'):
        try:
            with open(filepath, 'r', encoding=enc) as f:
                raw = f.read()
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
    else:
        raise ValueError(f'Cannot decode GEDCOM file: {filepath}')

    lines = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r'^(\d+)\s+(@\S+@)?\s*(\S+)\s*(.*)?$', line)
        if not m:
            continue
        level = int(m.group(1))
        xref = m.group(2) or ''
        tag = m.group(3).upper()
        value = (m.group(4) or '').strip()
        lines.append((level, xref, tag, value))
    return lines


def _extract_records(lines):
    individuals = {}
    families = {}
    current_xref = None
    current_tag = None
    current_lines = []

    def _flush():
        nonlocal current_xref, current_tag, current_lines
        if current_xref and current_lines:
            if current_tag == 'INDI':
                individuals[current_xref] = current_lines[:]
            elif current_tag == 'FAM':
                families[current_xref] = current_lines[:]
        current_lines = []

    for level, xref, tag, value in lines:
        if level == 0:
            _flush()
            if tag in ('INDI', 'FAM'):
                current_xref = xref
                current_tag = tag
            elif xref and value in ('INDI', 'FAM'):
                current_xref = xref
                current_tag = value
            else:
                current_xref = None
                current_tag = None
            continue
        if current_xref:
            current_lines.append((level, tag, value))
    _flush()
    return individuals, families


# ---- Field parsers --------------------------------------------------------

def _parse_name(value):
    m = re.match(r'^(.*?)\s*/([^/]*)/\s*(.*)$', value)
    if m:
        given = m.group(1).strip()
        surname = m.group(2).strip()
        suffix = m.group(3).strip()
        full = f'{given} {surname}'.strip()
        if suffix:
            full += f' {suffix}'
        return given, surname, full
    parts = value.strip().split()
    if len(parts) >= 2:
        return ' '.join(parts[:-1]), parts[-1], value.strip()
    return value.strip(), '', value.strip()


def _parse_date(value):
    if not value:
        return '', 0
    clean = re.sub(r'^(ABT|EST|CAL|BEF|AFT|BET|FROM|TO|INT)\s+', '', value, flags=re.I)
    clean = re.sub(r'\s+AND\s+.*$', '', clean, flags=re.I)
    m_full = re.match(r'^(\d{1,2})\s+([A-Z]{3})\s+(\d{4})$', clean, re.I)
    if m_full:
        day = m_full.group(1)
        month = _MONTH_MAP.get(m_full.group(2).upper(), m_full.group(2))
        year = int(m_full.group(3))
        return f'{month} {day}, {year}', year
    m_my = re.match(r'^([A-Z]{3})\s+(\d{4})$', clean, re.I)
    if m_my:
        month = _MONTH_MAP.get(m_my.group(1).upper(), m_my.group(1))
        year = int(m_my.group(2))
        return f'{month} {year}', year
    m_y = re.match(r'^(\d{4})$', clean)
    if m_y:
        year = int(m_y.group(1))
        return str(year), year
    return value.strip(), 0


def _parse_place(value):
    if not value:
        return '', '', '', ''
    parts = [p.strip() for p in value.split(',') if p.strip()]
    locality = ''
    county = ''
    state = ''
    country = ''

    if len(parts) >= 4:
        locality, county, state, country = parts[0], parts[1], parts[2], parts[3]
    elif len(parts) == 3:
        locality, state, country = parts[0], parts[1], parts[2]
    elif len(parts) == 2:
        state, country = parts[0], parts[1]
    elif len(parts) == 1:
        state = parts[0]

    state_lower = state.lower().strip()
    if state_lower in _STATE_ABBR:
        state = _STATE_ABBR[state_lower]
    elif state.upper() in _ABBR_SET:
        state = state.upper()

    county_lower = county.lower()
    if county_lower.endswith(' county'):
        county = county[:-7].strip()

    display = locality or county
    return display, county, state, value


def _state_coords(state_abbr):
    return _STATE_COORDS.get(state_abbr, (0.0, 0.0))


# ---- Individual & family parsing ------------------------------------------

def _get_sub_fields(record_lines, start_idx, base_level):
    fields = {}
    i = start_idx
    while i < len(record_lines):
        level, tag, value = record_lines[i]
        if level <= base_level:
            break
        if level == base_level + 1:
            if tag in ('CONC', 'CONT'):
                prev_key = list(fields.keys())[-1] if fields else None
                if prev_key:
                    sep = '\n' if tag == 'CONT' else ''
                    fields[prev_key] += sep + value
            else:
                fields[tag] = value
        i += 1
    return fields


def _parse_individual(xref, record_lines):
    person = {
        'xref': xref, 'given': '', 'surname': '', 'name': '',
        'sex': 'M', 'born_display': '', 'born_year': 0,
        'died_display': '', 'died_year': 0,
        'events': [], 'notes': [], 'fams_refs': [], 'famc_refs': []
    }

    i = 0
    while i < len(record_lines):
        level, tag, value = record_lines[i]
        if level != 1:
            i += 1
            continue

        if tag == 'NAME' and not person['name']:
            given, surname, full = _parse_name(value)
            person['given'] = given
            person['surname'] = surname
            person['name'] = full
        elif tag == 'SEX':
            person['sex'] = value.upper() if value.upper() in ('M', 'F') else 'M'
        elif tag == 'FAMS':
            person['fams_refs'].append(value)
        elif tag == 'FAMC':
            person['famc_refs'].append(value)
        elif tag in ('BIRT', 'DEAT', 'BURI', 'CENS', 'RESI', 'OCCU', 'EDUC',
                      'MILI', 'GRAD', 'EMIG', 'IMMI', 'NATU', 'EVEN', 'RETI',
                      'PROB', 'WILL', 'BAPM', 'CHR', 'CONF'):
            sub = _get_sub_fields(record_lines, i + 1, level)
            date_display, date_year = _parse_date(sub.get('DATE', ''))
            place_display, county, state, place_full = _parse_place(sub.get('PLAC', ''))
            event_type = sub.get('TYPE', '') or value
            note = sub.get('NOTE', '')

            if tag == 'BIRT':
                person['born_display'] = date_display
                person['born_year'] = date_year
            elif tag == 'DEAT':
                person['died_display'] = date_display
                person['died_year'] = date_year

            person['events'].append({
                'tag': tag, 'type': event_type,
                'date_display': date_display, 'year': date_year,
                'place_display': place_display, 'county': county,
                'state': state, 'place_full': place_full,
                'note': note
            })
        elif tag == 'NOTE':
            note_text = value
            sub = _get_sub_fields(record_lines, i + 1, level)
            for k in ('CONC', 'CONT'):
                if k in sub:
                    note_text += ('\n' if k == 'CONT' else '') + sub[k]
            j = i + 1
            while j < len(record_lines) and record_lines[j][0] > level:
                lv, tg, vl = record_lines[j]
                if tg == 'CONT':
                    note_text += '\n' + vl
                elif tg == 'CONC':
                    note_text += vl
                j += 1
            if note_text.strip():
                person['notes'].append(note_text.strip())
        i += 1

    return person


def _parse_family(xref, record_lines):
    family = {
        'xref': xref, 'husb': '', 'wife': '', 'children': [],
        'marriage_date': '', 'marriage_year': 0,
        'marriage_place': '', 'marriage_county': '', 'marriage_state': ''
    }
    i = 0
    while i < len(record_lines):
        level, tag, value = record_lines[i]
        if level != 1:
            i += 1
            continue
        if tag == 'HUSB':
            family['husb'] = value
        elif tag == 'WIFE':
            family['wife'] = value
        elif tag == 'CHIL':
            family['children'].append(value)
        elif tag == 'MARR':
            sub = _get_sub_fields(record_lines, i + 1, level)
            family['marriage_date'], family['marriage_year'] = _parse_date(sub.get('DATE', ''))
            disp, cnty, st, full = _parse_place(sub.get('PLAC', ''))
            family['marriage_place'] = disp
            family['marriage_county'] = cnty
            family['marriage_state'] = st
        i += 1
    return family


# ---- Narrative generation -------------------------------------------------

_EVENT_LABELS = {
    'BIRT': 'was born', 'DEAT': 'died', 'BURI': 'was buried',
    'CENS': 'was recorded in the census', 'RESI': 'lived',
    'OCCU': 'worked', 'EDUC': 'attended school', 'MILI': 'served in the military',
    'GRAD': 'graduated', 'EMIG': 'emigrated', 'IMMI': 'immigrated',
    'NATU': 'was naturalized', 'RETI': 'retired', 'PROB': 'had estate in probate',
    'BAPM': 'was baptized', 'CHR': 'was christened', 'CONF': 'was confirmed',
}

def _generate_narrative(person, event):
    tag = event['tag']
    pronoun = 'He' if person['sex'] == 'M' else 'She'
    verb = _EVENT_LABELS.get(tag, 'had an event')

    if tag == 'BIRT':
        subject = person['name']
    else:
        subject = pronoun

    parts = [f'{subject} {verb}']

    if tag == 'OCCU' and event['type']:
        parts = [f'{subject} worked as {event["type"]}']
    elif tag == 'EDUC' and event['type']:
        parts = [f'{subject} attended {event["type"]}']
    elif tag == 'MILI' and event['type']:
        parts = [f'{subject} served in the {event["type"]}']

    if event['date_display']:
        has_day = re.match(r'^[A-Z][a-z]+ \d{1,2},', event['date_display'])
        if has_day and tag in ('BIRT', 'DEAT', 'BURI', 'MARR'):
            parts.append(f'on {event["date_display"]}')
        else:
            parts.append(f'in {event["date_display"]}')

    if event['place_full']:
        parts.append(f'in {event["place_full"]}')

    sentence = ' '.join(parts).rstrip('.') + '.'
    if event['note']:
        sentence += f' {event["note"]}'
    return sentence


# ---- Slug ID generation ---------------------------------------------------

def _make_slug(name, seen_slugs):
    slug = name.lower().strip()
    slug = re.sub(r'[^a-z0-9\s]', '', slug)
    slug = re.sub(r'\s+', '_', slug).strip('_')
    if not slug:
        slug = 'unknown'
    base = slug
    counter = 2
    while slug in seen_slugs:
        slug = f'{base}_{counter}'
        counter += 1
    seen_slugs.add(slug)
    return slug


# ---- Generation inference --------------------------------------------------

def _infer_generations(people_by_xref, families):
    gen_map = {}
    parent_of = {}
    for fam in families.values():
        for child_xref in fam['children']:
            parents = []
            if fam['husb']:
                parents.append(fam['husb'])
            if fam['wife']:
                parents.append(fam['wife'])
            parent_of[child_xref] = parents

    def _get_gen(xref, visited=None):
        if xref in gen_map:
            return gen_map[xref]
        if visited is None:
            visited = set()
        if xref in visited:
            return 1
        visited.add(xref)
        parents = parent_of.get(xref, [])
        if not parents:
            gen_map[xref] = 1
            return 1
        max_parent_gen = max(_get_gen(p, visited) for p in parents)
        gen_map[xref] = max_parent_gen + 1
        return gen_map[xref]

    for xref in people_by_xref:
        _get_gen(xref)

    min_gen = min(gen_map.values()) if gen_map else 1
    for xref in gen_map:
        gen_map[xref] -= (min_gen - 1)
    return gen_map


# ---- Geocoding -------------------------------------------------------------

_geocode_cache = {}

def _geocode_place(place_full, state_abbr):
    if not place_full and not state_abbr:
        return 0.0, 0.0

    cache_key = place_full or state_abbr
    if cache_key in _geocode_cache:
        return _geocode_cache[cache_key]

    try:
        from geopy.geocoders import Nominatim
        from geopy.exc import GeocoderTimedOut, GeocoderServiceError
        geolocator = Nominatim(user_agent='family_archive_converter', timeout=5)
        time.sleep(1.1)
        try:
            location = geolocator.geocode(place_full or state_abbr)
            if location:
                result = (location.latitude, location.longitude)
                _geocode_cache[cache_key] = result
                return result
        except (GeocoderTimedOut, GeocoderServiceError):
            pass
    except ImportError:
        pass

    if state_abbr and state_abbr in _STATE_COORDS:
        result = _STATE_COORDS[state_abbr]
        _geocode_cache[cache_key] = result
        return result

    return 0.0, 0.0


# ---- Main conversion ------------------------------------------------------

def parse_gedcom(filepath, geocode=False, progress_callback=None):
    lines = _read_gedcom(filepath)
    indi_records, fam_records = _extract_records(lines)

    individuals = {}
    for xref, rec_lines in indi_records.items():
        individuals[xref] = _parse_individual(xref, rec_lines)

    families = {}
    for xref, rec_lines in fam_records.items():
        families[xref] = _parse_family(xref, rec_lines)

    gen_map = _infer_generations(individuals, families)
    seen_slugs = set()
    xref_to_slug = {}

    people = []
    for xref, person in individuals.items():
        slug = _make_slug(person['name'], seen_slugs)
        xref_to_slug[xref] = slug

        details = []
        for event in person['events']:
            narrative = _generate_narrative(person, event)
            if narrative:
                details.append(narrative)
        for note in person['notes']:
            details.append(note)

        age = ''
        if person['born_year'] and person['died_year']:
            age = str(person['died_year'] - person['born_year'])
            pronoun = 'He' if person['sex'] == 'M' else 'She'
            details.append(f'{pronoun} lived to the age of {age}.')

        people.append({
            'id': slug,
            'name': person['name'],
            'gen': gen_map.get(xref, 1),
            'born': str(person['born_year']) if person['born_year'] else '',
            'died': str(person['died_year']) if person['died_year'] else '',
            'photo_url': '',
            'details': details,
            'xref': xref
        })

    links = []
    for fam_xref, fam in families.items():
        husb_slug = xref_to_slug.get(fam['husb'], '')
        wife_slug = xref_to_slug.get(fam['wife'], '')

        if husb_slug and wife_slug:
            links.append({'source': husb_slug, 'target': wife_slug, 'relationship': 'spouse'})

        for child_xref in fam['children']:
            child_slug = xref_to_slug.get(child_xref, '')
            if not child_slug:
                continue
            if husb_slug:
                links.append({'source': husb_slug, 'target': child_slug, 'relationship': 'parent-child'})
            if wife_slug:
                links.append({'source': wife_slug, 'target': child_slug, 'relationship': 'parent-child'})

        if fam['marriage_year'] and (husb_slug or wife_slug):
            husb = individuals.get(fam['husb'])
            wife = individuals.get(fam['wife'])
            date_str = fam['marriage_date']
            place_str = fam['marriage_place']
            has_day = bool(re.match(r'^[A-Z][a-z]+ \d{1,2},', date_str))
            date_part = f' on {date_str}' if date_str and has_day else f' in {date_str}' if date_str else ''
            place_part = f' in {place_str}' if place_str else ''
            if husb:
                spouse_name = wife['name'] if wife else 'unknown'
                husb_person = next((p for p in people if p['xref'] == fam['husb']), None)
                if husb_person:
                    husb_person['details'].append(f'He married {spouse_name}{date_part}{place_part}.')
            if wife:
                spouse_name = husb['name'] if husb else 'unknown'
                wife_person = next((p for p in people if p['xref'] == fam['wife']), None)
                if wife_person:
                    wife_person['details'].append(f'She married {spouse_name}{date_part}{place_part}.')

    waypoints = []
    event_to_mig = {
        'BIRT': 'Born', 'DEAT': 'Died', 'CENS': 'Census', 'MARR': 'Marriage'
    }

    total = len(people)
    for idx, person in enumerate(people):
        if progress_callback:
            progress_callback(idx + 1, total, person['name'])
        indi = individuals.get(person['xref'])
        if not indi:
            continue
        for event in indi['events']:
            if not event['year']:
                continue
            state = event['state']
            county = event['county'] or event['place_display']

            if geocode:
                lat, lng = _geocode_place(event['place_full'], state)
            elif state in _STATE_COORDS:
                lat, lng = _STATE_COORDS[state]
            else:
                lat, lng = 0.0, 0.0

            if lat == 0.0 and lng == 0.0 and not state:
                continue

            mig_event = event_to_mig.get(event['tag'], 'Other')
            waypoints.append({
                'person_id': person['id'],
                'year': event['year'],
                'county': county,
                'state': state,
                'latitude': round(lat, 4),
                'longitude': round(lng, 4),
                'event': mig_event,
                'source_doc': '',
                'details': _generate_narrative(indi, event)
            })

    for fam in families.values():
        if not fam['marriage_year']:
            continue
        for spouse_xref in (fam['husb'], fam['wife']):
            slug = xref_to_slug.get(spouse_xref, '')
            if not slug:
                continue
            state = fam['marriage_state']
            county = fam['marriage_county'] or fam['marriage_place']
            if geocode:
                lat, lng = _geocode_place(
                    f"{fam['marriage_place']}, {state}" if state else fam['marriage_place'], state)
            elif state in _STATE_COORDS:
                lat, lng = _STATE_COORDS[state]
            else:
                lat, lng = 0.0, 0.0
            waypoints.append({
                'person_id': slug,
                'year': fam['marriage_year'],
                'county': county,
                'state': state,
                'latitude': round(lat, 4),
                'longitude': round(lng, 4),
                'event': 'Marriage',
                'source_doc': '',
                'details': f'Marriage in {fam["marriage_place"]}, {state}'.strip(', ')
            })

    for p in people:
        del p['xref']

    return people, links, waypoints


def write_csvs(people, links, waypoints, output_dir, basename=''):
    prefix = f'{basename}_' if basename else ''

    max_details = max((len(p['details']) for p in people), default=0)
    points_rows = []
    for p in people:
        row = {
            'ID': p['id'],
            'Name': p['name'],
            'Gen': p['gen'],
            'Born': p['born'],
            'Died': p['died'],
            'Photo URL': p['photo_url'],
        }
        for i, detail in enumerate(p['details']):
            col = 'Details' if i == 0 else f'Details.{i}'
            row[col] = detail
        points_rows.append(row)

    points_df = pd.DataFrame(points_rows)
    points_path = os.path.join(output_dir, f'{prefix}Points.csv')
    points_df.to_csv(points_path, index=False, encoding='utf-8-sig')

    links_df = pd.DataFrame([
        {'Source': l['source'], 'Target': l['target'], 'Relationship': l['relationship']}
        for l in links
    ])
    links_path = os.path.join(output_dir, f'{prefix}Links.csv')
    links_df.to_csv(links_path, index=False, encoding='utf-8-sig')

    mig_df = pd.DataFrame(waypoints, columns=[
        'person_id', 'year', 'county', 'state', 'latitude', 'longitude',
        'event', 'source_doc', 'details'
    ])
    mig_df = mig_df.sort_values(['person_id', 'year']).drop_duplicates(
        subset=['person_id', 'year', 'county', 'state', 'event'], keep='first')
    mig_path = os.path.join(output_dir, f'{prefix}Migration.csv')
    mig_df.to_csv(mig_path, index=False, encoding='utf-8-sig')

    return points_path, links_path, mig_path


# ---- Entry point -----------------------------------------------------------

def main():
    root = tk.Tk()
    root.withdraw()

    ged_path = filedialog.askopenfilename(
        title='Select GEDCOM file (.ged)',
        filetypes=[('GEDCOM files', '*.ged'), ('All files', '*.*')])
    if not ged_path:
        sys.exit(0)

    do_geocode = messagebox.askyesno(
        'Geocoding',
        'Attempt to geocode locations using Nominatim?\n\n'
        'Yes: more accurate coordinates (requires internet, slower)\n'
        'No: use US state centroids as approximate coordinates (fast)\n\n'
        'You can always improve coordinates later.')

    messagebox.showinfo('Processing',
        f'Parsing GEDCOM file...\n\nThis may take a moment for large files.')

    try:
        people, links, waypoints = parse_gedcom(
            ged_path, geocode=do_geocode,
            progress_callback=lambda i, t, name: None)
    except Exception as e:
        messagebox.showerror('Error', f'Failed to parse GEDCOM:\n{e}')
        sys.exit(1)

    output_dir = os.path.dirname(ged_path)
    basename = os.path.splitext(os.path.basename(ged_path))[0]

    points_path, links_path, mig_path = write_csvs(
        people, links, waypoints, output_dir, basename)

    msg = (f'Conversion complete!\n\n'
           f'People: {len(people)}\n'
           f'Relationships: {len(links)}\n'
           f'Migration waypoints: {len(waypoints)}\n\n'
           f'Files saved to:\n'
           f'  {os.path.basename(points_path)}\n'
           f'  {os.path.basename(links_path)}\n'
           f'  {os.path.basename(mig_path)}\n\n'
           f'You can now open these in the Family Archive Viewer.')
    messagebox.showinfo('Done', msg)
    root.destroy()


if __name__ == '__main__':
    main()
