#!/usr/bin/env python3
"""要件定義ループの機械検証（RQ-04, RQ-05, RQ-06, RQ-07）。

使い方: python3 check-requirements.py <案件フォルダ>
（案件フォルダ直下の requirements.md と requirements/ を読む）
終了コード: BLOCKER/MAJOR があれば 1、なければ 0
"""
import csv
import glob
import re
import sys
from pathlib import Path

STATE_WORDS = ("確定", "確定（詳細未定）", "基本方針確定", "候補", "未決定", "保留")
INDIVIDUAL_ID_FROM = 88  # 個別D番号を使い始めた番号

findings = []


def add(rid, sev, msg):
    findings.append((sev, rid, msg))


def latest_spec(root):
    def ver(p):
        m = re.search(r"_v(\d+)\.(\d+)\.md$", p.name)
        return (int(m.group(1)), int(m.group(2))) if m else (-1, -1)
    specs = sorted((Path(p) for p in glob.glob(str(root / "requirements_spec_v*.md"))), key=ver)
    return specs[-1] if specs else None


def d_numbers(cell):
    nums = [int(n) for n in re.findall(r"D-(\d+)", cell)]
    if len(nums) == 2 and ("–" in cell or "-D" in cell):
        return list(range(nums[0], nums[1] + 1))
    return nums


def state_ok(s):
    s = s.strip()
    s = re.sub(r"^Phase\s*\d+", "", s)  # "Phase 1範囲確定" など
    s = re.split(r"[／（(]", s)[0] if not s.startswith("確定（詳細未定）") else s
    return any(s.startswith(w) for w in STATE_WORDS) or s.endswith("確定")


def qnums(text):
    return set(re.findall(r"Q(\d+)", text))


def main(root):
    root = Path(root)
    # 案件リポジトリの形：直下に requirements.md、管理ファイルは requirements/ に置く。
    # 旧い形（requirements_spec_vX.Y.md と管理ファイルが同じ場所）にも対応する。
    reqdir = root / "requirements" if (root / "requirements").is_dir() else root
    spec = root / "requirements.md" if (root / "requirements.md").exists() else latest_spec(root)
    reg = reqdir / "decision_register.csv"
    issues = reqdir / "open_issues.md"
    state = reqdir / "STATE.md"
    for p in (spec, reg, issues, state):
        if p is None or not Path(p).exists():
            add("RQ-07", "MAJOR", f"ファイルがない: {p}")
    if findings:
        return report()

    rows = list(csv.DictReader(open(reg, encoding="utf-8-sig")))
    spec_text = spec.read_text(encoding="utf-8")
    issues_text = issues.read_text(encoding="utf-8")
    state_text = state.read_text(encoding="utf-8")

    # RQ-04 D番号の連番
    seen = []
    for r in rows:
        seen.extend(d_numbers(r["決定ID範囲"]))
    for a, b in zip(seen, seen[1:]):
        if b != a + 1:
            add("RQ-04", "MAJOR", f"D-{a} の次が D-{b}（重複または欠番）")

    # RQ-05 個別IDの参照
    for n in seen:
        if n >= INDIVIDUAL_ID_FROM and f"D-{n}" not in spec_text:
            add("RQ-05", "MAJOR", f"D-{n} が {spec.name} から参照されていない")

    # RQ-06 状態の語（台帳と要件定義書の表）
    for r in rows:
        if not state_ok(r["状態"]):
            add("RQ-06", "MINOR", f"台帳 {r['決定ID範囲']} の状態「{r['状態']}」")
    for line in spec_text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("| R-") or line.startswith("| AC-"):
            if len(cells) >= 3 and not state_ok(cells[2]):
                add("RQ-06", "MINOR", f"{cells[0]} の状態「{cells[2]}」")

    # RQ-07 最終回答と次の質問の一致
    last_q = rows[-1]["質問"].strip()
    m = re.search(r"最終回答済み:\s*(Q\d+)", spec_text)
    if not m or m.group(1) != last_q:
        add("RQ-07", "MAJOR", f"要件定義書の最終回答（{m.group(1) if m else 'なし'}）と台帳の最後（{last_q}）が違う")
    if last_q not in state_text:
        add("RQ-07", "MAJOR", f"STATE.md に最終回答 {last_q} がない")

    nxt = {}
    m = re.search(r"次の質問:\s*(.+)", spec_text)
    nxt["要件定義書の見出し"] = re.findall(r"Q(\d+)", m.group(1)) if m else []
    m = re.search(r"再開ポイント[:：](.+)", spec_text)
    nxt["要件定義書の再開ポイント"] = re.findall(r"Q(\d+)", m.group(1)) if m else []
    m = re.search(r"^\|[^|]*\|([^|]*)\|\s*次の質問\s*\|", issues_text, re.M)
    nxt["未決定事項"] = re.findall(r"Q(\d+)", m.group(1)) if m else []
    m = re.search(r"次の論点[:：](.+)", state_text)
    nxt["STATE.md"] = re.findall(r"Q(\d+)", m.group(1)) if m else []
    firsts = {k: v[0] if v else None for k, v in nxt.items()}  # 先頭のQ番号（参照用のQは無視）
    if len(set(firsts.values())) != 1:  # すべて「なし」（完了）も一致とみなす
        add("RQ-07", "MAJOR", "次の質問が一致しない: " + ", ".join(f"{k}=Q{v}" for k, v in firsts.items()))

    answered = {r["質問"].strip() for r in rows}
    for line in issues_text.splitlines():
        m = re.match(r"^\|\s*(高|中|低)\s*\|\s*Q(\d+)\s", line)  # 論点名の先頭がQ番号の行だけ
        if m and f"Q{m.group(2)}" in answered:
            add("RQ-07", "MAJOR", f"回答済みの Q{m.group(2)} が未決定事項に残っている")
    return report()


def report():
    order = {"BLOCKER": 0, "MAJOR": 1, "MINOR": 2}
    if not findings:
        print("OK: 指摘なし")
    for sev, rid, msg in sorted(findings, key=lambda f: order[f[0]]):
        print(f"[{sev}] {rid}: {msg}")
    return 1 if any(f[0] in ("BLOCKER", "MAJOR") for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
