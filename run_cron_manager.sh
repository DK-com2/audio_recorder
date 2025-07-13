#!/bin/bash

# cron_manager.py実行用スクリプト
# 仮想環境を有効化してからcron管理を実行

cd ~/Documents/audio_recorder
source venv/bin/activate
python cron_manager.py "$@"
