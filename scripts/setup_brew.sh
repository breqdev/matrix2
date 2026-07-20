#!/usr/bin/env zsh
brew tap oven-sh/bun
brew trust oven-sh/bun
brew install -y uv oven-sh/bun/bun cairo pillow

touch .env
grep -qxF 'DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib' .env || echo 'DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib' >> .env
uv sync
cd matter && bun install && cd ..
