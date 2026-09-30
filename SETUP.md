# Claude Code に入れる手順

設計フレームワークを、Claude Code の個人設定（`~/.claude/`）に入れる。Ubuntu（bash）を前提とする。

---

## 1. 置き場所を決める

設計フレームワークのフォルダを、ずっと置いておく場所に置く。インストールすると、この場所が設定に書き込まれるので、後から動かさない。

```bash
# 例：ホームの直下に置く
unzip design-framework.zip -d ~
cd ~/design-framework
```

git で管理すると、コミットIDが「設計フレームワークの版」として案件の STATE.md に記録される。

```bash
git init && git add . && git commit -m "設計フレームワーク 初版"
```

---

## 2. インストールする

```bash
./install.sh
```

次のものが入る。

| 入る場所 | 中身 |
|---|---|
| `~/.claude/skills/<スキル名>/SKILL.md` | フェーズのスキルと共通スキル |
| `~/.claude/skills/design-loop/SKILL.md` | 設計ループの入口 |
| `~/.claude/agents/design-verifier.md` | 検証役のサブエージェント |

同じ名前のファイルがすでにあって中身が違う場合は、`.bak` を付けて退避してから上書きする。

---

## 3. 確かめる

Claude Code を起動し直して、次を確かめる。

- `/design-loop` が候補に出る
- `/agents` の一覧に `design-verifier` がある

---

## 4. 直したとき

スキルや役の中身を直したら、`./install.sh` をもう一度実行する。LOOP.md、README.md、templates/ は設計フレームワークのフォルダから直接読まれるので、再インストールは要らない。

git で管理している場合は、直したらコミットしてからインストールする（版が新しいコミットIDになる）。
