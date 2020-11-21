import os
import platform
import pytest
from pytest_mock import mocker
import pathlib
import shutil
import yaml

import src.remind_task as rt


# @pytest.mark.dev
class TestSoundfile:
    def test_none(self):
        default_path = "/System/Library/Sounds/Purr.aiff"
        assert rt.get_soundfile(None) == default_path

    def test_filename(self):
        default_path = "/System/Library/Sounds/Purr.aiff"
        # 引数が無いならデフォルトのパスを返す
        assert rt.get_soundfile("Blow.aiff") == "/System/Library/Sounds/Blow.aiff"
        # 引数が相対Pathなら規定のディレクトリとjoinして返す
        assert rt.get_soundfile("Blow.aiff") == "/System/Library/Sounds/Blow.aiff"
        # joinして存在チェックを行い、存在しないファイルはデフォルト値を返す
        assert rt.get_soundfile("Blow") == default_path
        # 引数が絶対パスならそのまま返す
        assert rt.get_soundfile("/bin/cat") == "/bin/cat"
        # 引数が絶対パスでも存在しないならデフォルト値を返す
        assert rt.get_soundfile("/bin/doc") == default_path


class TestReadTasks:
    def test_not_found(self):
        with pytest.raises(rt.TaskFileNotFoundError):
            rt.read_tasks("/bin/doc")

    def test_read_tasks(self, setup_paths):
        # rt.create_task_file(force=True)
        d = rt.read_tasks(setup_paths[0])
        assert d == {"tasks": ["task 1", "task 2", "task 3"], "title": "sample title"}

    def test_read_tasks_with_invalid(self, setup_paths):
        # rt.create_task_file(force=True)
        assert rt.read_tasks(setup_paths[1]) is None


# @pytest.mark.dev
class TestCreateTaskFile:
    # EXIST_INPUT = "~/.config/remind_task/tasks.yml"

    def test_exist_file(self, setup_paths):
        with pytest.raises(rt.TaskFileExsistsError):
            rt.create_task_file(setup_paths[0])

    def test_exist_file_and_force(self, mocker, setup_paths):
        mocker.patch("os.makedirs")
        mocker.patch("shutil.copy")
        # shutil.copy.__enter__.return_value = None
        rt.create_task_file(path=setup_paths[0], force=True)
        os.makedirs.assert_called_once()
        shutil.copy.assert_called_once()

    def test_create_task_file(self, mocker, setup_paths):
        # NOTFOUND_INPUT = "~/.config/remind_task/testfile"
        mocker.patch("os.makedirs")
        mocker.patch("shutil.copy")
        # shutil.copy.__enter__.return_value = None
        rt.create_task_file(setup_paths[2])
        os.makedirs.assert_called_once()
        shutil.copy.assert_called_once()


class TestCallNotification:
    """
    引数をosascriptに成型して呼ぶ
    前処理(osのチェック等)はnotificationで行うので呼ぶだけ
    sound_pathがtruthyならコマンドに反映される
    """

    def test_not_sound_path(self, mocker):
        mocker.patch("os.system")
        rt.call_notification("msg1", "title1", None)
        os.system.assert_called_once_with(
            'osascript -e \'display notification "msg1" with title "title1"\''
        )

    def test_with_sound_path(self, mocker):
        mocker.patch("os.system")
        rt.call_notification("msg1", "title1", "sound_file1")
        os.system.assert_called_once_with(
            'osascript -e \'display notification "msg1" with title "title1" sound name "sound_file1"\''
        )


class TestNotification:
    """
    引数を元にして通知を行う
    """

    def test_not_macos(self, mocker):
        """masos意外のplatformならFalseを返す"""
        mocker.patch("platform.system", return_value="Windows")
        assert rt.notification() is False

    def test_macos(self, mocker, setup_paths):
        """masos(Darwin)なら通知を行う"""
        sound_path = "/System/Library/Sounds/Purr.aiff"
        mocker.patch("platform.system", return_value="Darwin")
        mocker.patch.object(rt, "call_notification")
        rt.notification(setup_paths[0])
        rt.call_notification.assert_any_call("task 1", "sample title", sound_path)
        rt.call_notification.assert_any_call("task 2", "sample title", sound_path)
        rt.call_notification.assert_any_call("task 3", "sample title", sound_path)

    def test_macos_invalid(self, mocker, setup_paths):
        """taskが読み込めない場合はFalseを返す"""
        mocker.patch("platform.system", return_value="Darwin")
        assert rt.notification(setup_paths[1]) is False
