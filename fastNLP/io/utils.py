__all__ = [
    "check_loader_paths"
]

import os
from pathlib import Path
from typing import Union, Dict

# from ..core import log


def check_loader_paths(paths: Union[str, Dict[str, str]]) -> Dict[str, str]:
    r"""
    检查传入 ``dataloader`` 的文件的合法性。如果为合法路径，将返回至少包含 ``'train'`` 这个 key 的字典。类似于下面的结果::

        {
            'train': '/some/path/to/', # 一定包含，建词表应该在这上面建立，剩下的其它文件应该只需要处理并index。
            'test': 'xxx' # 可能有，也可能没有
            ...
        }

    如果 ``paths`` 为不合法的，将直接进行 raise 相应的错误。如果 ``paths`` 内不包含 ``'train'`` 也会报错。

    :param str paths: 路径。可以为：
    
            - 一个文件路径，此时认为该文件就是 train 的文件；
            - 一个文件目录，将在该目录下寻找包含 ``train`` （文件名中包含 train 这个字段）， ``test`` ，``dev`` 这三个字段的文件或文件夹；
            - 一个 dict, 则 key 是用户自定义的某个文件的名称，value 是这个文件的路径。
    :return:
    """
    if isinstance(paths, (str, Path)):
        paths = os.path.abspath(os.path.expanduser(paths))
        if os.path.isfile(paths):
            return {'train': paths}
        elif os.path.isdir(paths):
            filenames = os.listdir(paths)
            filenames.sort()
            files = {}
            for filename in filenames:
                path_pair = None
                if 'train' in filename:
                    path_pair = ('train', filename)
                if 'dev' in filename:
                    if path_pair:
                        raise Exception(
                            "Directory:{} in {} contains both `{}` and `dev`.".format(filename, paths, path_pair[0]))
                    path_pair = ('dev', filename)
                if 'test' in filename:
                    if path_pair:
                        raise Exception(
                            "Directory:{} in {} contains both `{}` and `test`.".format(filename, paths, path_pair[0]))
                    path_pair = ('test', filename)
                if path_pair:
                    if path_pair[0] in files:
                        raise FileExistsError(f"Two files contain `{path_pair[0]}` were found, please specify the "
                                              f"filepath for `{path_pair[0]}`.")
                    files[path_pair[0]] = os.path.join(paths, path_pair[1])
            # if 'train' not in files:
            #     raise KeyError(f"There is no train file in {paths}.")
            return files
        else:
            raise FileNotFoundError(f"{paths} is not a valid file path.")
    
    elif isinstance(paths, dict):
        if paths:
            # if 'train' not in paths:
            #     raise KeyError("You have to include `train` in your dict.")
            for key, value in paths.items():
                if isinstance(key, str) and isinstance(value, str):
                    value = os.path.abspath(os.path.expanduser(value))
                    if not os.path.exists(value):
                        raise TypeError(f"{value} is not a valid path.")
                    paths[key] = value
                else:
                    raise TypeError("All keys and values in paths should be str.")
            return paths
        else:
            raise ValueError("Empty paths is not allowed.")
    else:
        raise TypeError(f"paths only supports str and dict. not {type(paths)}.")
