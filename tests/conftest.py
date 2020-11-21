import os
import pytest
import yaml


@pytest.fixture(scope="module", autouse=True)
def setup_paths():
    # test start
    # Before hook
    TEST_TASK_PATH = ".tmp/tasks.yml"
    TEST_TASK_PATH_INVALID = ".tmp/tasks.invalid.yml"
    TEST_TASK_PATH_NOTFOUND = ".tmp/notfound.yml"
    data = {"title": "sample title", "tasks": ["task 1", "task 2", "task 3"]}
    os.makedirs(".tmp", exist_ok=True)
    with open(TEST_TASK_PATH, mode="w") as f:
        yaml.dump(data, stream=f)
    with open(TEST_TASK_PATH_INVALID, mode="w") as f:
        yaml.dump({"tasks": []}, stream=f)
    # Before hook end
    yield (TEST_TASK_PATH, TEST_TASK_PATH_INVALID, TEST_TASK_PATH_NOTFOUND)
    # after hook
    os.remove(TEST_TASK_PATH)
    os.remove(TEST_TASK_PATH_INVALID)
    # test end