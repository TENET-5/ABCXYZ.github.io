#!/usr/bin/env python3
"""
Website CI/CD Test Suite — Canadian Accountability Project
ABCXYZ.github.io

Tests: HTML structure, internal links, LIRIL classification, NATS health,
       zero external API check, source attribution, nav.js integrity.

Usage:
  python test_website.py             # core tests only
  python test_website.py --liril     # include live LIRIL NPU classify
  python test_website.py --nats      # include NATS bus check
  python test_website.py --verbose   # full output

SEED: 118400 | TICK: 118.4Hz | No external dependencies for core tests.
"""

import argparse
import os
import re
import sys
from pathlib import Path

SITE_DIR   = Path(__file__).parent
TENET5_DIR = Path("E:/S.L.A.T.E/tenet5")
VENV_PY    = TENET5_DIR / ".venv/Scripts/python.exe"
LIRIL_CLI  = TENET5_DIR / "tools/liril_ask.py"

EXPECTED_PAGES = [
    "index.html",
    "maid-accountability.html",
    "rcmp-commissioners.html",
    "records.html",
    "liril-analysis.html",
    "cicd-status.html",
    "about.html",
]

EXPECTED_ASSETS = ["styles.css", "nav.js"]

# Internal links that must resolve to existing files
INTERNAL_LINK_MAP = {
    "index.html":               ["records.html","maid-accountability.html","rcmp-commissioners.html","liril-analysis.html","cicd-status.html"],
    "records.html":             ["index.html"],
    "maid-accountability.html": ["index.html"],
    "rcmp-commissioners.html":  ["index.html"],
    "liril-analysis.html":      ["index.html"],
    "cicd-status.html":         ["index.html"],
}

# Patterns that indicate external API usage — fail if found
EXTERNAL_API_PATTERNS = [
    r'fetch\s*\(\s*["\']https?://',
    r'XMLHttpRequest.*open.*https?://',
    r'src=["\']https://(?!fonts\.)',  # external scripts (allow google fonts as common exception but we have none)
    r'href=["\']https://.*\.css',    # external CSS
    r'(googleapis|cloudflare|jsdelivr|unpkg|cdnjs)\.',
    r'import\s*\(["\']https?://',
]

REQUIRED_HTML_ELEMENTS = {
    "<!doctype html": "DOCTYPE declaration",
    'lang="en"':      "lang attribute",
    'charset="UTF-8"': "charset meta",
    "viewport":        "viewport meta",
    "<title>":         "title element",
    'rel="stylesheet"': "stylesheet link",
}

PASS  = "\033[92m PASS\033[0m"
FAIL  = "\033[91m FAIL\033[0m"
WARN  = "\033[93m WARN\033[0m"
INFO  = "\033[94m INFO\033[0m"
SKIP  = "\033[90m SKIP\033[0m"

results = {"pass": 0, "fail": 0, "warn": 0, "skip": 0}


def log(status, phase, msg, detail=""):
    tag = {"pass": PASS, "fail": FAIL, "warn": WARN, "info": INFO, "skip": SKIP}.get(status, INFO)
    if status in ("pass", "fail", "warn"):
        results[status] = results.get(status, 0) + 1
    line = f"[{phase:02d}]{tag}  {msg}"
    if detail:
        line += f"\n       {detail}"
    print(line)


def phase_html_structure(phase=1, verbose=False):
    print(f"\n── Phase {phase}: HTML Structure Validation ──")
    for page in EXPECTED_PAGES:
        path = SITE_DIR / page
        if not path.exists():
            log("fail", phase, f"{page} — FILE NOT FOUND")
            continue
        content = path.read_text(encoding="utf-8", errors="replace").lower()
        all_ok = True
        for pattern, desc in REQUIRED_HTML_ELEMENTS.items():
            if pattern.lower() not in content:
                log("fail", phase, f"{page} — missing {desc}")
                all_ok = False
        if all_ok:
            log("pass", phase, f"{page}")


def phase_assets(phase=2, verbose=False):
    print(f"\n── Phase {phase}: Shared Assets ──")
    for asset in EXPECTED_ASSETS:
        path = SITE_DIR / asset
        if path.exists():
            size = path.stat().st_size
            log("pass", phase, f"{asset} ({size:,} bytes)")
        else:
            log("fail", phase, f"{asset} — NOT FOUND")

    # Check nav.js contains LIRIL_SITE_DATA
    nav = SITE_DIR / "nav.js"
    if nav.exists():
        content = nav.read_text(encoding="utf-8", errors="replace")
        if "LIRIL_SITE_DATA" in content and "118400" in content:
            log("pass", phase, "nav.js contains LIRIL_SITE_DATA with seed=118400")
        else:
            log("fail", phase, "nav.js missing LIRIL_SITE_DATA or seed")

    # Check all pages reference both assets
    for page in EXPECTED_PAGES:
        path = SITE_DIR / page
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        if "styles.css" not in content:
            log("fail", phase, f"{page} — missing styles.css link")
        if "nav.js" not in content:
            log("warn", phase, f"{page} — missing nav.js script")


def phase_internal_links(phase=3, verbose=False):
    print(f"\n── Phase {phase}: Internal Link Integrity ──")
    broken = 0
    for page, links in INTERNAL_LINK_MAP.items():
        src = SITE_DIR / page
        if not src.exists():
            continue
        for link in links:
            target = SITE_DIR / link
            if target.exists():
                if verbose:
                    log("pass", phase, f"{page} → {link}")
            else:
                log("fail", phase, f"{page} → {link} — NOT FOUND")
                broken += 1
    if broken == 0:
        log("pass", phase, f"All internal links resolve ({sum(len(v) for v in INTERNAL_LINK_MAP.values())} checked)")


def phase_no_external_api(phase=4, verbose=False):
    print(f"\n── Phase {phase}: Zero External API Check ──")
    hits_total = 0
    for page in EXPECTED_PAGES + list(EXPECTED_ASSETS) + ["nav.js"]:
        path = SITE_DIR / page
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        for pattern in EXTERNAL_API_PATTERNS:
            hits = re.findall(pattern, content, re.IGNORECASE)
            if hits:
                log("fail", phase, f"{page} — external API pattern: {pattern}", str(hits[:3]))
                hits_total += len(hits)
    if hits_total == 0:
        log("pass", phase, "Zero external API/CDN patterns found across all files")


def phase_source_attribution(phase=5, verbose=False):
    print(f"\n── Phase {phase}: Source Attribution ──")
    # maid-accountability.html and records.html must have sources
    for page in ["maid-accountability.html", "records.html", "rcmp-commissioners.html"]:
        path = SITE_DIR / page
        if not path.exists():
            log("skip", phase, f"{page} not found")
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        has_sources = "sources" in content.lower() and (
            "health canada" in content.lower() or
            "auditor general" in content.lower() or
            "hansard" in content.lower() or
            "order-in-council" in content.lower()
        )
        if has_sources:
            log("pass", phase, f"{page} — source citations present")
        else:
            log("warn", phase, f"{page} — source citations may be missing")


def phase_records_count(phase=6, verbose=False):
    print(f"\n── Phase {phase}: Records Database Content ──")
    path = SITE_DIR / "records.html"
    if not path.exists():
        log("skip", phase, "records.html not found")
        return
    content = path.read_text(encoding="utf-8", errors="replace")
    count = content.count('class="record-card"')
    if count >= 10:
        log("pass", phase, f"{count} record-card elements found in records.html")
    elif count >= 5:
        log("warn", phase, f"Only {count} records found — consider expanding database")
    else:
        log("fail", phase, f"Only {count} records found — database too sparse")


def phase_liril_classify(phase=7, verbose=False):
    print(f"\n── Phase {phase}: LIRIL NPU Classification (live) ──")
    import subprocess
    if not VENV_PY.exists():
        log("skip", phase, f"venv not found: {VENV_PY}")
        return
    if not LIRIL_CLI.exists():
        log("skip", phase, f"liril_ask.py not found: {LIRIL_CLI}")
        return

    probes = [
        ("RCMP Commissioner accountability MAID legislation", "ETHICS"),
        ("disability rights euthanasia ethics state killing", "ETHICS"),
        ("criminal code charter rights safeguards",           "ETHICS"),
    ]
    for text, expected in probes:
        try:
            result = subprocess.run(
                [str(VENV_PY), str(LIRIL_CLI), "classify", text],
                capture_output=True, text=True, timeout=30
            )
            import json
            data = json.loads(result.stdout)
            domain = data.get("domain","?")
            conf   = data.get("confidence", 0)
            device = data.get("device","?")
            if domain == expected:
                log("pass", phase, f"'{text[:45]}...' → {domain} {conf:.0%} [{device}]")
            else:
                log("warn", phase, f"Expected {expected}, got {domain} for '{text[:40]}'")
        except Exception as e:
            log("fail", phase, f"LIRIL classify error: {e}")


def phase_nats_health(phase=8, verbose=False):
    print(f"\n── Phase {phase}: NATS Bus Health ──")
    try:
        import socket
        s = socket.create_connection(("127.0.0.1", 4223), timeout=5)
        s.close()
        log("pass", phase, "NATS TCP 127.0.0.1:4223 reachable")
    except Exception as e:
        log("fail", phase, f"NATS unreachable: {e}")
        return

    try:
        import urllib.request, json
        data = urllib.request.urlopen("http://127.0.0.1:18222/varz", timeout=5).read()
        v = json.loads(data)
        conns = v.get("connections", 0)
        subs  = v.get("subscriptions", 0)
        ver   = v.get("version","?")
        log("pass", phase, f"NATS v{ver} | connections={conns} | subscriptions={subs}")
        if conns < 5:
            log("warn", phase, f"Low NATS connections ({conns}) — app agents may be offline")
    except Exception as e:
        log("warn", phase, f"NATS monitor unavailable: {e}")


def main():
    parser = argparse.ArgumentParser(description="Canadian Accountability Project — Website CI/CD Tests")
    parser.add_argument("--liril",   action="store_true", help="Run live LIRIL NPU classification test")
    parser.add_argument("--nats",    action="store_true", help="Run NATS bus health test")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    print("═" * 64)
    print("  CANADIAN ACCOUNTABILITY PROJECT — Website CI/CD Test Suite")
    print(f"  Site dir: {SITE_DIR}")
    print(f"  LIRIL seed: 118400 | TICK: 118.4Hz | SATOR·OPERA·row3")
    print("═" * 64)

    phase_html_structure(1, args.verbose)
    phase_assets(2, args.verbose)
    phase_internal_links(3, args.verbose)
    phase_no_external_api(4, args.verbose)
    phase_source_attribution(5, args.verbose)
    phase_records_count(6, args.verbose)

    if args.liril:
        phase_liril_classify(7, args.verbose)
    else:
        print(f"\n── Phase 7: LIRIL NPU Classification (skipped — use --liril) ──")
        results["skip"] += 1

    if args.nats:
        phase_nats_health(8, args.verbose)
    else:
        print(f"\n── Phase 8: NATS Bus Health (skipped — use --nats) ──")
        results["skip"] += 1

    print("\n" + "═" * 64)
    total = results["pass"] + results["fail"] + results["warn"]
    print(f"  RESULTS: {results['pass']} PASS  |  {results['warn']} WARN  |  {results['fail']} FAIL  |  {results['skip']} SKIP")
    if results["fail"] == 0:
        print("  STATUS:  \033[92m✓ GREEN — pipeline clean\033[0m")
    else:
        print("  STATUS:  \033[91m✗ RED — fix failures before deploy\033[0m")
    print("═" * 64)

    sys.exit(1 if results["fail"] > 0 else 0)


if __name__ == "__main__":
    main()
