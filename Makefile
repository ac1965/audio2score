# ============================================================
# Audio2Score Full Pipeline Makefile (uv-based, Python 3.11)
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

# ffmpeg で変換後の WAV（パイプライン入口）
RAW_WAV := $(BUILD_DIR)/$(NAME).wav

# ============================================================
# Main targets
# ============================================================
.PHONY: all
all: score

# ------------------------------------------------------------
# 1. Create / sync uv-managed environment
#    - プロジェクト単位で Python 3.11 を pin してから uv sync
# ------------------------------------------------------------
.PHONY: setup
setup:
	@echo ">>> Pinning Python 3.11 for this project"
	$(UV) python pin 3.11
	@echo ">>> Syncing uv environment (.venv / uv.lock)"
	$(UV) sync

# ------------------------------------------------------------
# 2. Convert INPUT → WAV with ffmpeg (mono / 44.1kHz)
# ------------------------------------------------------------
.PHONY: ffmpeg
ffmpeg: $(RAW_WAV)

$(RAW_WAV):
	@mkdir -p $(BUILD_DIR)
	@echo "[FFMPEG] Converting $(INPUT) → $@ (mono, 44.1kHz)"
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
