# ============================================================
# Audio2Score Full Pipeline Makefile (uv-based Complete Version)
# ============================================================
# Features:
# - uv による Python / 仮想環境 / 依存関係の一括管理
# - pyproject.toml / uv.lock に基づく再現可能な環境
# - ffmpeg による音源 → WAV 変換（外部 WAV も常に正規化用に通す）
# - audio2score CLI（uv run 経由）による Demucs + BasicPitch + MuseScore 自動実行
# - build/ が存在しない状態にも完全対応
# ============================================================

SHELL := /bin/bash

# ------------------------------------------------------------
# Tools
# ------------------------------------------------------------
UV := uv

# ------------------------------------------------------------
# Input / Output
# ------------------------------------------------------------
# 入力ファイル（拡張子は何でも可：m4a, mp3, flac, wav ...）
INPUT ?= input.wav

# ベース名だけ取り出し（拡張子なし）
NAME := $(notdir $(basename $(INPUT)))

# 出力ルートディレクトリ
BUILD_DIR := build

# ffmpeg で変換後の正規化前 WAV（パイプライン入口）
RAW_WAV := $(BUILD_DIR)/$(NAME).wav

# ============================================================
# Main targets
# ============================================================
.PHONY: all
all: score

# ------------------------------------------------------------
# 1. Create / sync uv-managed environment
#    - プロジェクト単位で Python 3.10.14 を pin してから uv sync
# ------------------------------------------------------------
.PHONY: setup
setup:
	@echo ">>> Pinning Python 3.10 for this project"
	$(UV) python pin 3.10.14
	@echo ">>> Syncing uv environment (.venv / uv.lock)"
	$(UV) sync

# ------------------------------------------------------------
# 2. Convert INPUT → WAV with ffmpeg (mono / 44.1kHz)
#    - すべての入力を一度ここに通し、後段の正規化処理の入口にする
# ------------------------------------------------------------
.PHONY: ffmpeg
ffmpeg: $(RAW_WAV)

$(RAW_WAV):
	@mkdir -p $(BUILD_DIR)
	@echo "[FFMPEG] Converting $(INPUT) → $@ (mono, 44.1kHz)"
	ffmpeg -y -i "$(INPUT)" -ac 1 -ar 44100 "$@"

# ------------------------------------------------------------
# 3. Run audio2score pipeline (Demucs + BasicPitch + MuseScore)
#    - uv run 経由で src/audio2score/cli.py を実行
# ------------------------------------------------------------
.PHONY: score
score: setup ffmpeg
	@echo "=== Running audio2score pipeline via uv run ==="
	$(UV) run -- python -m audio2score.cli \
		"$(RAW_WAV)" \
		--output-dir "$(BUILD_DIR)" \
		--stems \
		--models htdemucs htdemucs_6s \
		--musescore-cmd mscore

# 将来用: ステム分離なしで実行したい場合の例（コメントアウト）
#.PHONY: score-no-stems
#score-no-stems: setup ffmpeg
#	@echo "=== Running audio2score pipeline (no stems) via uv run ==="
#	$(UV) run -- python -m audio2score.cli \
#		"$(RAW_WAV)" \
#		--output-dir "$(BUILD_DIR)" \
#		--musescore-cmd mscore \
#		--no-pdf

# ------------------------------------------------------------
# Clean up
# ------------------------------------------------------------
.PHONY: clean
clean:
	rm -rf $(BUILD_DIR)

.PHONY: clean-venv
clean-venv:
	rm -rf .venv uv.lock

.PHONY: distclean
distclean: clean clean-venv
	rm -rf src/audio2score/*.pyc __pycache__
