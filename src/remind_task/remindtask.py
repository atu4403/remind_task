import os
import platform
import sched
import time
import datetime
import subprocess
import fire
import remind_task

# import remind_task


class Remindtask(object):
    @staticmethod
    def loop(val):
        return val

    def init(self, force: bool = False, silent: bool = False):
        """設定ファイルを作成する

        設定ファイルを作成する。既に存在するなら何もしない

        Args:
            force (bool): 設定ファイルがあっても強制再作成する
            silent (bool): ログを出力しない
        """
        try:
            if platform.system() != "Darwin":
                raise remind_task.NotMacosError("このアプリケーションはmacOS専用です")
            remind_task.create_task_file(force=force)
            if not silent:
                print(f"{remind_task.TASK_FILE_PATH}に設定ファイルを作成しました")
        except remind_task.NotMacosError as e:
            # print("このアプリケーションはmacOS専用です")
            raise e
        except remind_task.TaskFileExsistsError:
            if not silent:
                print(f"{remind_task.TASK_FILE_PATH}は既に存在します。 --force オプションで強制再作成を行います")

    def run(self, minute: int = 0):
        """通知を行う

        通知を行う。optionがない場合は1回だけ行う。

        Args:
            minute (int): 通知を繰り返す間隔を分単位で設定する
        """
        self.init(silent=True)
        remind_task.notification()
        if minute:
            s = sched.scheduler(time.time, time.sleep)
            minute = minute * 60
            while Remindtask.loop(1):
                s.enter(minute, 1, remind_task.notification)
                s.run()
                print("Notified: ", datetime.datetime.now(), os.getpid())

    def edit(self, app: str = None):
        """設定ファイルをエディタで開く

        設定ファイルを開く。optionがない場合は規定のエディタで開く。
        内部的には[open <yml_path>]と実行される。
        --app codeとした場合は[code <yml_path>]と実行される。

        Args:
            app (str): エディタを指定する。(vim code等)
        """
        self.init(silent=True)
        if not app:
            app = "open"
        subprocess.run([app, remind_task.get_task_path()])


def main():
    # fire.Fire(Remindtask())
    fire.Fire(
        {
            "init": Remindtask().init,
            "run": Remindtask().run,
            "edit": Remindtask().edit,
        }
    )


if __name__ == "__main__":
    main()