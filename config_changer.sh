#!/bin/bash

# 録音設定変更スクリプト
# 録音時間と地点名を変更できます

CONFIG_FILE="config.py"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 現在の設定を表示
show_current_settings() {
    echo "=== 現在の録音設定 ==="
    
    # 録音時間を取得
    CURRENT_SECONDS=$(grep "RECORD_SECONDS = " $CONFIG_FILE | sed 's/.*= \([0-9]*\).*/\1/')
    CURRENT_MINUTES=$((CURRENT_SECONDS / 60))
    CURRENT_HOURS=$((CURRENT_MINUTES / 60))
    
    # 地点名を取得
    CURRENT_LOCATION=$(grep "LOCATION_NAME = " $CONFIG_FILE | sed "s/.*= '\([^']*\)'.*/\1/")
    
    # デバイス設定を取得
    CURRENT_DEVICE_INDEX=$(grep "DEVICE_INDEX = " $CONFIG_FILE | sed 's/.*= \([0-9]*\).*/\1/')
    CURRENT_DEVICE_NAME=$(grep "MICROPHONE_NAME = " $CONFIG_FILE | sed "s/.*= '\([^']*\)'.*/\1/")
    
    echo "録音時間: ${CURRENT_HOURS}時間${CURRENT_MINUTES}分 (${CURRENT_SECONDS}秒)"
    echo "地点名: ${CURRENT_LOCATION}"
    echo "音声デバイス: Index ${CURRENT_DEVICE_INDEX} (${CURRENT_DEVICE_NAME})"
    echo ""
}

# 録音時間を変更
change_record_time() {
    echo "録音時間の設定:"
    echo "1) 30分 (1800秒)"
    echo "2) 1時間 (3600秒) [デフォルト]"
    echo "3) 2時間 (7200秒)"
    echo "4) カスタム (分単位で入力)"
    echo ""
    read -p "選択してください (1-4): " choice
    
    case $choice in
        1)
            NEW_SECONDS=1800
            echo "30分に設定しました"
            ;;
        2)
            NEW_SECONDS=3600
            echo "1時間に設定しました"
            ;;
        3)
            NEW_SECONDS=7200
            echo "2時間に設定しました"
            ;;
        4)
            read -p "録音時間を分単位で入力してください: " minutes
            if [[ $minutes =~ ^[0-9]+$ ]] && [ $minutes -gt 0 ]; then
                NEW_SECONDS=$((minutes * 60))
                echo "${minutes}分 (${NEW_SECONDS}秒) に設定しました"
            else
                echo "エラー: 有効な数値を入力してください"
                return 1
            fi
            ;;
        *)
            echo "無効な選択です"
            return 1
            ;;
    esac
    
    # config.pyを更新
    sed -i "s/RECORD_SECONDS = [0-9]*/RECORD_SECONDS = $NEW_SECONDS/" $CONFIG_FILE
    echo "設定を保存しました"
}

# 音声デバイスを変更
change_audio_device() {
    echo "音声デバイスの設定:"
    echo "利用可能なデバイス:"
    
    # PyAudioデバイス一覧を表示
    source venv/bin/activate 2>/dev/null
    python3 -c "
import pyaudio
try:
    p = pyaudio.PyAudio()
    input_devices = []
    for i in range(p.get_device_count()):
        try:
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                input_devices.append((i, info))
                print(f'{len(input_devices)}. Index {i}: {info[\"name\"]}')
        except: pass
    p.terminate()
except Exception as e:
    print(f'エラー: {e}')
" 2>/dev/null
    
    echo ""
    read -p "使用するデバイスの番号を選択してください (1-3): " device_choice
    
    case $device_choice in
        1)
            NEW_INDEX=1
            NEW_NAME="USB Condenser Microphone"
            ;;
        2)
            NEW_INDEX=2
            NEW_NAME="pulse"
            ;;
        3)
            NEW_INDEX=3
            NEW_NAME="default"
            ;;
        *)
            echo "無効な選択です"
            return 1
            ;;
    esac
    
    # config.pyを更新
    sed -i "s/DEVICE_INDEX = [0-9]*/DEVICE_INDEX = $NEW_INDEX/" $CONFIG_FILE
    sed -i "s/MICROPHONE_NAME = '[^']*'/MICROPHONE_NAME = '$NEW_NAME'/" $CONFIG_FILE
    echo "デバイスをIndex $NEW_INDEX ($NEW_NAME)に設定しました"
}
change_location() {
    echo "地点名の設定:"
    echo "現在の地点名: $(grep "LOCATION_NAME = " $CONFIG_FILE | sed "s/.*= '\([^']*\)'.*/\1/")"
    echo ""
    echo "よく使用される地点名の例:"
    echo "- HOME (自宅)"
    echo "- OFFICE (オフィス)"
    echo "- STUDIO (スタジオ)"
    echo "- ROOM1, ROOM2 (部屋番号)"
    echo "- OUTDOOR (屋外)"
    echo ""
    read -p "新しい地点名を入力してください (英数字とアンダースコアのみ): " new_location
    
    # 入力値検証
    if [[ $new_location =~ ^[A-Za-z0-9_]+$ ]]; then
        # config.pyを更新
        sed -i "s/LOCATION_NAME = '[^']*'/LOCATION_NAME = '$new_location'/" $CONFIG_FILE
        echo "地点名を「$new_location」に設定しました"
    else
        echo "エラー: 地点名は英数字とアンダースコア(_)のみ使用できます"
        return 1
    fi
}

# メイン処理
main() {
    echo "=== 録音設定変更ツール ==="
    echo ""
    
    show_current_settings
    
    echo "変更したい項目を選択してください:"
    echo "1) 録音時間を変更"
    echo "2) 地点名を変更"
    echo "3) 音声デバイスを変更"
    echo "4) すべてを変更"
    echo "5) 設定を表示のみ"
    echo "6) 終了"
    echo ""
    read -p "選択してください (1-6): " main_choice
    
    case $main_choice in
        1)
            change_record_time
            ;;
        2)
            change_location
            ;;
        3)
            change_audio_device
            ;;
        4)
            change_record_time
            echo ""
            change_location
            echo ""
            change_audio_device
            ;;
        5)
            echo "設定表示完了"
            ;;
        6)
            echo "終了します"
            exit 0
            ;;
        *)
            echo "無効な選択です"
            exit 1
            ;;
    esac
    
    echo ""
    echo "=== 更新後の設定 ==="
    show_current_settings
    
    echo "生成されるファイル名の例:"
    # Pythonで実際のファイル名を生成して表示
    python3 -c "
import sys
sys.path.append('.')
from config import Config
print('ファイル名:', Config.get_filename().split('/')[-1])
"
}

# スクリプト実行
main
