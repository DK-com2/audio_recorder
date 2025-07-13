# cron_manager.py
import os
import subprocess
import logging
from config import Config

logging.basicConfig(level=logging.INFO)

class CronManager:
    def __init__(self):
        self.config = Config()
    
    def add_cron_job(self, schedule="0 */1 * * *"):
        """
        cronジョブを追加
        デフォルト: 毎時0分に実行
        schedule例:
        - "0 */1 * * *"  # 毎時0分
        - "0 9 * * *"    # 毎日9時
        - "0 9 * * 1-5"  # 平日9時
        """
        try:
            # 現在のcrontabを取得
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            current_cron = result.stdout if result.returncode == 0 else ""
            
            # 新しいジョブ行
            new_job = f"{schedule} {self.config.CRON_COMMAND} >> S:\\Documents\\audio_recorder\\recorder_cron.log 2>&1"
            
            # 既存のジョブをチェック
            if self.config.CRON_COMMAND in current_cron:
                logging.info("cronジョブは既に存在します")
                return False
            
            # 新しいcrontabを作成
            new_cron = current_cron + new_job + "\n"
            
            # crontabに書き込み
            process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
            process.communicate(input=new_cron)
            
            if process.returncode == 0:
                logging.info(f"cronジョブを追加しました: {new_job}")
                return True
            else:
                logging.error("cronジョブの追加に失敗しました")
                return False
                
        except Exception as e:
            logging.error(f"cronジョブ追加エラー: {e}")
            return False
    
    def remove_cron_job(self):
        """録音用のcronジョブを削除"""
        try:
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            if result.returncode != 0:
                logging.info("crontabが存在しません")
                return True
            
            current_cron = result.stdout
            
            # 該当するジョブを除外
            lines = current_cron.split('\n')
            new_lines = [line for line in lines if self.config.CRON_COMMAND not in line]
            new_cron = '\n'.join(new_lines)
            
            # crontabを更新
            process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
            process.communicate(input=new_cron)
            
            if process.returncode == 0:
                logging.info("cronジョブを削除しました")
                return True
            else:
                logging.error("cronジョブの削除に失敗しました")
                return False
                
        except Exception as e:
            logging.error(f"cronジョブ削除エラー: {e}")
            return False
    
    def list_cron_jobs(self):
        """現在のcronジョブを表示"""
        try:
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            if result.returncode == 0:
                print("現在のcronジョブ:")
                print(result.stdout)
            else:
                print("crontabが存在しないか、エラーが発生しました")
        except Exception as e:
            logging.error(f"crontabリストエラー: {e}")

def main():
    """コマンドライン実行用"""
    import sys
    
    cron_manager = CronManager()
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python cron_manager.py add [schedule]    # cronジョブを追加")
        print("  python cron_manager.py remove            # cronジョブを削除")
        print("  python cron_manager.py list              # cronジョブを表示")
        print("")
        print("スケジュール例:")
        print("  '0 */1 * * *'   # 毎時0分")
        print("  '0 9 * * *'     # 毎日9時")
        print("  '0 9 * * 1-5'   # 平日9時")
        return
    
    command = sys.argv[1]
    
    if command == "add":
        schedule = sys.argv[2] if len(sys.argv) > 2 else "0 */1 * * *"
        cron_manager.add_cron_job(schedule)
    elif command == "remove":
        cron_manager.remove_cron_job()
    elif command == "list":
        cron_manager.list_cron_jobs()
    else:
        print(f"不明なコマンド: {command}")

if __name__ == "__main__":
    main()
