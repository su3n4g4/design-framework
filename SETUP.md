# Claude Code に入れる手順

設計フレームワークを、Claude Code の個人設定（`~/.claude/`）に入れる。

---

## 0. 用意するもの

- Claude Code（インストール済みで、ログインできること）
- git

---

## 1. 取得する

設計フレームワークのフォルダを、ずっと置いておく場所に clone する。インストールすると、この場所が設定に書き込まれるので、後から動かさない。

```bash
git clone {リポジトリurl}
cd ~/design-framework
```

### 設計フレームワークの版について

設計フレームワークのルールは更新されることがある。どのルールで設計したかを後から追えるように、「版」で区別する。

- 版は、インストールしたときの設計フレームワークのコミットID（例：`1e9cdbe`）。
- 案件で各フェーズを始めると、そのときの版が案件の `design/STATE.md` に自動で書き込まれる。
- 設計フレームワークを更新（`git pull`）したら、`./install.sh` をもう一度実行する。実行し直すまで版は変わらない。

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

`~/.claude/` 以外に入れたい場合は、`CLAUDE_DIR` で場所を指定する。

```bash
CLAUDE_DIR=/path/to/.claude ./install.sh
```

---

## 3. 確かめる

Claude Code を起動し直して、次を確かめる。

- `/design-loop` が候補に出る
- `/agents` の一覧に `design-verifier` がある

---

## 4. 新しい版に更新する

設計フレームワークが更新されたら、次の順に行う。

1. 動いている `/design-loop` がないことを確かめる。フェーズの途中で更新すると、1つのフェーズの中で版が混ざる
2. 最新を取得する

   ```bash
   cd ~/design-framework
   git pull
   ```

3. もう一度インストールする

   ```bash
   ./install.sh
   ```

4. Claude Code を起動し直す
5. 版が入れ替わったことを確かめる。次の2つが同じコミットIDになっていればよい

   ```bash
   git rev-parse --short HEAD
   grep 設計フレームワークの版 ~/.claude/skills/design-loop/SKILL.md
   ```

`git pull` だけで止めない。LOOP.md、README.md、templates/ は設計フレームワークのフォルダから直接読まれるので `git pull` で反映されるが、スキルや役（skills/、roles/、entry/）と STATE.md に記録される版は `./install.sh` を実行するまで古いままになり、記録と実際に使われるスキルが食い違う。

### 案件の途中で更新した場合

- 更新した後に始めたフェーズには、新しい版が記録される。前のフェーズと版が違うと、実装者が始める前に知らせてくる
- すでに完了したフェーズの成果物は、自動では作り直されない。新しい版で作り直したい場合は、そのフェーズを差し戻す（LOOP.md の「差し戻し」）
- この更新より前に作った案件の STATE.md には、フェーズ一覧に「版」の列がない。その案件で使い続ける場合は、`templates/STATE.md` にならって列を足す

---

## 5. 中身を直したいとき

手元のフォルダを直接書き換えない。書き換えると、STATE.md に記録される版（コミットID）と実際の中身が食い違い、他の人と同じ版で設計していることを確かめられなくなる。

直したい点があれば、ブランチを作ってプルリクエストを出す。取り込まれたら、4 の手順で更新する。

---

## 困ったとき

| 症状 | 確かめること |
|---|---|
| `./install.sh` で `Permission denied` が出る | `chmod +x install.sh` を実行してからやり直す |
| `/design-loop` が候補に出ない | Claude Code を起動し直したか。`~/.claude/skills/design-loop/SKILL.md` があるか |
| フォルダを動かしてしまった | 動かした先で `./install.sh` をもう一度実行する |
