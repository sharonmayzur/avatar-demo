#!/usr/bin/env python3
"""
sync_from_confluence.py
Syncs the FE Alternatives comparison tables from Confluence → local HTML file.

FIRST-TIME SETUP:
  python3 sync_from_confluence.py --setup

MANUAL SYNC:
  python3 sync_from_confluence.py

FORCE SYNC (even if page hasn't changed):
  python3 sync_from_confluence.py --force

AUTO-SYNC (hourly cron):
  bash setup_auto_sync.sh
"""

import urllib.request
import urllib.error
import base64
import json
import re
import sys
import os
from pathlib import Path
from html.parser import HTMLParser

# ── Configuration ──────────────────────────────────────────────────────────────
CONFLUENCE_BASE = "https://kaltura.atlassian.net"
PAGE_ID = "6441009157"
HTML_FILE = Path("/Users/sharonmayzur/Documents/GitHub/avatar-demo/FE alternative/FE Alternative/fe-alternatives-comparison.html")
CONFIG_FILE = Path.home() / ".fe_sync_config.json"
VERSION_FILE = Path.home() / ".fe_sync_version.json"


# ── Credentials ────────────────────────────────────────────────────────────────
def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return None

def save_config(email, token):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"email": email, "api_token": token}, f, indent=2)
    os.chmod(CONFIG_FILE, 0o600)

def setup_credentials():
    print("\n═══ Confluence Sync — First-Time Setup ════════════════════════")
    print("You need a Confluence API token.")
    print("Get one at: https://id.atlassian.com/manage-profile/security/api-tokens\n")
    email = input("Your Atlassian email address: ").strip()
    token = input("Your API token: ").strip()
    save_config(email, token)
    print(f"\n  ✓ Credentials saved to {CONFIG_FILE}")
    return {"email": email, "api_token": token}


# ── Confluence API ─────────────────────────────────────────────────────────────
def cf_get(path, config, params=""):
    creds = base64.b64encode(
        f"{config['email']}:{config['api_token']}".encode()
    ).decode()
    url = f"{CONFLUENCE_BASE}{path}{params}"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Basic {creds}", "Accept": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def get_page_version(config):
    d = cf_get(f"/wiki/rest/api/content/{PAGE_ID}", config, "?expand=version")
    return d["version"]["number"]

def get_page_html(config):
    d = cf_get(f"/wiki/rest/api/content/{PAGE_ID}", config, "?expand=body.view")
    return d["body"]["view"]["value"]


# ── Version Tracking ───────────────────────────────────────────────────────────
def load_last_version():
    if VERSION_FILE.exists():
        with open(VERSION_FILE) as f:
            return json.load(f).get("version", 0)
    return 0

def save_version(v):
    with open(VERSION_FILE, 'w') as f:
        json.dump({"version": v}, f)


# ── HTML Table Parser ──────────────────────────────────────────────────────────
class TableParser(HTMLParser):
    """Extracts all top-level tables from HTML into list-of-rows-of-cell-strings.
    Handles rowspan and converts <br>/<p> to newlines within cells."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables = []
        self._table_depth = 0
        self._cur_table = None
        self._cur_row = None
        self._cur_col = 0
        self._cur_cell = None
        self._cur_rs = 1
        self._cur_cs = 1
        self._rowspan = {}  # {col_idx: (rows_remaining, text)}

    def handle_starttag(self, tag, attrs):
        attrs_d = dict(attrs)
        if tag == 'table':
            self._table_depth += 1
            if self._table_depth == 1:
                self._cur_table = []
                self._rowspan = {}
        elif tag == 'tr' and self._table_depth == 1:
            self._cur_row = []
            self._cur_col = 0
        elif tag in ('td', 'th') and self._table_depth == 1 and self._cur_row is not None:
            # Fill rowspan carry-overs before this cell
            while self._cur_col in self._rowspan:
                remaining, text = self._rowspan[self._cur_col]
                self._cur_row.append(text)
                remaining -= 1
                if remaining <= 0:
                    del self._rowspan[self._cur_col]
                else:
                    self._rowspan[self._cur_col] = (remaining, text)
                self._cur_col += 1
            self._cur_cell = []
            self._cur_rs = int(attrs_d.get('rowspan', 1))
            self._cur_cs = int(attrs_d.get('colspan', 1))
        elif tag == 'br' and self._cur_cell is not None:
            self._cur_cell.append('\n')
        elif tag == 'p' and self._cur_cell is not None and self._cur_cell:
            # New paragraph = new line (only if there's already content)
            if self._cur_cell[-1:] != ['\n']:
                self._cur_cell.append('\n')

    def handle_endtag(self, tag):
        if tag == 'table':
            if self._table_depth == 1 and self._cur_table is not None:
                self.tables.append(self._cur_table)
                self._cur_table = None
            self._table_depth -= 1
        elif tag == 'tr' and self._table_depth == 1 and self._cur_row is not None:
            # Fill any remaining rowspan cells at end of row
            max_col = max(self._rowspan.keys(), default=-1) + 1
            col = self._cur_col
            while col < max_col:
                if col in self._rowspan:
                    remaining, text = self._rowspan[col]
                    self._cur_row.append(text)
                    remaining -= 1
                    if remaining <= 0:
                        del self._rowspan[col]
                    else:
                        self._rowspan[col] = (remaining, text)
                col += 1
            if self._cur_table is not None:
                self._cur_table.append(self._cur_row)
            self._cur_row = None
        elif tag in ('td', 'th') and self._table_depth == 1 and self._cur_cell is not None:
            text = ''.join(self._cur_cell).strip()
            text = re.sub(r'\n{3,}', '\n\n', text)
            self._cur_row.append(text)
            if self._cur_rs > 1:
                self._rowspan[self._cur_col] = (self._cur_rs - 1, text)
            self._cur_col += self._cur_cs
            self._cur_cell = None

    def handle_data(self, data):
        if self._cur_cell is not None:
            self._cur_cell.append(data)


def parse_tables(html):
    parser = TableParser()
    parser.feed(html)
    return parser.tables

def find_table_by_headers(tables, expected_headers):
    """Find the table whose first non-empty row contains all expected header strings."""
    for table in tables:
        for row in table[:3]:  # check first 3 rows
            row_lower = [c.strip().lower() for c in row]
            if all(h.lower() in row_lower for h in expected_headers):
                return table
    return None


# ── Status Conversion ──────────────────────────────────────────────────────────
def parse_main_cell(cell):
    """Parse a vendor cell from the main table.
    Returns (status_code, comment). status_code: 'av'|'pa'|'na'|'un'"""
    cell = cell.strip()
    if not cell:
        return 'un', ''
    lines = [l.strip() for l in cell.split('\n') if l.strip()]
    first = lines[0] if lines else ''
    comment = ' '.join(lines[1:]) if len(lines) > 1 else ''

    f = first.lower()
    if first.startswith('✅') or f.startswith('available'):
        return 'av', comment
    elif first.startswith('⚠️') or f.startswith('partial'):
        return 'pa', comment
    elif first.startswith('❌') or f.startswith('not available') or f.startswith('not compliant'):
        return 'na', comment
    else:
        return 'un', ''

def parse_tv_cell(cell):
    """Parse a vendor cell from the True Vision table.
    Returns (status_string, comment) matching what tvStatus() expects in the HTML."""
    cell = cell.strip()
    if not cell:
        return '', ''
    lines = [l.strip() for l in cell.split('\n') if l.strip()]
    first = lines[0] if lines else ''
    comment = ' '.join(lines[1:]) if len(lines) > 1 else ''

    f = first.lower()
    if first.startswith('✅') or f.startswith('available') or f.startswith('compliant'):
        return 'Compliant', comment
    elif first.startswith('⚠️') or f.startswith('partial'):
        return 'Partially compliant', comment
    elif first.startswith('❌') or f.startswith('not available') or f.startswith('not compliant'):
        return 'Not compliant', comment
    elif first.startswith('🔵') or f.startswith('roadmap'):
        return 'Roadmap', comment
    elif first.startswith('🟣') or f.startswith('backend'):
        return 'Backend', comment
    elif f.startswith('n/a'):
        return 'N/A', comment
    else:
        # No recognizable status — treat entire cell as comment
        return '', first


# ── JS String Helpers ──────────────────────────────────────────────────────────
def js_esc(s):
    """Escape a string for use inside JS single quotes."""
    return (s
            .replace('\\', '\\\\')
            .replace("'", "\\'")
            .replace('\n', ' ')
            .strip())

def main_vendor_js(status, comment):
    """Generate AV()|PA()|NA()|UN() call for main table."""
    fn = {'av': 'AV', 'pa': 'PA', 'na': 'NA', 'un': 'UN'}.get(status, 'UN')
    if status == 'un' or not comment:
        return f"{fn}()"
    return f"{fn}('{js_esc(comment)}')"

def tv_vendor_js(status, comment):
    """Generate ['status','comment'] array for True Vision table."""
    return f"['{js_esc(status)}','{js_esc(comment)}']"


# ── Data Generation ────────────────────────────────────────────────────────────
MAIN_VENDORS = ['wiztivi', 'applicaster', 'magycal', 'kux', 'ksp']

def build_main_data(table):
    """Convert main comparison table rows → JavaScript data array string."""
    rows_js = []
    last_mod = ''

    for row in table:
        if not row or len(row) < 10:
            continue
        num_str = row[0].strip()
        if not num_str.isdigit():
            continue  # skip header rows

        mod = row[1].strip() or last_mod
        if mod:
            last_mod = mod
        feat   = row[2].strip()
        plat   = row[3].strip()
        # Vendor columns: Wiztivi=4, Applicaster=5, Magycal=6, KUX=7, KSP=8
        vendor_cols = row[4:9]
        prio   = row[9].strip() if len(row) > 9 else '1'

        vendors_js = {}
        for i, key in enumerate(MAIN_VENDORS):
            raw = vendor_cols[i] if i < len(vendor_cols) else ''
            st, cm = parse_main_cell(raw)
            vendors_js[key] = main_vendor_js(st, cm)

        row_str = (
            f"  {{mod:'{js_esc(mod)}',feat:'{js_esc(feat)}',"
            f"prio:'{js_esc(prio)}',plat:'{js_esc(plat)}',"
            f"wiztivi:{vendors_js['wiztivi']},"
            f"applicaster:{vendors_js['applicaster']},"
            f"magycal:{vendors_js['magycal']},"
            f"kux:{vendors_js['kux']},"
            f"ksp:{vendors_js['ksp']}}}"
        )
        rows_js.append(row_str)

    return ',\n'.join(rows_js)


def build_tv_data(table):
    """Convert True Vision table rows → JavaScript tvData array string."""
    rows_js = []
    last_mod = ''

    for row in table:
        if not row or len(row) < 9:
            continue
        num_str = row[0].strip()
        if not num_str.isdigit():
            continue  # skip header rows

        mod = row[1].strip() or last_mod
        if mod:
            last_mod = mod

        feat_raw = row[2].strip()
        # Extract requirement ID (e.g. P0-PLAT-01) from feature text
        id_match = re.match(r'^(P\d-[A-Z]+-\d+)\s*(.*)', feat_raw, re.DOTALL)
        if id_match:
            req_id   = id_match.group(1).strip()
            req_feat = id_match.group(2).strip()
        else:
            req_id   = ''
            req_feat = feat_raw

        # Vendor columns: Wiztivi=4, Applicaster=5, Magycal=6, KUX=7, KSP=8
        wiztivi_raw    = row[4] if len(row) > 4 else ''
        applicaster_raw = row[5] if len(row) > 5 else ''
        ksp_raw        = row[8] if len(row) > 8 else ''
        prio           = row[9].strip() if len(row) > 9 else 'P0'

        wiz_st, wiz_cm = parse_tv_cell(wiztivi_raw)
        app_st, app_cm = parse_tv_cell(applicaster_raw)
        ksp_st, ksp_cm = parse_tv_cell(ksp_raw)

        row_str = (
            f"  {{mod:'{js_esc(mod)}',id:'{js_esc(req_id)}',"
            f"feat:'{js_esc(req_feat)}',prio:'{js_esc(prio)}',"
            f"wiztivi:{tv_vendor_js(wiz_st, wiz_cm)},"
            f"applicaster:{tv_vendor_js(app_st, app_cm)},"
            f"ksp:{tv_vendor_js(ksp_st, ksp_cm)}}}"
        )
        rows_js.append(row_str)

    return ',\n'.join(rows_js)


# ── HTML File Update ───────────────────────────────────────────────────────────
def update_html_file(main_data_js, tv_data_js):
    html = HTML_FILE.read_text(encoding='utf-8')

    # Replace const data=[...]
    new_html = re.sub(
        r'(const data=\[)(.*?)(\];)',
        lambda m: m.group(1) + '\n' + main_data_js + '\n' + m.group(3),
        html,
        flags=re.DOTALL
    )
    if new_html == html:
        print("  ⚠ Warning: could not find 'const data=[...]' in HTML file")

    # Replace const tvData=[...]
    new_html2 = re.sub(
        r'(const tvData\s*=\s*\[)(.*?)(\];)',
        lambda m: m.group(1) + '\n' + tv_data_js + '\n' + m.group(3),
        new_html,
        flags=re.DOTALL
    )
    if new_html2 == new_html:
        print("  ⚠ Warning: could not find 'const tvData=[...]' in HTML file")

    HTML_FILE.write_text(new_html2, encoding='utf-8')


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    force = '--force' in sys.argv

    # Handle first-time setup
    config = load_config()
    if '--setup' in sys.argv or config is None:
        config = setup_credentials()
        if '--setup' in sys.argv and '--force' not in sys.argv:
            print("\nSetup complete. Run the script again to sync.")
            return

    print(f"Checking Confluence page {PAGE_ID}...")

    # Check if page has changed
    try:
        current_version = get_page_version(config)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("✗ Authentication failed. Run with --setup to update your credentials.")
        else:
            print(f"✗ Confluence API error {e.code}: {e.reason}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Could not reach Confluence: {e}")
        sys.exit(1)

    last_version = load_last_version()
    if current_version <= last_version and not force:
        print(f"  ✓ Already up to date (version {current_version}). Nothing to sync.")
        return

    action = "Force syncing" if force else f"Page updated (v{last_version} → v{current_version}). Syncing"
    print(f"  → {action}...")

    # Fetch rendered HTML
    try:
        page_html = get_page_html(config)
    except Exception as e:
        print(f"✗ Error fetching page content: {e}")
        sys.exit(1)

    # Parse tables
    all_tables = parse_tables(page_html)
    print(f"  → Found {len(all_tables)} table(s) on the page")

    # Identify main comparison table (has Wiztivi, Applicaster, KUX, KSP columns)
    main_table = find_table_by_headers(all_tables, ['wiztivi', 'applicaster', 'kux', 'ksp'])
    if main_table is None:
        print("✗ Could not find main comparison table in Confluence page.")
        sys.exit(1)

    # True Vision table is the next table after the main one
    try:
        main_idx = all_tables.index(main_table)
        tv_table = all_tables[main_idx + 1] if main_idx + 1 < len(all_tables) else None
    except ValueError:
        tv_table = None

    data_rows = sum(1 for r in main_table if r and r[0].strip().isdigit())
    print(f"  → Main table: {data_rows} feature rows")

    if tv_table:
        tv_rows = sum(1 for r in tv_table if r and r[0].strip().isdigit())
        print(f"  → True Vision table: {tv_rows} requirement rows")

    # Build JS data strings
    main_js = build_main_data(main_table)
    tv_js   = build_tv_data(tv_table) if tv_table else ''

    # Update HTML file
    update_html_file(main_js, tv_js)
    save_version(current_version)

    print(f"\n  ✓ HTML file updated successfully!")
    print(f"    {HTML_FILE}")


if __name__ == '__main__':
    main()
