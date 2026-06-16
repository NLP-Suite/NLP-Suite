"""Standalone Family Archive Viewer.

Three-tab application: Family Tree, Relations, Migration.
Double-click the executable (or run from source) to pick data files,
then view your family archive interactively in the browser.

Expected files:
  - Points (xlsx/csv): ID, Name, Gen, Born, Died, Photo URL, Details...
  - Links  (xlsx/csv): Source, Target, Relationship (spouse / parent-child)
  - Migration (csv, optional): person_id, year, county, state, latitude, longitude, event, details

Usage (source):  python family_archive_app.py
Usage (exe):     FamilyArchiveViewer.exe
"""

import os
import sys
import json
import tkinter as tk
from tkinter import filedialog, messagebox
import webbrowser

import pandas as pd


def _read_file(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in ('.xlsx', '.xls'):
        return pd.read_excel(path)
    try:
        return pd.read_csv(path, encoding='utf-8', error_bad_lines=False)
    except TypeError:
        return pd.read_csv(path, encoding='utf-8', on_bad_lines='skip')
    except UnicodeDecodeError:
        try:
            return pd.read_csv(path, encoding='ISO-8859-1', error_bad_lines=False)
        except TypeError:
            return pd.read_csv(path, encoding='ISO-8859-1', on_bad_lines='skip')


def _parse_points(df):
    col_map = {}
    for c in df.columns:
        cl = c.lower().strip()
        if cl == 'id':
            col_map['id'] = c
        elif cl == 'name':
            col_map['name'] = c
        elif cl in ('gen', 'generation'):
            col_map['gen'] = c
        elif cl == 'born':
            col_map['born'] = c
        elif cl == 'died':
            col_map['died'] = c
        elif cl in ('photo url', 'photo_url', 'image', 'photo'):
            col_map['photo_url'] = c

    detail_cols = [c for c in df.columns
                   if c.lower().strip() == 'details'
                   or c.lower().strip().startswith('details.')]

    people = []
    for _, row in df.iterrows():
        pid = str(row.get(col_map.get('id', 'ID'), '')).strip()
        if not pid or pid.lower() == 'nan':
            continue

        born = str(row.get(col_map.get('born', 'Born'), '')).strip()
        died = str(row.get(col_map.get('died', 'Died'), '')).strip()
        for field_val in [born, died]:
            pass
        born = born.replace('.0', '') if born.lower() not in ('nan', '') else ''
        died = died.replace('.0', '') if died.lower() not in ('nan', '') else ''

        gen_val = row.get(col_map.get('gen', 'Gen'), 0)
        try:
            gen = int(float(gen_val))
        except (ValueError, TypeError):
            gen = 0

        photo = str(row.get(col_map.get('photo_url', 'Photo URL'), '')).strip()
        if not photo or photo.lower() in ('nan', 'url', ''):
            photo = ''
        elif not photo.startswith(('http://', 'https://', '/')):
            photo = ''

        details = []
        for dc in detail_cols:
            val = str(row.get(dc, '')).strip()
            if val and val.lower() != 'nan':
                details.append(val)

        people.append({
            'id': pid,
            'name': str(row.get(col_map.get('name', 'Name'), '')).strip(),
            'gen': gen,
            'born': born,
            'died': died,
            'photo_url': photo,
            'details': details,
            'spouses': [],
            'children': [],
            'parents': []
        })
    return people


def _parse_links(df):
    links = []
    for _, row in df.iterrows():
        source = str(row.get('Source', '')).strip()
        target = str(row.get('Target', '')).strip()
        rel = str(row.get('Relationship', '')).strip().lower()
        if source and target and source.lower() != 'nan' and target.lower() != 'nan':
            links.append({'source': source, 'target': target, 'relationship': rel})
    return links


def _parse_migration(df):
    waypoints = []
    for _, row in df.iterrows():
        pid = str(row.get('person_id', '')).strip()
        if not pid or pid.lower() == 'nan':
            continue
        try:
            year = int(float(row.get('year', 0) or 0))
        except (ValueError, TypeError):
            continue
        if not year:
            continue
        try:
            lat = float(row.get('latitude', 0) or 0)
            lng = float(row.get('longitude', 0) or 0)
        except (ValueError, TypeError):
            lat, lng = 0.0, 0.0
        waypoints.append({
            'person_id': pid,
            'year': year,
            'county': str(row.get('county', '')).strip(),
            'state': str(row.get('state', '')).strip(),
            'lat': lat,
            'lng': lng,
            'event': str(row.get('event', '')).strip(),
            'details': str(row.get('details', '')).strip()
        })
    return waypoints


def _build_relationships(people, links):
    spouse_map = {}
    children_map = {}
    parents_map = {}

    for link in links:
        s, t, rel = link['source'], link['target'], link['relationship']
        if rel == 'spouse':
            spouse_map.setdefault(s, []).append(t)
            spouse_map.setdefault(t, []).append(s)
        elif rel == 'parent-child':
            children_map.setdefault(s, []).append(t)
            parents_map.setdefault(t, []).append(s)

    for link in links:
        if link['relationship'] == 'parent-child':
            s, t = link['source'], link['target']
            for sp in spouse_map.get(s, []):
                if t not in children_map.get(sp, []):
                    children_map.setdefault(sp, []).append(t)
                if sp not in parents_map.get(t, []):
                    parents_map.setdefault(t, []).append(sp)

    for p in people:
        p['spouses'] = list(set(spouse_map.get(p['id'], [])))
        p['children'] = list(set(children_map.get(p['id'], [])))
        p['parents'] = list(set(parents_map.get(p['id'], [])))


def _build_html(people, links, waypoints, output_dir, title):
    _build_relationships(people, links)

    migration_by_person = {}
    for wp in waypoints:
        migration_by_person.setdefault(wp['person_id'], []).append(wp)
    for pid in migration_by_person:
        migration_by_person[pid].sort(key=lambda w: w['year'])

    migration_persons = []
    for p in people:
        if p['id'] in migration_by_person:
            migration_persons.append({
                'id': p['id'],
                'name': p['name'],
                'waypoints': migration_by_person[p['id']]
            })

    has_migration = len(waypoints) > 0

    html = _HTML_TEMPLATE
    html = html.replace('__TITLE__', title)
    html = html.replace('__PEOPLE_JSON__', json.dumps(people, ensure_ascii=False))
    html = html.replace('__LINKS_JSON__', json.dumps(links, ensure_ascii=False))
    html = html.replace('__MIGRATION_JSON__', json.dumps(migration_persons, ensure_ascii=False))
    html = html.replace('__HAS_MIGRATION__', 'true' if has_migration else 'false')

    safe_title = ''.join(c if c.isalnum() or c in ' _-' else '_' for c in title)
    output_path = os.path.join(output_dir, f'{safe_title}_family_archive.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    return output_path


_HTML_TEMPLATE = r"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>__TITLE__ — Family Archive</title>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Segoe UI','Inter',Arial,sans-serif;background:#faf9f7;overflow:hidden;height:100vh;}
#header{background:#faf9f7;border-bottom:1px solid #e8e3dd;padding:10px 24px;display:flex;align-items:center;}
#header h1{font-size:17px;color:#2c2c2c;font-weight:600;}
#tab-bar{display:flex;gap:0;border-bottom:1px solid #e8e3dd;background:#faf9f7;padding-left:24px;flex-shrink:0;}
.tab-btn{padding:11px 24px;font-size:13px;font-weight:400;color:#8a8279;background:transparent;
  border:none;border-bottom:2px solid transparent;cursor:pointer;font-family:inherit;margin-bottom:-1px;
  transition:color .15s,border-color .15s;}
.tab-btn.active{color:#2c2c2c;border-bottom-color:#7c9a92;font-weight:500;}
.tab-btn:hover{color:#2c2c2c;}
.tab-content{display:none;width:100%;height:calc(100vh - 90px);position:relative;}
.tab-content.active{display:flex;}
#tree-container,#relations-container{width:100%;height:100%;}

/* Migration layout */
#migration-container{display:flex;flex:1;height:100%;overflow:hidden;}
#person-sidebar{width:260px;flex-shrink:0;border-right:1px solid #e8e3dd;background:#faf9f7;
  display:flex;flex-direction:column;}
#sidebar-header{padding:14px 20px 10px;border-bottom:1px solid #e8e3dd;}
#sidebar-header h3{font-size:11px;font-weight:600;color:#a39e96;text-transform:uppercase;letter-spacing:.8px;}
#sidebar-header p{font-size:11px;color:#8a8279;margin-top:4px;line-height:1.4;}
#person-list{flex:1;overflow-y:auto;}
.person-btn{display:flex;align-items:center;gap:10px;width:100%;text-align:left;padding:10px 20px 10px 17px;
  border:none;border-left:3px solid transparent;background:transparent;cursor:pointer;font-family:inherit;
  transition:background .15s,border-color .15s;}
.person-btn.selected{background:#f0ede8;}
.person-btn:hover{background:#f0ede8;}
.person-dot{width:10px;height:10px;border-radius:50%;border:1.5px solid;flex-shrink:0;
  transition:background .15s;}
.person-info{flex:1;min-width:0;}
.person-name{font-size:13px;color:#3d3832;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.person-btn.selected .person-name{font-weight:500;color:#2c2c2c;}
.person-lifespan{font-size:11px;color:#8a8279;margin-top:2px;}
#map-area{flex:1;display:flex;flex-direction:column;}
#map{flex:1;z-index:1;}
#timeline-bar{height:64px;flex-shrink:0;background:#faf9f7;border-top:1px solid #e8e3dd;
  display:flex;align-items:center;padding:0 20px;gap:14px;}
#mig-play{width:32px;height:32px;display:flex;align-items:center;justify-content:center;
  background:transparent;border:1px solid #e8e3dd;border-radius:6px;cursor:pointer;
  color:#5a5550;font-size:14px;flex-shrink:0;}
.speed-btn{padding:3px 8px;font-size:11px;font-weight:400;color:#8a8279;background:transparent;
  border:1px solid #e8e3dd;border-radius:4px;cursor:pointer;font-family:inherit;}
.speed-btn.active{font-weight:600;color:#2c2c2c;background:#e8e3dd;}
#mig-year{font-size:16px;font-weight:600;color:#2c2c2c;min-width:48px;text-align:center;flex-shrink:0;}
#mig-slider-wrap{flex:1;position:relative;height:40px;display:flex;align-items:center;cursor:pointer;}
#mig-slider{width:100%;cursor:pointer;accent-color:#7c9a92;}

/* Detail panel */
#detail-panel{position:fixed;right:-460px;top:0;width:440px;height:100vh;background:#faf9f7;
  border-left:1px solid #e8e3dd;box-shadow:-4px 0 16px rgba(0,0,0,.06);transition:right .3s ease;
  overflow-y:auto;z-index:200;font-family:inherit;}
#detail-panel.open{right:0;}
#detail-close{position:absolute;top:12px;right:12px;width:28px;height:28px;border:1px solid #e8e3dd;
  border-radius:6px;background:transparent;color:#8a8279;cursor:pointer;font-size:18px;line-height:1;
  display:flex;align-items:center;justify-content:center;z-index:1;}
#detail-content{padding:40px 28px 20px;}
.dp-avatar{display:flex;justify-content:center;margin-bottom:20px;}
.dp-avatar img{width:96px;height:96px;border-radius:50%;object-fit:cover;}
.dp-initials{width:96px;height:96px;border-radius:50%;display:flex;align-items:center;
  justify-content:center;color:#fff;font-size:32px;font-weight:600;letter-spacing:1px;}
.dp-name{font-size:20px;font-weight:600;color:#2c2c2c;text-align:center;margin-bottom:4px;line-height:1.3;}
.dp-dates{font-size:14px;color:#8a8279;text-align:center;margin-bottom:6px;}
.dp-gen{font-size:12px;color:#a39e96;text-align:center;margin-bottom:24px;letter-spacing:.3px;}
.dp-divider{height:1px;background:#e8e3dd;margin:18px 0;}
.dp-section{margin-bottom:18px;}
.dp-section h3{font-size:11px;font-weight:600;color:#a39e96;text-transform:uppercase;
  letter-spacing:.8px;margin-bottom:10px;}
.dp-row{display:flex;justify-content:space-between;margin-bottom:6px;}
.dp-row span:first-child{font-size:13px;color:#8a8279;}
.dp-row span:last-child{font-size:13px;color:#3d3832;text-align:right;}
.dp-section ul{list-style:none;padding:0;}
.dp-section li{font-size:13px;color:#3d3832;line-height:1.55;margin-bottom:7px;padding-left:12px;position:relative;}
.dp-section li::before{content:'';position:absolute;left:0;top:.6em;width:4px;height:4px;
  border-radius:50%;background:#c4bfb8;}
.dp-relgroup{margin-bottom:12px;}
.dp-rellabel{font-size:11px;color:#8a8279;display:block;margin-bottom:2px;}
.dp-relname{font-size:13px;color:#3d3832;margin-bottom:2px;padding-left:8px;cursor:pointer;
  text-decoration:underline;text-decoration-color:#e8e3dd;}
.dp-relname:hover{color:#7c9a92;}
.dp-nofamily{font-size:13px;color:#a39e96;font-style:italic;}

/* Records in detail panel */
.dp-collapsible{cursor:pointer;user-select:none;}
.dp-collapsible::after{content:' ▾';font-size:10px;}
.dp-collapsible.collapsed::after{content:' ▸';}
.dp-record{font-size:12px !important;color:#5a5550 !important;line-height:1.5 !important;}
.dp-rec-badge{display:inline-block;padding:1px 6px;border-radius:3px;font-size:10px;font-weight:600;
  color:#fff;background:#8a8279;margin-right:4px;vertical-align:middle;text-transform:uppercase;letter-spacing:.3px;}

/* Records tab */
#records-container{display:flex;flex-direction:column;width:100%;height:100%;overflow:hidden;}
#records-toolbar{padding:12px 20px;border-bottom:1px solid #e8e3dd;display:flex;gap:10px;align-items:center;flex-wrap:wrap;}
#records-search{flex:1;min-width:200px;padding:7px 12px;border:1px solid #e8e3dd;border-radius:6px;
  font-size:13px;font-family:inherit;background:#fff;color:#2c2c2c;}
.rec-filter-btn{padding:4px 10px;border:1px solid #e8e3dd;border-radius:4px;font-size:11px;
  cursor:pointer;font-family:inherit;background:#fff;color:#5a5550;transition:all .15s;}
.rec-filter-btn.active{background:#2c2c2c;color:#fff;border-color:#2c2c2c;}
.rec-filter-btn:hover{border-color:#2c2c2c;}
#records-count{font-size:11px;color:#8a8279;margin-left:auto;}
#records-table-wrap{flex:1;overflow:auto;padding:0;}
#records-table{width:100%;border-collapse:collapse;font-size:13px;}
#records-table th{position:sticky;top:0;background:#f0ede8;padding:8px 14px;text-align:left;
  font-size:11px;font-weight:600;color:#8a8279;text-transform:uppercase;letter-spacing:.5px;border-bottom:1px solid #e8e3dd;}
#records-table td{padding:8px 14px;border-bottom:1px solid #f0ede8;color:#3d3832;vertical-align:top;}
#records-table tr:hover td{background:#f7f5f2;}
#records-table .rec-person{font-weight:500;cursor:pointer;color:#446891;white-space:nowrap;}
#records-table .rec-person:hover{text-decoration:underline;}
#records-table .rec-type{font-size:11px;font-weight:600;color:#fff;background:#8a8279;
  padding:2px 6px;border-radius:3px;text-transform:uppercase;letter-spacing:.3px;white-space:nowrap;}
#records-table .rec-citation{max-width:500px;line-height:1.5;}

/* Leaflet tooltip override */
.head-label{background:rgba(250,249,247,.96);border:1px solid #e8e3dd;border-radius:8px;
  padding:5px 10px;box-shadow:0 4px 12px rgba(0,0,0,.08);font-family:'Segoe UI','Inter',sans-serif;
  font-size:12px;font-weight:600;color:#2c2c2c;}
.head-label::before{border-top-color:#e8e3dd !important;}

/* No-migration notice */
.no-data{display:flex;align-items:center;justify-content:center;height:100%;width:100%;color:#8a8279;font-size:14px;}

/* Generation zoom buttons */
.gen-btn{padding:5px 10px;border:1px solid #c4bfb8;border-radius:4px;background:#fff;
  color:#2c2c2c;font-size:12px;cursor:pointer;font-family:inherit;transition:all 0.2s;}
.gen-btn:hover{background:#2c2c2c;color:#fff;}
.gen-btn.active{background:#2c2c2c;color:#fff;font-weight:600;}

/* vis.js navigation buttons */
div.vis-network div.vis-navigation div.vis-button{background-color:rgba(250,249,247,0.85);border:1px solid #c4bfb8;border-radius:4px;}
div.vis-network div.vis-navigation div.vis-button:hover{background-color:#2c2c2c;box-shadow:none;}
</style>
</head><body>

<div id="header"><h1>__TITLE__ — Family Archive</h1></div>

<div id="tab-bar">
  <button class="tab-btn active" data-tab="tree" onclick="switchTab('tree')">Family Tree</button>
  <button class="tab-btn" data-tab="relations" onclick="switchTab('relations')">Relations</button>
  <button class="tab-btn" data-tab="migration" id="migration-tab-btn" onclick="switchTab('migration')"
    style="display:none">Migration</button>
  <button class="tab-btn" data-tab="records" id="records-tab-btn" onclick="switchTab('records')"
    style="display:none">Records</button>
</div>

<div id="tab-tree" class="tab-content active">
  <div id="tree-container"></div>
</div>

<div id="tab-relations" class="tab-content">
  <div id="relations-container"></div>
</div>

<div id="tab-migration" class="tab-content">
  <div id="migration-container">
    <div id="person-sidebar">
      <div id="sidebar-header">
        <h3>People</h3>
        <p>Click to add or remove from the map</p>
      </div>
      <div id="person-list"></div>
    </div>
    <div id="map-area">
      <div id="map"></div>
      <div id="timeline-bar">
        <button id="mig-play" onclick="migTogglePlay()" title="Play/Pause">&#9654;</button>
        <div style="display:flex;gap:4px;flex-shrink:0">
          <button class="speed-btn active" data-speed="1" onclick="migSetSpeed(1)">1x</button>
          <button class="speed-btn" data-speed="2" onclick="migSetSpeed(2)">2x</button>
          <button class="speed-btn" data-speed="4" onclick="migSetSpeed(4)">4x</button>
        </div>
        <div id="mig-year"></div>
        <div id="mig-slider-wrap">
          <input type="range" id="mig-slider" min="0" max="0" value="0" step="1"
            oninput="migScrub(parseInt(this.value))">
        </div>
      </div>
    </div>
  </div>
</div>

<div id="tab-records" class="tab-content">
  <div id="records-container">
    <div id="records-toolbar">
      <input type="text" id="records-search" placeholder="Search records..." oninput="filterRecords()">
      <div id="records-filters"></div>
      <span id="records-count"></span>
    </div>
    <div id="records-table-wrap">
      <table id="records-table">
        <thead><tr><th>Person</th><th>Type</th><th>Citation</th></tr></thead>
        <tbody id="records-tbody"></tbody>
      </table>
    </div>
  </div>
</div>

<!-- Detail Panel -->
<div id="detail-panel">
  <button id="detail-close" onclick="hideDetailPanel()">&times;</button>
  <div id="detail-content"></div>
</div>

<script>
// ===== DATA =====
var PEOPLE = __PEOPLE_JSON__;
var LINKS = __LINKS_JSON__;
var MIGRATION = __MIGRATION_JSON__;
var HAS_MIGRATION = __HAS_MIGRATION__;

var peopleById = {};
PEOPLE.forEach(function(p) { peopleById[p.id] = p; });

var GEN_COLORS = ['#7c9a92','#8a6534','#446891','#6e7e3a','#824f73','#b35e3c','#3d5866','#5a8861'];
var MIG_COLORS = ['#4d8c7f','#8a6534','#446891','#6e7e3a','#824f73','#b35e3c','#3d5866','#5a8861'];

// ===== UTILITIES =====
function getInitials(name) {
  var parts = name.trim().split(/\s+/);
  if (parts.length <= 1) return (parts[0] || '?').charAt(0).toUpperCase();
  return (parts[0].charAt(0) + parts[parts.length-1].charAt(0)).toUpperCase();
}
function formatDates(born, died) {
  if (born && died) return born + '–' + died;
  if (born) return 'b. ' + born;
  return 'dates unknown';
}
function ordinal(n) {
  var s = ['th','st','nd','rd'];
  var v = n % 100;
  return n + (s[(v-20)%10] || s[v] || s[0]);
}
function isRecord(fact) { return fact.indexOf('[Record]') === 0; }
function stripRecordPrefix(fact) { return fact.replace(/^\[Record\]\s*/, ''); }

function categorize(fact) {
  if (isRecord(fact)) return 'Records';
  var lower = fact.toLowerCase();
  var first = lower.split(/\s+/)[0] || '';
  if (first === 'his' || first === 'her') return 'Family';
  if (/\bwas born\b/.test(lower)) return 'Birth';
  if (/\blived to the age\b/.test(lower)) return 'Lifespan';
  if (/\b(died|was buried|burial|buried|obituary|entered probate|funeral)\b/.test(lower)) return 'Death';
  if (/\b(marriage|married)\b/.test(lower)) return 'Marriage';
  if (/\b(graduated|enrolled|attending|attended|began attending|school|college|university|medical school)\b/.test(lower)) return 'Education';
  if (/\b(lived (in|at)|moved to|relocated|lives in|resided)\b/.test(lower)) return 'Residences';
  if (/\b(worked as|served as|was employed|occupation|associated with|was a physician|practiced|traveled|private secretary)\b/.test(lower)) return 'Occupation';
  if (/\brecorded as\b/.test(lower)) return 'Records';
  if (/\b(was the (son|daughter)|had (one|two|three|a|no|an) (son|daughter|child|children|sister|brother|half)|never married|no known children)\b/.test(lower)) return 'Family';
  return 'Other';

}
function classifyRecord(text) {
  var t = text.toLowerCase();
  if (/census|enumeration district/.test(t)) return 'Census';
  if (/military|soldier|regiment|confederate|civil war|veteran/.test(t)) return 'Military';
  if (/marriage|married/.test(t)) return 'Marriage';
  if (/birth|christening|baptis/.test(t)) return 'Birth';
  if (/death|burial|cemetery|gravesite|obituary|funeral|find.a.grave/.test(t)) return 'Death';
  if (/probate|will|estate|executor/.test(t)) return 'Probate';
  if (/tax|revenue|assessment/.test(t)) return 'Tax';
  if (/immigration|emigration|passenger|ship|naturalization/.test(t)) return 'Immigration';
  if (/newspaper/.test(t)) return 'Newspaper';
  if (/postmaster|appointment/.test(t)) return 'Government';
  return 'Other';
}
function escHtml(s) { var d = document.createElement('div'); d.textContent = s; return d.innerHTML; }

// ===== TAB SWITCHING =====
var currentTab = 'tree';
var inited = { tree: false, relations: false, migration: false, records: false };

function switchTab(tabId) {
  document.querySelectorAll('.tab-btn').forEach(function(btn) {
    btn.classList.toggle('active', btn.getAttribute('data-tab') === tabId);
  });
  document.querySelectorAll('.tab-content').forEach(function(el) {
    el.classList.toggle('active', el.id === 'tab-' + tabId);
  });
  currentTab = tabId;
  if (!inited[tabId]) {
    inited[tabId] = true;
    if (tabId === 'tree') initFamilyTree();
    else if (tabId === 'relations') initRelations();
    else if (tabId === 'migration') initMigration();
    else if (tabId === 'records') initRecords();
  }
  if (tabId === 'tree' && treeNetwork) setTimeout(function(){ treeNetwork.fit(); }, 50);
  if (tabId === 'relations' && relNetwork) setTimeout(function(){ relNetwork.fit(); }, 50);
  if (tabId === 'migration' && migMap) setTimeout(function(){ migMap.invalidateSize(); }, 50);
}

// ===== DETAIL PANEL =====
function showDetailPanel(personId) {
  var p = peopleById[personId];
  if (!p) return;
  var panel = document.getElementById('detail-panel');
  var content = document.getElementById('detail-content');
  var initials = getInitials(p.name);
  var dates = formatDates(p.born, p.died);
  var genLabel = p.gen ? ordinal(p.gen) + ' Generation' : '';
  var color = GEN_COLORS[((p.gen||1) - 1) % GEN_COLORS.length];

  var h = '';
  // Avatar
  if (p.photo_url) {
    h += '<div class="dp-avatar"><img src="' + escHtml(p.photo_url) + '" alt="' + escHtml(p.name) + '"></div>';
  } else {
    h += '<div class="dp-avatar"><div class="dp-initials" style="background:'+color+'">' + initials + '</div></div>';
  }
  h += '<div class="dp-name">' + escHtml(p.name) + '</div>';
  h += '<p class="dp-dates">' + dates + '</p>';
  if (genLabel) h += '<p class="dp-gen">' + genLabel + '</p>';

  // Key Facts
  h += '<div class="dp-divider"></div>';
  h += '<div class="dp-section"><h3>KEY FACTS</h3>';
  h += '<div class="dp-row"><span>Born</span><span>' + (p.born || 'Unknown') + '</span></div>';
  h += '<div class="dp-row"><span>Died</span><span>' + (p.died || 'Unknown') + '</span></div>';
  if (genLabel) h += '<div class="dp-row"><span>Generation</span><span>' + genLabel + '</span></div>';
  h += '</div>';

  // Categorized narrative facts
  if (p.details && p.details.length > 0) {
    h += '<div class="dp-divider"></div>';
    var cats = {};
    var catOrder = ['Birth','Family','Education','Marriage','Residences','Occupation','Records','Death','Lifespan','Other'];
    p.details.forEach(function(fact) {
      var cat = categorize(fact);
      if (!cats[cat]) cats[cat] = [];
      cats[cat].push(fact);
    });
    catOrder.forEach(function(cat) {
      if (cats[cat] && cats[cat].length > 0) {
        if (cat === 'Records') {
          var recId = 'dp-records-' + Date.now();
          h += '<div class="dp-section"><h3 class="dp-collapsible" onclick="var el=document.getElementById(\'' + recId + '\');el.style.display=el.style.display===\'none\'?\'block\':\'none\';this.classList.toggle(\'collapsed\')">';
          h += '&#128196; RECORDS (' + cats[cat].length + ')</h3>';
          h += '<ul id="' + recId + '">';
          cats[cat].forEach(function(f) {
            var clean = stripRecordPrefix(f);
            var rtype = classifyRecord(clean);
            h += '<li class="dp-record"><span class="dp-rec-badge">' + rtype + '</span> ' + escHtml(clean) + '</li>';
          });
          h += '</ul></div>';
        } else {
          h += '<div class="dp-section"><h3>' + cat.toUpperCase() + '</h3><ul>';
          cats[cat].forEach(function(f) { h += '<li>' + escHtml(f) + '</li>'; });
          h += '</ul></div>';
        }
      }
    });
  }

  // Related people
  h += '<div class="dp-divider"></div>';
  h += '<div class="dp-section"><h3>RELATED PEOPLE</h3>';
  var hasRels = false;
  if (p.parents && p.parents.length > 0) {
    hasRels = true;
    h += '<div class="dp-relgroup"><span class="dp-rellabel">Parents</span>';
    p.parents.forEach(function(pid) {
      var r = peopleById[pid];
      h += '<p class="dp-relname" onclick="showDetailPanel(\'' + pid + '\')">' + escHtml(r ? r.name : pid) + '</p>';
    });
    h += '</div>';
  }
  if (p.spouses && p.spouses.length > 0) {
    hasRels = true;
    h += '<div class="dp-relgroup"><span class="dp-rellabel">' + (p.spouses.length > 1 ? 'Spouses' : 'Spouse') + '</span>';
    p.spouses.forEach(function(pid) {
      var r = peopleById[pid];
      h += '<p class="dp-relname" onclick="showDetailPanel(\'' + pid + '\')">' + escHtml(r ? r.name : pid) + '</p>';
    });
    h += '</div>';
  }
  if (p.children && p.children.length > 0) {
    hasRels = true;
    h += '<div class="dp-relgroup"><span class="dp-rellabel">Children</span>';
    p.children.forEach(function(pid) {
      var r = peopleById[pid];
      h += '<p class="dp-relname" onclick="showDetailPanel(\'' + pid + '\')">' + escHtml(r ? r.name : pid) + '</p>';
    });
    h += '</div>';
  }
  if (!hasRels) h += '<p class="dp-nofamily">No linked relatives in this dataset</p>';
  h += '</div>';

  content.innerHTML = h;
  panel.classList.add('open');
}

function hideDetailPanel() {
  document.getElementById('detail-panel').classList.remove('open');
}

// ===== FAMILY TREE (vis.js hierarchical) =====
var treeNetwork = null;

function initFamilyTree() {
  var container = document.getElementById('tree-container');
  var nodes = [];
  var edges = [];

  PEOPLE.forEach(function(p) {
    var color = GEN_COLORS[((p.gen||1) - 1) % GEN_COLORS.length];
    var label = p.name + '\n' + formatDates(p.born, p.died);
    var node = {
      id: p.id, label: label, level: p.gen || 1,
      shape: 'box',
      color: { background: color, border: color,
               highlight: { background: '#2c2c2c', border: '#2c2c2c' },
               hover: { background: color, border: '#2c2c2c' } },
      font: { color: '#fff', size: 12, face: "Segoe UI, Inter, sans-serif", multi: 'html' },
      margin: { top: 12, bottom: 12, left: 14, right: 14 },
      widthConstraint: { minimum: 130, maximum: 170 },
      shadow: { enabled: true, color: 'rgba(0,0,0,0.08)', size: 6, x: 0, y: 2 },
      borderWidth: 0, borderWidthSelected: 2
    };
    if (p.photo_url) {
      node.shape = 'circularImage';
      node.image = p.photo_url;
      node.brokenImage = '';
      node.size = 38;
      node.borderWidth = 3;
      node.color = { border: color, highlight: { border: '#2c2c2c' }, hover: { border: '#2c2c2c' } };
      node.font = { size: 11, color: '#2c2c2c', face: "Segoe UI, Inter, sans-serif" };
    }
    nodes.push(node);
  });

  // Deduplicate spouse edges (keep only one direction)
  var spouseSeen = {};
  LINKS.forEach(function(link) {
    if (link.relationship === 'parent-child') {
      edges.push({
        from: link.source, to: link.target,
        arrows: { to: { enabled: true, scaleFactor: 0.5 } },
        color: { color: '#c4bfb8', highlight: '#2c2c2c' },
        width: 1.5,
        smooth: { type: 'cubicBezier', forceDirection: 'vertical', roundness: 0.4 }
      });
    } else if (link.relationship === 'spouse') {
      var key = [link.source, link.target].sort().join('|');
      if (!spouseSeen[key]) {
        spouseSeen[key] = true;
        edges.push({
          from: link.source, to: link.target,
          dashes: [5, 5],
          color: { color: '#d4917a', highlight: '#c44' },
          width: 2, smooth: false
        });
      }
    }
  });

  var data = { nodes: new vis.DataSet(nodes), edges: new vis.DataSet(edges) };
  var nCount = nodes.length;
  var spacing = nCount > 80 ? 200 : nCount > 40 ? 180 : 170;
  var options = {
    layout: {
      hierarchical: {
        direction: 'UD', sortMethod: 'directed',
        levelSeparation: 180, nodeSpacing: spacing, treeSpacing: 250,
        blockShifting: true, edgeMinimization: true, parentCentralization: true
      }
    },
    physics: false,
    interaction: { hover: true, tooltipDelay: 200, zoomView: true, dragView: true,
                   navigationButtons: true, keyboard: { enabled: true } }
  };

  treeNetwork = new vis.Network(container, data, options);

  // Add gen-level zoom buttons
  var gens = {};
  PEOPLE.forEach(function(p) { gens[p.gen || 1] = true; });
  var genList = Object.keys(gens).map(Number).sort(function(a,b){return a-b;});
  if (genList.length > 1) {
    var genBar = document.createElement('div');
    genBar.style.cssText = 'position:absolute;top:8px;left:8px;z-index:10;display:flex;gap:4px;flex-wrap:wrap;';
    var fitBtn = document.createElement('button');
    fitBtn.textContent = 'Fit All';
    fitBtn.className = 'gen-btn';
    function setActiveGen(activeBtn) {
      genBar.querySelectorAll('.gen-btn').forEach(function(b) { b.classList.remove('active'); });
      activeBtn.classList.add('active');
    }
    fitBtn.onclick = function() {
      setActiveGen(fitBtn);
      treeNetwork.fit({ animation: { duration: 500, easingFunction: 'easeInOutQuad' } });
    };
    genBar.appendChild(fitBtn);
    genList.forEach(function(g) {
      var btn = document.createElement('button');
      btn.textContent = 'Gen ' + g;
      btn.className = 'gen-btn';
      btn.onclick = function() {
        setActiveGen(btn);
        var genNodes = PEOPLE.filter(function(p){return (p.gen||1)===g;}).map(function(p){return p.id;});
        treeNetwork.fit({ nodes: genNodes, animation: { duration: 400, easingFunction: 'easeInOutQuad' } });
        setTimeout(function() {
          var scale = treeNetwork.getScale();
          if (scale < 0.45) treeNetwork.moveTo({ scale: 0.45, animation: { duration: 300, easingFunction: 'easeInOutQuad' } });
        }, 450);
      };
      genBar.appendChild(btn);
    });
    container.style.position = 'relative';
    container.appendChild(genBar);
  }

  treeNetwork.on('click', function(params) {
    if (params.nodes.length > 0) showDetailPanel(params.nodes[0]);
    else hideDetailPanel();
  });
  treeNetwork.once('stabilized', function() { treeNetwork.fit({ animation: false }); });
}

// ===== RELATIONS (vis.js force-directed) =====
var relNetwork = null;

function initRelations() {
  var container = document.getElementById('relations-container');
  var nodes = [];
  var edges = [];

  var connCount = {};
  LINKS.forEach(function(link) {
    connCount[link.source] = (connCount[link.source] || 0) + 1;
    connCount[link.target] = (connCount[link.target] || 0) + 1;
  });
  var maxConn = Math.max.apply(null, Object.values(connCount).concat([1]));

  PEOPLE.forEach(function(p) {
    var color = GEN_COLORS[((p.gen||1) - 1) % GEN_COLORS.length];
    var freq = connCount[p.id] || 1;
    var sz = 12 + (freq / maxConn) * 28;
    var node = {
      id: p.id, label: p.name, color: color, size: sz,
      font: { size: 11, color: '#2c2c2c', face: "Segoe UI, Inter, sans-serif" },
      shape: 'dot',
      title: p.name + ' (' + formatDates(p.born, p.died) + ')'
    };
    if (p.photo_url) {
      node.shape = 'circularImage';
      node.image = p.photo_url;
      node.brokenImage = '';
      node.borderWidth = 3;
      node.color = { border: color, background: color };
    }
    nodes.push(node);
  });

  var spouseSeen = {};
  LINKS.forEach(function(link) {
    var isSpouse = link.relationship === 'spouse';
    if (isSpouse) {
      var key = [link.source, link.target].sort().join('|');
      if (spouseSeen[key]) return;
      spouseSeen[key] = true;
    }
    edges.push({
      from: link.source, to: link.target,
      color: { color: isSpouse ? '#d4917a' : '#c4bfb8', highlight: '#2c2c2c' },
      width: isSpouse ? 2 : 1.5,
      dashes: isSpouse ? [5, 5] : false,
      arrows: isSpouse ? {} : { to: { enabled: true, scaleFactor: 0.5 } },
      smooth: { type: 'continuous' },
      title: link.relationship
    });
  });

  var data = { nodes: new vis.DataSet(nodes), edges: new vis.DataSet(edges) };
  var options = {
    physics: {
      solver: 'forceAtlas2Based',
      forceAtlas2Based: { gravitationalConstant: -60, springLength: 160, springConstant: 0.04, damping: 0.5 },
      stabilization: { iterations: 200 }
    },
    interaction: { hover: true, tooltipDelay: 100 },
    edges: { smooth: { type: 'continuous' } }
  };

  relNetwork = new vis.Network(container, data, options);

  // Click: highlight connected, show detail
  var origNodeProps = {};
  data.nodes.forEach(function(n) { origNodeProps[n.id] = { size: n.size, fontSize: n.font ? n.font.size : 11 }; });
  var origEdgeColors = {};
  data.edges.forEach(function(e) { origEdgeColors[e.id] = e.color && e.color.color ? e.color.color : '#c4bfb8'; });

  relNetwork.on('click', function(params) {
    if (params.nodes.length === 0) {
      hideDetailPanel();
      data.nodes.forEach(function(n) {
        var orig = origNodeProps[n.id];
        data.nodes.update({ id: n.id, opacity: 1, size: orig.size, font: { size: orig.fontSize, color: '#2c2c2c' } });
      });
      data.edges.forEach(function(e) {
        data.edges.update({ id: e.id, color: { color: origEdgeColors[e.id], opacity: 1 } });
      });
      return;
    }
    var nid = params.nodes[0];
    showDetailPanel(nid);

    var connEdges = relNetwork.getConnectedEdges(nid);
    var connNodes = new Set([nid]);
    connEdges.forEach(function(eid) {
      var e = data.edges.get(eid);
      connNodes.add(e.from); connNodes.add(e.to);
    });
    data.nodes.forEach(function(n) {
      var orig = origNodeProps[n.id];
      if (connNodes.has(n.id)) {
        data.nodes.update({ id: n.id, opacity: 1, size: orig.size, font: { size: orig.fontSize, color: '#2c2c2c' } });
      } else {
        data.nodes.update({ id: n.id, opacity: 0.15, size: 5, font: { size: 1, color: 'transparent' } });
      }
    });
    data.edges.forEach(function(e) {
      var oc = origEdgeColors[e.id];
      if (connEdges.indexOf(e.id) >= 0) {
        data.edges.update({ id: e.id, color: { color: oc, opacity: 1 } });
      } else {
        data.edges.update({ id: e.id, color: { color: '#eee', opacity: 0.08 } });
      }
    });
  });
}

// ===== MIGRATION (Leaflet) =====
var migMap = null;
var migState = {
  selected: new Set(),
  layers: {},
  playing: false,
  speed: 1,
  minYear: 0, maxYear: 0,
  currentYear: 0,
  animFrame: null
};

function initMigration() {
  if (!HAS_MIGRATION || MIGRATION.length === 0) return;

  // Build person selector
  var listEl = document.getElementById('person-list');
  MIGRATION.forEach(function(m, idx) {
    var color = MIG_COLORS[idx % MIG_COLORS.length];
    var born = '', died = '';
    m.waypoints.forEach(function(w) {
      if (w.event === 'Born') born = w.year;
      if (w.event === 'Died') died = w.year;
    });
    var lifespan = born && died ? born + '–' + died : born ? 'b. ' + born : '';
    var btn = document.createElement('button');
    btn.className = 'person-btn';
    btn.setAttribute('data-person', m.id);
    btn.setAttribute('data-color', color);
    btn.innerHTML = '<span class="person-dot" style="border-color:' + color + '"></span>' +
      '<div class="person-info"><div class="person-name">' + escHtml(m.name) + '</div>' +
      '<div class="person-lifespan">' + lifespan + ' · ' + m.waypoints.length + ' stops</div></div>';
    btn.onclick = function() { togglePerson(m.id); };
    listEl.appendChild(btn);
  });

  // Init Leaflet
  migMap = L.map('map').setView([38, -85], 5);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors', maxZoom: 18
  }).addTo(migMap);

  // Select first person
  if (MIGRATION.length > 0) togglePerson(MIGRATION[0].id);
}

function togglePerson(personId) {
  if (migState.selected.has(personId)) {
    migState.selected.delete(personId);
    removeMigLayers(personId);
  } else {
    migState.selected.add(personId);
    addMigLayers(personId);
  }
  // Update sidebar
  document.querySelectorAll('.person-btn').forEach(function(btn) {
    var pid = btn.getAttribute('data-person');
    var isSel = migState.selected.has(pid);
    btn.classList.toggle('selected', isSel);
    btn.style.borderLeftColor = isSel ? btn.getAttribute('data-color') : 'transparent';
    var dot = btn.querySelector('.person-dot');
    dot.style.backgroundColor = isSel ? btn.getAttribute('data-color') : 'transparent';
  });
  updateYearRange();
  fitMigBounds();
}

function addMigLayers(personId) {
  var migration = MIGRATION.find(function(m) { return m.id === personId; });
  if (!migration) return;
  var idx = MIGRATION.indexOf(migration);
  var color = MIG_COLORS[idx % MIG_COLORS.length];
  var wps = migration.waypoints;
  if (wps.length === 0) return;
  var latlngs = wps.map(function(w) { return [w.lat, w.lng]; });

  var trail = L.polyline(latlngs, { color: color, weight: 3, opacity: 0.8 }).addTo(migMap);

  var markers = wps.map(function(w) {
    var mk = L.circleMarker([w.lat, w.lng], {
      radius: 7, fillColor: color, color: '#fff', weight: 2, fillOpacity: 0.9
    }).addTo(migMap);
    mk.bindPopup('<b>' + escHtml(migration.name) + '</b><br><b>' + w.year + '</b> — ' +
      escHtml(w.event) + '<br>' + escHtml(w.county + ', ' + w.state) +
      (w.details ? '<br><em>' + escHtml(w.details) + '</em>' : ''));
    return mk;
  });

  var head = L.circleMarker([wps[0].lat, wps[0].lng], {
    radius: 13, fillColor: color, color: '#fff', weight: 3, fillOpacity: 1
  }).addTo(migMap);
  var tooltip = L.tooltip({ permanent: true, direction: 'top', offset: [0, -16], className: 'head-label' });
  tooltip.setContent(migration.name);
  head.bindTooltip(tooltip);

  migState.layers[personId] = { trail: trail, markers: markers, head: head, wps: wps, color: color, name: migration.name };
}

function removeMigLayers(personId) {
  var ly = migState.layers[personId];
  if (!ly) return;
  migMap.removeLayer(ly.trail);
  ly.markers.forEach(function(m) { migMap.removeLayer(m); });
  migMap.removeLayer(ly.head);
  delete migState.layers[personId];
}

function updateYearRange() {
  var min = Infinity, max = -Infinity;
  migState.selected.forEach(function(pid) {
    var ly = migState.layers[pid];
    if (!ly) return;
    ly.wps.forEach(function(w) {
      if (w.year < min) min = w.year;
      if (w.year > max) max = w.year;
    });
  });
  if (min === Infinity) { min = 0; max = 0; }
  migState.minYear = min; migState.maxYear = max;
  migState.currentYear = max;
  var slider = document.getElementById('mig-slider');
  slider.min = min; slider.max = max; slider.value = max;
  document.getElementById('mig-year').textContent = max || '';
  updateMigDisplay();
}

function getPositionAtYear(wps, year) {
  if (wps.length === 0) return null;
  if (year <= wps[0].year) return null;
  if (year >= wps[wps.length-1].year) return [wps[wps.length-1].lat, wps[wps.length-1].lng];
  for (var i = 0; i < wps.length - 1; i++) {
    if (year >= wps[i].year && year < wps[i+1].year) {
      var t = (year - wps[i].year) / (wps[i+1].year - wps[i].year);
      return [
        wps[i].lat + t * (wps[i+1].lat - wps[i].lat),
        wps[i].lng + t * (wps[i+1].lng - wps[i].lng)
      ];
    }
  }
  return [wps[wps.length-1].lat, wps[wps.length-1].lng];
}

function updateMigDisplay() {
  var year = migState.currentYear;
  Object.keys(migState.layers).forEach(function(pid) {
    var ly = migState.layers[pid];
    var wps = ly.wps;
    var reached = wps.filter(function(w) { return w.year <= year; });

    if (reached.length > 0) {
      var trailPts = reached.map(function(w) { return [w.lat, w.lng]; });
      // Interpolate head position
      var headPos = getPositionAtYear(wps, year);
      if (headPos) trailPts.push(headPos);
      ly.trail.setLatLngs(trailPts);
      var pos = headPos || [reached[reached.length-1].lat, reached[reached.length-1].lng];
      ly.head.setLatLng(pos);
      ly.head.setStyle({ fillOpacity: 1, opacity: 1 });

      // Update tooltip with current location
      var lastReached = reached[reached.length-1];
      ly.head.setTooltipContent(ly.name + ' · ' + lastReached.county + ', ' + lastReached.state);
    } else {
      ly.trail.setLatLngs([]);
      ly.head.setStyle({ fillOpacity: 0, opacity: 0 });
    }

    // Update marker opacity
    wps.forEach(function(w, i) {
      ly.markers[i].setStyle({ fillOpacity: w.year <= year ? 0.9 : 0.15, opacity: w.year <= year ? 1 : 0.3 });
    });
  });
}

function fitMigBounds() {
  var pts = [];
  Object.keys(migState.layers).forEach(function(pid) {
    migState.layers[pid].wps.forEach(function(w) { pts.push([w.lat, w.lng]); });
  });
  if (pts.length > 1) migMap.fitBounds(L.latLngBounds(pts), { padding: [40, 40] });
  else if (pts.length === 1) migMap.setView(pts[0], 8);
}

function migScrub(year) {
  migState.currentYear = parseInt(year);
  document.getElementById('mig-year').textContent = year;
  document.getElementById('mig-slider').value = year;
  updateMigDisplay();
}

function migTogglePlay() {
  if (migState.playing) {
    migState.playing = false;
    document.getElementById('mig-play').innerHTML = '&#9654;';
    if (migState.animFrame) cancelAnimationFrame(migState.animFrame);
  } else {
    migState.playing = true;
    document.getElementById('mig-play').innerHTML = '&#10074;&#10074;';
    if (migState.currentYear >= migState.maxYear) migState.currentYear = migState.minYear;
    var lastTime = performance.now();
    function tick(now) {
      if (!migState.playing) return;
      var delta = (now - lastTime) / 1000;
      lastTime = now;
      migState.currentYear += delta * migState.speed * 3;
      if (migState.currentYear >= migState.maxYear) {
        migState.currentYear = migState.minYear;
      }
      migScrub(Math.round(migState.currentYear));
      migState.animFrame = requestAnimationFrame(tick);
    }
    migState.animFrame = requestAnimationFrame(tick);
  }
}

function migSetSpeed(s) {
  migState.speed = s;
  document.querySelectorAll('.speed-btn').forEach(function(btn) {
    btn.classList.toggle('active', parseInt(btn.getAttribute('data-speed')) === s);
  });
}

// ===== RECORDS TAB =====
var allRecords = [];
var activeRecType = 'All';

function initRecords() {
  allRecords = [];
  PEOPLE.forEach(function(p) {
    if (!p.details) return;
    p.details.forEach(function(d) {
      if (isRecord(d)) {
        var clean = stripRecordPrefix(d);
        var rtype = classifyRecord(clean);
        allRecords.push({ person: p.name, personId: p.id, type: rtype, citation: clean });
      }
    });
  });

  // Build filter buttons
  var types = {};
  allRecords.forEach(function(r) { types[r.type] = (types[r.type] || 0) + 1; });
  var filtersEl = document.getElementById('records-filters');
  filtersEl.innerHTML = '';
  var allBtn = document.createElement('button');
  allBtn.className = 'rec-filter-btn active';
  allBtn.textContent = 'All';
  allBtn.onclick = function() { activeRecType = 'All'; applyRecFilters(); highlightRecBtn(allBtn); };
  filtersEl.appendChild(allBtn);
  Object.keys(types).sort().forEach(function(t) {
    var btn = document.createElement('button');
    btn.className = 'rec-filter-btn';
    btn.textContent = t + ' (' + types[t] + ')';
    btn.setAttribute('data-type', t);
    btn.onclick = function() { activeRecType = t; applyRecFilters(); highlightRecBtn(btn); };
    filtersEl.appendChild(btn);
  });

  applyRecFilters();
}

function highlightRecBtn(active) {
  document.querySelectorAll('.rec-filter-btn').forEach(function(b) { b.classList.remove('active'); });
  active.classList.add('active');
}

function applyRecFilters() {
  var query = (document.getElementById('records-search').value || '').toLowerCase();
  var filtered = allRecords.filter(function(r) {
    if (activeRecType !== 'All' && r.type !== activeRecType) return false;
    if (query && r.person.toLowerCase().indexOf(query) < 0 && r.citation.toLowerCase().indexOf(query) < 0) return false;
    return true;
  });

  var tbody = document.getElementById('records-tbody');
  tbody.innerHTML = '';
  filtered.forEach(function(r) {
    var tr = document.createElement('tr');
    tr.innerHTML = '<td class="rec-person" onclick="switchTab(\'tree\');setTimeout(function(){showDetailPanel(\'' +
      r.personId + '\')},200)">' + escHtml(r.person) + '</td>' +
      '<td><span class="rec-type">' + r.type + '</span></td>' +
      '<td class="rec-citation">' + escHtml(r.citation) + '</td>';
    tbody.appendChild(tr);
  });

  document.getElementById('records-count').textContent = filtered.length + ' of ' + allRecords.length + ' records';
}

function filterRecords() { applyRecFilters(); }

// ===== INIT =====
document.addEventListener('DOMContentLoaded', function() {
  if (HAS_MIGRATION && MIGRATION.length > 0) {
    document.getElementById('migration-tab-btn').style.display = '';
  }
  // Show Records tab if any records exist
  var hasRecords = PEOPLE.some(function(p) { return p.details && p.details.some(isRecord); });
  if (hasRecords) document.getElementById('records-tab-btn').style.display = '';
  initFamilyTree();
  inited.tree = true;
});

// Close detail panel on Escape
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') hideDetailPanel();
});
</script>
</body></html>"""


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    root = tk.Tk()
    root.withdraw()

    messagebox.showinfo(
        'Family Archive Viewer',
        'You will be asked to select your data files:\n\n'
        '1. Points file (people) — required\n'
        '2. Links file (relationships) — required\n'
        '3. Migration file (locations) — optional\n\n'
        'Supported formats: .xlsx, .xls, .csv')

    points_path = filedialog.askopenfilename(
        title='Step 1/3: Select Points file (people data)',
        filetypes=[('Excel/CSV', '*.xlsx *.xls *.csv'), ('All files', '*.*')])
    if not points_path:
        sys.exit(0)

    links_path = filedialog.askopenfilename(
        title='Step 2/3: Select Links file (relationships)',
        filetypes=[('Excel/CSV', '*.xlsx *.xls *.csv'), ('All files', '*.*')])
    if not links_path:
        sys.exit(0)

    do_migration = messagebox.askyesno(
        'Migration Data',
        'Do you have a Migration file (location/movement data)?\n\n'
        'Click Yes to select it, or No to skip.')

    migration_path = None
    if do_migration:
        migration_path = filedialog.askopenfilename(
            title='Step 3/3: Select Migration file (location data)',
            filetypes=[('Excel/CSV', '*.xlsx *.xls *.csv'), ('All files', '*.*')])

    try:
        points_df = _read_file(points_path)
        links_df = _read_file(links_path)
        migration_df = _read_file(migration_path) if migration_path else pd.DataFrame()
    except Exception as e:
        messagebox.showerror('Error', f'Could not read data files:\n{e}')
        sys.exit(1)

    people = _parse_points(points_df)
    if not people:
        messagebox.showerror('Error',
            f'No people found in Points file.\n'
            f'Columns found: {list(points_df.columns)}\n\n'
            f'Expected: ID, Name, Gen, Born, Died')
        sys.exit(1)

    links = _parse_links(links_df)
    if not links:
        messagebox.showerror('Error',
            f'No relationships found in Links file.\n'
            f'Columns found: {list(links_df.columns)}\n\n'
            f'Expected: Source, Target, Relationship')
        sys.exit(1)

    waypoints = _parse_migration(migration_df) if not migration_df.empty else []

    base = os.path.splitext(os.path.basename(points_path))[0]
    title = base.replace('Points', '').replace('points', '').strip(' _-') or 'Family'
    output_dir = os.path.dirname(points_path)

    html_path = _build_html(people, links, waypoints, output_dir, title)
    webbrowser.open('file://' + os.path.abspath(html_path))
    root.destroy()


if __name__ == '__main__':
    main()
