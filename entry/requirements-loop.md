---
name: requirements-loop
description: 設計フレームワークの要件定義ループ（フェーズ 0）を進める入口。「要件定義を進めて」「次の論点を聞いて」のように、案件の要件を1論点ずつ確定させるときに使う。
---

# 要件定義ループ（作る役として動く）

- 設計フレームワークの場所：{{FRAMEWORK_DIR}}
- 設計フレームワークの版：{{VERSION}}

以下のファイル名は、設計フレームワークの場所からの相対パス。

---

## 最初にやること

1. `LOOP.md` の「0. 要件定義」と、スキル `requirements-definition` を読む。以降はこの2つに従う
2. 案件フォルダは、いまの作業ディレクトリとする
3. 案件フォルダに `requirements/` がなければ作り、`requirements/STATE.md`・`requirements/decision_register.csv`・`requirements/open_issues.md`・`requirements/reviews/` を用意する。要件定義書は案件フォルダ直下の `requirements.md`
4. `requirements/STATE.md` の「次の論点」から再開する

---

## 機械検証

記録のたびに次を実行する。BLOCKER／MAJOR が出たら直して再実行する。

```bash
python3 {{FRAMEWORK_DIR}}/scripts/check-requirements.py <案件フォルダ>
```

---

## 意味検証

記録のあと、`design-verifier` サブエージェントを起動して意味検証を任せる。起動するときは次だけを伝える（作る役の考えは伝えない）。

- フェーズ：0 要件定義（スキル requirements-definition の品質評価基準 RQ を使う）
- 案件フォルダの絶対パス
- 今回記録した論点の番号と、保存先 `requirements/reviews/<日付>_<論点番号>.md`

---

## 人に任せること

- 論点への回答（承認ポイント）。AIは選択肢と提案までを用意し、決めない
- 優先順の変更、既存の決定の変更、選択肢の作り直しの確定
