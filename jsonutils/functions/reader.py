import json
from typing import Any, List
from functools import partial
import requests
from jsonutils.exceptions import JSONDecodeException
from jsonutils.functions.parsers import url_validator
from jsonutils.utils.retry import retry_function
import multiprocessing as mp


def _open_multiple_files(file_list: List[str], raise_exception: bool, **kwargs) -> List:
    if not file_list:
        raise ValueError("You must specify at least one path to open")
    FUNCTION = partial(_open_single_file, raise_exception=raise_exception, **kwargs)
    with mp.Pool() as pool:
        results = pool.map(FUNCTION, file_list)
    return results


def _open_single_file(file: str, raise_exception: bool, **kwargs) -> Any:
    file = str(file)
    # decide whether to use requests.get or requests.post by checking kwargs
    if kwargs.get("json") or kwargs.get("data"):
        FUNCTION = requests.post
    else:
        FUNCTION = requests.get
    if url_validator(file):
        req = retry_function(FUNCTION, file, raise_exception=raise_exception, **kwargs)
        try:
            data = req.json()
        except Exception as e:
            raise JSONDecodeException(f"Selected URL has no valid json file. Details: {e}")
        else:
            return data
    with open(file) as f:
        data = json.load(f)
    return data
