# ============================================================
# Audio2Score Full Pipeline Makefile (Complete Version)
# ============================================================
# Features:
# - pyenv Python 3.10 自動検出
# - .venv 自動生成
# - README.org → src/*** 自動 'tangle
# - パッケージ自動インストール (pip install .)
# - ffmpeg による音源 → WAV 変換（外部 WAV も常に正規化用に通す）
# - audio2score CLI による Demucs+BasicPitch 自動実行
# - build/ が存在しない状態にも完全対応
# ============================================================

SHELL := /bin/bash
VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
FIND_PYENV := $(shell command -v pyenv >/dev/null 2>&1 && echo yes || echo no)

# ------------------------------------------------------------
# Python binary auto-select (pyenv 3.10.x → fallback python3)
# ------------------------------------------------------------
ifeq ($(FIND_PYENV),yes)
	# 最新の Python 3.10.x を pyenv から取得
	PYENV_VER := $(shell pyenv versions --bare | grep '^3\.10' | sort -V | tail -1)
	ifneq ($(PYENV_VER),)
		PYTHON_BIN := $(HOME)/.pyenv/versions/$(PYENV_VER)/bin/python3
	else
		PYTHON_BIN := python3
	endif
else
	PYTHON_BIN := python3
endif

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
# 1. create virtualenv + install package
# ------------------------------------------------------------
$(VENV):
	@echo ">>> Creating virtualenv: $(VENV)"
	$(PYTHON_BIN) -m venv $(VENV)
	$(PIP) install --upgrade pip wheel setuptools

.PHONY: setup
setup: $(VENV)
	@echo ">>> Installing audio2score package"
	$(PIP) install .


# ------------------------------------------------------------
# 2. Convert INPUT → WAV with ffmpeg  (always run for normalization)
# ------------------------------------------------------------
$(RAW_WAV):
	@mkdir -p $(BUILD_DIR)
	@echo "[FFMPEG] Converting $(INPUT) → $@"
	ffmpeg -y -i "$(INPUT)" -ac 1 -ar 44100 "$@"

.PHONY: ffmpeg
ffmpeg: $(RAW_WAV)


# ------------------------------------------------------------
# 3. Run audio2score pipeline (Demucs + BasicPitch + MuseScore)
# ------------------------------------------------------------
.PHONY: score
score: setup ffmpeg
	@echo "=== Running audio2score pipeline ==="
	$(PY) -m audio2score.cli \
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
	rm -rf $(VENV)

.PHONY: distclean
distclean: clean clean-venv
	rm -rf src/audio2score/*.pyc __pycache__
