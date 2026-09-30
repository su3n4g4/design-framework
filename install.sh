#!/usr/bin/env bash
# 設計フレームワークを Claude Code の個人設定（~/.claude/）に入れる。
# スキルや役の中身を直したら、もう一度このスクリプトを実行する。
set -euo pipefail

FW="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="${CLAUDE_DIR:-$HOME/.claude}"

if git -C "$FW" rev-parse --short HEAD >/dev/null 2>&1; then
  VERSION="$(git -C "$FW" rev-parse --short HEAD)"
else
  VERSION="$(date +%Y-%m-%d)"
fi

mkdir -p "$CLAUDE_DIR/skills" "$CLAUDE_DIR/agents"

# 既存のファイルと中身が違う場合は .bak に退避してから上書きする
place() {
  local src_content="$1" dest="$2"
  mkdir -p "$(dirname "$dest")"
  if [ -f "$dest" ] && ! printf '%s' "$src_content" | cmp -s - "$dest"; then
    cp "$dest" "$dest.bak"
    echo "  既存のファイルを退避しました: $dest.bak"
  fi
  printf '%s' "$src_content" > "$dest"
}

fill() {
  sed -e "s|{{FRAMEWORK_DIR}}|$FW|g" -e "s|{{VERSION}}|$VERSION|g" "$1"
}

echo "設計フレームワーク: $FW"
echo "版: $VERSION"
echo "インストール先: $CLAUDE_DIR"
echo

echo "スキル:"
for f in "$FW"/skills/phase/*.md "$FW"/skills/common/*.md; do
  name="$(basename "$f" .md)"
  place "$(cat "$f")" "$CLAUDE_DIR/skills/$name/SKILL.md"
  echo "  $name"
done

place "$(fill "$FW/entry/design-loop.md")" "$CLAUDE_DIR/skills/design-loop/SKILL.md"
echo "  design-loop（入口）"

echo
echo "サブエージェント:"
place "$(fill "$FW/roles/verifier.md")" "$CLAUDE_DIR/agents/design-verifier.md"
echo "  design-verifier"

echo
echo "完了しました。Claude Code を起動し直してください。"
