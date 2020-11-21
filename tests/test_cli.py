import os
import platform
import shutil
import sched
import pytest
import subprocess
from pytest_mock import mocker, MockerFixture

from src.remind_task.remindtask import Remindtask
from src import remind_task


class TestLoop:
    def test_not_args(self, mocker):
        d = {"a": 1}
        assert Remindtask.loop(d) is d


class TestInit:
    def test_not_macos(self, mocker):
        cli = Remindtask()
        mocker.patch("platform.system", return_value="Windows")
        with pytest.raises(remind_task.NotMacosError) as excinfo:
            cli.init()
        assert excinfo.typename == "NotMacosError"
        platform.system.assert_called_once()

    def test_silent(self, mocker):
        cli = Remindtask()
        mocker.patch.object(remind_task, "create_task_file")
        mocker.patch("builtins.print")
        cli.init(silent=True)
        remind_task.create_task_file.assert_called_once()
        print.assert_not_called()

    def test_not_silent(self, mocker):
        cli = Remindtask()
        mocker.patch.object(remind_task, "create_task_file")
        mocker.patch("builtins.print")
        cli.init()
        remind_task.create_task_file.assert_called_once()
        print.assert_called_once_with("~/.config/remind_task/tasks.ymlに設定ファイルを作成しました")

    def test_TaskFileExsistsError(self, mocker):
        cli = Remindtask()
        mocker.patch("os.path.isfile", return_value=True)
        mocker.patch("builtins.print")
        cli.init()
        os.path.isfile.assert_called_once()
        print.assert_called_once_with(
            "~/.config/remind_task/tasks.ymlは既に存在します。 --force オプションで強制再作成を行います"
        )

    def test_TaskFileExsistsError_silent(self, mocker):
        cli = Remindtask()
        mocker.patch("os.path.isfile", return_value=True)
        mocker.patch("builtins.print")
        cli.init(silent=True)
        os.path.isfile.assert_called_once()
        print.assert_not_called()


class TestRun:
    def test_not_args(self, mocker):
        cli = Remindtask()
        mocker.patch.object(remind_task, "notification")
        # mocker.patch("platform.system", return_value="Windows")
        cli.run()
        # assert excinfo.typename == "NotMacosError"
        remind_task.notification.assert_called_once_with()

    def test_minute(self, mocker):
        cli = Remindtask()
        mocker.patch.object(Remindtask, "loop", side_effect=[1, 0])
        mocker.patch("sched.scheduler")
        cli.run(minute=60)
        sched.scheduler().enter.assert_called_once()
        sched.scheduler().run.assert_called_once_with()


class TestEdit:
    def test_not_args(self, mocker):
        cli = Remindtask()
        mocker.patch("subprocess.run")
        cli.edit()
        subprocess.run.assert_any_call(["open", remind_task.get_task_path()])

    def test_app_vim(self, mocker):
        cli = Remindtask()
        mocker.patch("subprocess.run")
        cli.edit(app="vim")
        subprocess.run.assert_any_call(["vim", remind_task.get_task_path()])
