#!/bin/bash

# cron実行用スクリプト
# 仮想環境を有効化してから録音を実行

cd "$(dirname "${BASH_SOURCE[0]}")"

# ALSAエラーメッセージを抑制する環境変数
export ALSA_PCM_CARD=3
export ALSA_PCM_DEVICE=0

# 仮想環境を有効化
source venv/bin/activate

# 録音実行（ALSAエラーを抑制）
python recorder.py 2>/dev/null
