import logging
import os
import sys
import copy
import json

_logger = logging.getLogger(
    __package__ and __package__.name or os.path.basename(__file__))


def load_json(filename, default=None):
    try:
        with open(filename) as fd:
            d = json.load(fd)
            fd.close()
            return d
    except IOError:
        if default is not None:
            return None
        raise
    pass


def get_by_platform(**kwargs):
    return kwargs.get(sys.platform, kwargs.get("default"))


def abspath(path, dirname=None):
    if os.path.isabs(path):
        return path
    if dirname:
        return abspath(os.path.join(dirname, path))

    return os.path.abspath(path)


def makedirs(*path):
    path = os.path.join(*path)
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def get_value(obj, **kwargs):
    return [obj.get(key, kwargs[key]) for key in kwargs]


def merge_keys(dst, src, *keys, **kwargs):
    pred = get_value(kwargs, pred=copy.deepcopy)
    for key in keys:
        if key in src:
            v = src[key]
            dst[key] = pred(v)


def merge_keys_call(dst, src, dst_prefix=None, src_prefix=None, **kwargs):
    dst_prefix = dst_prefix or ""
    src_prefix = src_prefix or ""
    for key, pred in kwargs.items():
        if key in src:
            v = src[src_prefix + key]
            if callable(pred):
                v = pred(v)
            elif pred is None:
                pass
            else:
                raise RuntimeError("cannot call pred for key `%s'!" % key)

            dst[dst_prefix + key] = v


def keys(obj):
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj.keys()
    return [x for x in dir(obj) if x and not x.startswith("_")]


def transform(obj, *func, **kwfunc):
    for k in keys(obj):
        for f in func:
            obj[k] = f(k, obj[k])
        if k in kwfunc:
            obj[k] = kwfunc[k](k, obj[k])
    return obj


def merge(dst, *srcs):
    for src in srcs:
        for k in src:
            if k in dst and isinstance(dst[k], dict):
                merge(dst[k], src[k])
            else:
                dst[k] = copy.deepcopy(src[k])
            continue
        continue
    return dst


if __name__ == "__main__":

    pass
