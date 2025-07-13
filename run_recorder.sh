#!/bin/bash

# cron実行用スクリプト
# 仮想環境を有効化してから録音を実行

cd ~/Documents/audio_recorder
source venv/bin/activate
python recorder.py
