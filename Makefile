# ============================================================
# Audio2Score Full Pipeline Makefile (uv-based Complete Version)
# ============================================================
# Features:
# - uv による Python / 仮想環境 / 依存関係の一括管理
# - README.org → src/*** 自動 tangle（Org Babel 側で実行）
# - pyproject.toml / uv.lock に基づく再現可能な環境
# - ffmpeg による音源 → WAV 変換（外部 WAV も常に正規化用に通す）
# - audio2score CLI（uv run 経由）による Demucs+BasicPitch 自動実行
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
INPUT ?= input.wav
NAME := $(notdir $(basename $(INPUT)))
BUILD_DIR := build

RAW_WAV := $(BUILD_DIR)/$(NAME).wav

# ============================================================
# Main targets
# ============================================================
.PHONY: all
all: score

# ------------------------------------------------------------
# 1. Create / sync uv-managed environment
# ------------------------------------------------------------
.PHONY: setup
setup:
	@echo ">>> Syncing uv environment (.venv / uv.lock)"
	$(UV) sync

# ------------------------------------------------------------
# 2. Convert INPUT → WAV with ffmpeg  (always run for normalization)
# ------------------------------------------------------------
.PHONY: ffmpeg
ffmpeg: $(RAW_WAV)

$(RAW_WAV):
	@mkdir -p $(BUILD_DIR)
	@echo "[FFMPEG] Converting $(INPUT) → $@"
	ffmpeg -y -i "$(INPUT)" -ac 1 -ar 44100 "$@"

# ------------------------------------------------------------
# 3. Run audio2score pipeline (Demucs + BasicPitch + MuseScore)
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
