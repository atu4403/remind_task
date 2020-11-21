import os
import platform
import pathlib
import shutil
import yaml

DEFAULT_SOUND_DIRECTORY = "/System/Library/Sounds/"
DEFAULT_SOUND_FILE = "Purr.aiff"
DEFAULT_SOUND_PATH = os.path.join(DEFAULT_SOUND_DIRECTORY, DEFAULT_SOUND_FILE)
TASK_FILE_PATH = "~/.config/remind_task/tasks.yml"


class TaskFileNotFoundError(Exception):
    """taskfileが存在しないことを知らせるエラー"""

    pass


class TaskFileExsistsError(Exception):
    """taskfileが存在することを知らせるエラー"""

    pass


class NotMacosError(Exception):
    """macOSではないことをを知らせるエラー"""

    pass


def get_task_path(path: str = TASK_FILE_PATH):
    return pathlib.Path(path).expanduser()


def get_soundfile(path: str = DEFAULT_SOUND_PATH):
    """
    効果音のファイルパスを取得する
    pathがfalsyならNoneを返す

    引数pathのデフォルトをTASK_FILE_PATHにする
    引数pathは文字列のみ
    絶対パスならその値、相対パスなら規定のディレクトリとjoinする
    いずれの場合も存在チェックを行い、存在しないなら TASK_FILE_PATHを返す
    """
    if type(path) != str:
        return DEFAULT_SOUND_PATH
    else:
        validate_path = DEFAULT_SOUND_PATH
        if os.path.isabs(path):
            validate_path = path
        else:
            validate_path = os.path.join(DEFAULT_SOUND_DIRECTORY, path)
        if os.path.isfile(validate_path):
            return validate_path
        else:
            return DEFAULT_SOUND_PATH


def create_task_file(path: str = TASK_FILE_PATH, force: bool = False):
    """
    taskを記す為のファイルを作成する
    引数pathの場所もしくはTASK_FILE_PATHに作成する
    pathの場所がexistならTaskFileExsistsErrorを投げる
    forceが真なら上書きで作成する
    返り値は作成したファイルのpath
    """
    path = get_task_path(path)
    if os.path.isfile(path) and not force:
        raise TaskFileExsistsError("その場所には既にファイルが存在します")
    else:
        dir_name = os.path.dirname(path)
        os.makedirs(dir_name, exist_ok=True)
        return shutil.copy("src/remind_task/tasks.yml", path)


def read_tasks(task_path: str = TASK_FILE_PATH):
    """
    ~/.config/remind_task/tasks.ymlからdictを読み込む
    存在しない場合は作成を促すメッセージを含んだ例外を投げる
    テキストが何も含まれてない、もしくはtasksが空ならNoneを返す
    """
    path = pathlib.Path(task_path).expanduser()
    if not os.path.isfile(path):
        raise TaskFileNotFoundError(f"{TASK_FILE_PATH}が存在しません")
    with open(path) as f:
        d = yaml.safe_load(f)
    if d.get("tasks"):
        return d
    else:
        return None


def call_notification(msg: str, title: str, sound_path: str):
    """
    osascriptを呼び、コマンドを文字列で返す
    """
    res = f"""osascript -e 'display notification "{msg}" with title "{title}\""""
    if sound_path:
        res += f""" sound name "{sound_path}"'"""
    else:
        res += "'"
    os.system(res)
    return res


def notification(task_path: str = TASK_FILE_PATH):
    """
    osxの通知を使い、msgを流す

    args:
        task_path (str): taskfileのpath 指定しない場合は~/.config以下になる

    Returns:
        str: 通知の際に内部で呼ばれるコマンド

    Raises:
        TaskFileNotFoundError: taskfileが存在しない場合
    """
    if platform.system() != "Darwin":
        return False
    d = read_tasks(task_path)  # TaskFileNotFoundErrorが投げられる可能性があるが、cli側で処理する

    if d and type(d["tasks"]) == list:
        title = d.get("title") or "remind"
        sound_path = get_soundfile(d.get("sound"))
        for task in d["tasks"]:
            call_notification(task, title, sound_path)
        return d
    else:
        return False
