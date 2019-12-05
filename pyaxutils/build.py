import subprocess
import sys
import logging
import os
import re
import argparse
import json

import utils
import msvc

BUILD_SETTINGS_FILENAME = "build-settings.json"

ALIASES = {
    "win32": "win",
    "win64": "win",
    "msvc141": "msvc",
    "msvc142": "msvc",
}


NEPHOS_DEBUG = int(os.environ.get("NEPHOS_DEBUG", 0))
if not __package__:
    logging.basicConfig()
    logger = logging.getLogger()
else:
    logger = logging.getLogger(__package__.name)

if NEPHOS_DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)


def get_by_alias(data, key, default=None):
    if key in data:
        return data[key]
    if key in ALIASES:
        return data.get(ALIASES[key], default)
    return default


ROOT_DIR = os.path.abspath(os.path.dirname(__file__))


class Settings:
    def __init__(self, **kwargs):
        self._keys = []
        for k, v in kwargs.iteritems():
            self._keys.append(k)
            setattr(self, k, v)

    def keys(self):
        return self._keys

    def get(self, key, default=None):
        if key in self._keys:
            return getattr(self, key)
        else:
            return default

    def set(self, key, value):
        if key not in self._keys:
            self._keys.append(key)
        setattr(self, key, value)
        return self

    def merge(self, **src):
        for k, v in src.iteritems():
            self.set(k, v)
        return self

    def __getitem__(self, key):
        if key not in self._keys:
            raise KeyError(key=key)
        return self.get(key)

    def __setitem__(self, k, v):
        self.set(k, v)

    def __contains__(self, k):
        return k in self._keys


class BuildSettings(Settings):
    def __init__(self, data):
        Settings.__init__(self, **data)
        self.platforms = utils.get_by_platform(**self.platforms)
        self.toolchains = Settings(
            **utils.transform(
                utils.get_by_platform(**self.toolchains),
                lambda k, v: Settings(**v)
            )
        )


class PlatformSetting:
    def __init__(self,
                 default=None,
                 **kwargs):
        self.default = default
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    def get(self):
        p = sys.platform
        if hasattr(self, p):
            return getattr(self, p)
        else:
            return self.default


# class Target:
#     def __init__(self,
#                  platform,
#                  toolchain,
#                  config,
#                  target,
#                  args,
#                  settings):

#         self.platform = platform
#         self.toolchain = toolchain
#         self.config = config
#         self.target = target
#         self.args = args

#         self.src_dir = os.path.join(args.src_dir, self._target.SRC_DIR)
#         self.build_dir = os.path.join(
#             self.args.build_dir, self.platform, self.toolchain, self.config)
#         if not os.path.isdir(self.build_dir):
#             os.makedirs(self.build_dir)
#         self.mingw_dir = args.mingw_dir
#         self.sh = args.sh

#     def setup(self, args=None):
#         args = args or self.args
#         self._target.setup(self, args)

#     def _write_file(self, filepath, content):
#         with open(filepath, 'wb') as fd:
#             fd.write(content)
#             fd.close()
#         return filepath

#     def write_build_file(self, filename, content):
#         return self._write_file(os.path.join(self.build_dir, filename), content)

#     def write_configure_script(self, content, ext=None):
#         filename = "configure" + \
#             (ext or {"win32": ".bat"}.get(sys.platform, ""))
#         return self.write_build_file(os.path.join(self.build_dir, filename),
#                                      content)

#     def to_mingw_path(self, path):
#         path = os.path.abspath(path)
#         path = path.split('\\')
#         path[0] = "/%s" % path[0][0].lower()
#         return "/".join(path)

#     @property
#     def is_win(self):
#         return self.platform in ("win32", "win64")

#     @property
#     def is_msvc(self):
#         return self.toolchain.startswith("msvc")

#     @property
#     def is_debug(self):
#         return self.config == "Debug"

#     @property
#     def config_dict(self):
#         d = obj_to_dict(self, excludes=["config_dict"])
#         obj_to_dict(self._toolchain, d, "toolchain_")
#         return d

#     def call_sh(self, func, *cmd, **kwargs):
#         func = func or subprocess.call
#         sh = [self.sh]
#         if "no_login" in kwargs:
#             if not kwargs["no_login"]:
#                 sh += ["--login"]
#             del kwargs["no_login"]
#         sh += list(cmd)
#         return func(sh, **kwargs)

#     def check_sh_output(self, *cmd, **kwargs):
#         return self.call_sh(subprocess.check_output, *cmd, **kwargs).strip()

#     def check_sh_cmd_output(self, *cmd, **kwargs):
#         return self.check_sh_output(
#             "-c",
#             " ".join([(' ' in x) and '"%s"' % x or x for x in cmd]),
#             **kwargs
#         )

#     def to_sh_path(self, path):
#         if os.path.isdir(path):
#             return self.check_sh_cmd_output("pwd", no_login=True, cwd=path)

#         elif os.path.isfile(path):
#             return "/".join([self.to_sh_path(os.path.dirname(path)),
#                              os.path.basename(path)])

#             # return self.check_sh_cmd_output("realpath", os.path.basename(path),
#             #                                 cwd=os.path.dirname(path)
#             #                                 )
#         else:
#             raise RuntimeError("path %s not found!" % path)
#     pass


# def args_to_sh_cmdline(*args):
#     return " ".join([arg.strip().replace(" ", "\\ ") for arg in args])


settings = dict(
    src_dir=os.path.join(ROOT_DIR, "src"),
    buld_dir=os.path.join(ROOT_DIR, "build"),
    dist_dir=os.path.join(ROOT_DIR, "dist"),
    mingw_dir=os.path.join("C:\\", "MinGW"),
    # sh_path=dict(win32=None,
    #              default="/bin/sh"),
    platforms=dict(win32=["win32", "win64"]),
    toolchains=dict(
        win32=dict(
            msvc141=dict(
                toolset="14.1",
                arch=dict(
                    win32="x86",
                    win64="x64",
                )
            )
        )
    ),
    configs=["Debug", "Release"],
    targets=[],


)

argv = sys.argv[1:]

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose",
                    help="log level",
                    action="count",
                    default=0)
args, argv = parser.parse_known_args(argv)
if args.verbose > 0:
    level = min(logging.INFO - args.verbose * 10, logging.NOTSET)
    logger.setLevel(level=level)
    logger.log(level, "log level=%s" % level)


# parser = argparse.ArgumentParser()
parser.add_argument("--settings-file",
                    nargs="?",
                    help="settings file",
                    action="append",
                    dest="settings")
args, argv = parser.parse_known_args(argv)

for cfg in [BUILD_SETTINGS_FILENAME] + (args.settings or[]):
    cfg = os.path.join(ROOT_DIR, cfg)
    if not os.path.isfile(cfg):
        continue
    with open(cfg) as fd:
        cfg = json.load(fd)
        fd.close()
    utils.merge(settings, cfg)


# def update_settings(data):
#     global settings
#     utils.merge_keys_call(
#         settings, data,
#         src_dir=lambda x: utils.abspath(x, ROOT_DIR),
#         buld_dir=lambda x: utils.abspath(x, ROOT_DIR),
#         dist_dir=lambda x: utils.abspath(x, ROOT_DIR),
#         mingw_dir=utils.abspath,
#         sh_path=lambda x: x,
#         platforms=lambda x: x,
#         toolchains=lambda x: x,
#         configs=None,
#         targets=None
#     )


# utils.merge(settings, os.environ)
settings = BuildSettings(settings)


parser.add_argument("-s", "--src-dir",
                    help="src dir",
                    default=settings.src_dir)

parser.add_argument("-b", "--build-dir",
                    help="build dir",
                    default=settings.buld_dir)

parser.add_argument("-d", "--dist-dir",
                    help="dist dir",
                    default=settings.dist_dir)

if sys.platform == "win32":
    parser.add_argument("--mingw-dir",
                        help="mingw dir",
                        dest="mingw_dir",
                        default=settings.mingw_dir)

parser.add_argument("--sh",
                    help="sh path",
                    dest="sh_path",
                    default=None)

parser.add_argument("-p", "--platform",
                    help="platform",
                    action="append",
                    dest="platforms",
                    choices=settings.platforms)

parser.add_argument("--toolchain",
                    help="tool chain",
                    action="append",
                    dest="toolchains",
                    choices=settings.toolchains.keys())

parser.add_argument("-c", "--config",
                    help="config type",
                    action="append",
                    dest="configs",
                    choices=settings.configs)

parser.add_argument("-t", "--target",
                    nargs="?",
                    help="build targets",
                    action="append",
                    dest="targets")

parser.add_argument("--configure",
                    action="store_true",
                    help="configure targets",
                    default=None)

parser.add_argument("--build",
                    action="store_true",
                    help="build targets",
                    default=None)

parser.add_argument("--install",
                    action="store_true",
                    help="install targets",
                    default=None)

args = parser.parse_args(argv)
logger.debug(args)


if args.configure is None and args.build is None and args.install is None:
    args.configure = True
    args.build = True
    args.install = True

if args.sh_path is not None and not os.path.isfile(args.sh_path):
    raise RuntimeError("sh not found(%s)!" % args.sh_path)

if sys.platform == "win32":
    if args.mingw_dir:
        if not os.path.isdir(args.mingw_dir):
            raise RuntimeError("mingw dir not found(%s)!" % args.mingw_dir)
        if args.sh_path is None:
            args.sh_path = os.path.join(
                args.mingw_dir, "msys", "1.0", "bin", "sh.exe")

logger.debug("mingw_dir=%s" % args.mingw_dir)

if args.sh_path is None:
    try:
        subprocess.check_call(["sh", "--version"])
        args.sh_path = "sh"
    except subprocess.CalledProcessError:
        pass
    except WindowsError:
        pass
logger.debug("sh_path=%s" % args.sh_path)

if not args.platforms:
    args.platforms = settings.platforms

if not args.toolchains:
    args.toolchains = settings.toolchains.keys()


if not args.configs:
    args.configs = settings.configs

if not args.targets:
    args.targets = settings.targets

logger.debug(args)

for platform, toolchain, config, target in [
    (platform, toolchain, config, target)
    for platform in args.platforms
    for toolchain in args.toolchains
    for config in args.configs
    for target in args.targets
]:
    if platform not in settings.platforms:
        raise RuntimeError("unknown platform '%s'" % platform)
    if toolchain not in settings.toolchains:
        raise RuntimeError("unknown toolchain '%s'" % toolchain)
    toolchain_settings = settings.toolchains[toolchain]

    if config not in settings.configs:
        raise RuntimeError("unknown config '%s'" % config)
    if target not in settings.targets:
        raise RuntimeError("unknown target '%s'" % target)

    print platform, toolchain, config, target  # , args

    os.environ["SH_PATH"] = args.sh_path or ""

    src_dir = utils.abspath(target, args.src_dir)
    logger.debug("SRC_DIR=%s", src_dir)
    os.environ["SRC_DIR"] = src_dir

    build_dir = utils.makedirs(args.build_dir,
                               platform, toolchain, config, target)
    logger.debug("BUILD_DIR=%s", build_dir)
    os.environ["BUILD_DIR"] = build_dir

    target_settings = utils.load_json(
        os.path.join(src_dir, BUILD_SETTINGS_FILENAME), {})

    target_settings = get_by_alias(target_settings, platform, target_settings)
    target_settings = get_by_alias(target_settings, toolchain, target_settings)
    target_settings = get_by_alias(target_settings, config, target_settings)
    target_settings = Settings(disable=False,
                               configure="configure",
                               build="build",
                               install="install",
                               shell=True).merge(**target_settings)

    if target_settings.disable:
        logger.info("target '%s' for %s/%s/%s disabled.",
                    target, platform, toolchain, config)
        continue

    if toolchain.startswith("msvc"):
        arch = toolchain_settings.arch[platform]
        toolchain_settings = msvc.get_msvc(
            arch, toolset=toolchain_settings.toolset)
        print toolchain_settings
    else:
        raise RuntimeError("unknown toolchian '%s'" % toolchain)

    if args.configure:
        logger.info("configuring...")
        if target_settings.shell:
            cmd = "%s && \"%s\" %s %s %s" % (
                toolchain_settings.shell_setvars,
                os.path.join(src_dir, target_settings.configure),
                platform,
                toolchain,
                config)
            subprocess.check_call(
                cmd,
                cwd=build_dir,
                shell=True
            )
        else:
            raise RuntimeError("must shell=1")

    if args.build:
        logger.info("building...")
        if target_settings.shell:
            cmd = "%s && \"%s\" %s %s %s" % (
                toolchain_settings.shell_setvars,
                os.path.join(src_dir, target_settings.build),
                platform,
                toolchain,
                config)
            subprocess.check_call(
                cmd,
                cwd=build_dir,
                shell=True
            )
        else:
            raise RuntimeError("must shell=1")

    # if args.install:
    #     if target_settings.shell:
    #         cmd = "%s && \"%s\" %s %s %s" % (
    #             toolchain_settings.shell_setvars,
    #             os.path.join(src_dir, target_settings.install),
    #             platform,
    #             toolchain,
    #             config)
    #         subprocess.check_call(
    #             cmd,
    #             cwd=build_dir,
    #             shell=True
    #         )
    #     else:
    #         raise RuntimeError("must shell=1")

    #assert 0

# def get_build_targets(targets=[], args=args):
#   targets = targets or args.target
#   return [BuildTarget(platform=platform,
#                       toolchain=toolchain,
#                       config=config,
#                       target=target,
#                       args=args)
#           for (platform, toolchain, config) in get_build_configs()
#           for target in TARGETS
#           if not targets or target in targets]

# def obj_to_dict(obj, d={}, key_prefix="", excludes=None):
#   for k in dir(obj):
#     if k.startswith("_"):
#       continue
#     if excludes and k in excludes:
#       continue
#     v = getattr(obj, k)
#     if not isinstance(v, str):
#       continue
#     k = key_prefix + k
#     d[k] = v
#   return d
