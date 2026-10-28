#!/bin/bash
# Installs REA (https://github.com/morluto/rea) for Claude Code cloud sessions:
#   - Node.js 24 in /opt/node24 (REA needs >=22.23.4 / >=24.22.1; the image ships 22.22)
#   - the rea-agents CLI, pinned
#   - the reverse-engineer-anything skill into ~/.claude/skills (user scope, every repo)
#   - the rea MCP server registered at user scope
# Idempotent: safe to run on every session start.
set -euo pipefail

REA_VERSION="${REA_VERSION:-6.8.0}"
NODE_VERSION="${NODE_VERSION:-24.22.1}"
NODE_DIR=/opt/node24

if [[ ! -x "$NODE_DIR/bin/node" ]] || [[ "$("$NODE_DIR/bin/node" --version)" != "v$NODE_VERSION" ]]; then
  tarball="node-v${NODE_VERSION}-linux-x64.tar.xz"
  tmp="$(mktemp -d)"
  curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/${tarball}" -o "$tmp/$tarball"
  curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/SHASUMS256.txt" \
    | grep " ${tarball}\$" | (cd "$tmp" && sha256sum -c -)
  rm -rf "$NODE_DIR" && mkdir -p "$NODE_DIR"
  tar -xJf "$tmp/$tarball" -C "$NODE_DIR" --strip-components=1
  rm -rf "$tmp"
fi

export PATH="$NODE_DIR/bin:$PATH"

if [[ "$(rea --version 2>/dev/null || true)" != *"$REA_VERSION"* ]]; then
  npm install --global --no-fund --no-audit "rea-agents@${REA_VERSION}"
fi

skill_src="$(npm root --global)/rea-agents/skills/reverse-engineer-anything"
mkdir -p "$HOME/.claude/skills"
rm -rf "$HOME/.claude/skills/reverse-engineer-anything"
cp -r "$skill_src" "$HOME/.claude/skills/"

claude mcp remove --scope user rea >/dev/null 2>&1 || true
claude mcp add --scope user rea -- "$NODE_DIR/bin/node" "$NODE_DIR/bin/rea" mcp

echo "REA ${REA_VERSION} ready (node $(node --version))"
