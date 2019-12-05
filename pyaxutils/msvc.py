import os
import re
import sys

import logging
logger = logging.getLogger("find_msvc")


VS_VERS = ["2019", "2017"]
VS_INSTALL_TYPES = ["BuildTools", "Community"]
VC_ARCH = ["x86", "x64"]

INSTALLED_MSVC = {}
PROGRAMFILES_X86 = os.environ["PROGRAMFILES(X86)"]

for vs_ver, vs_install in [(vs_ver, vs_install)
                           for vs_ver in VS_VERS
                           for vs_install in VS_INSTALL_TYPES]:
    logger.debug("checking %s(%s) ...", vs_ver, vs_install)
    vs_install_dir = os.path.join(
        PROGRAMFILES_X86,
        "Microsoft Visual Studio", vs_ver, vs_install, "VC")
    if not os.path.isdir(vs_install_dir):
        continue
    logger.debug("install found: %s .", vs_install_dir)

    vcvarsall_bat = os.path.join(vs_install_dir,
                                 "Auxiliary",
                                 "Build", "vcvarsall.bat")
    if not os.path.isfile(vcvarsall_bat):
        logger.debug("vcvarsall.bat not found. %s", vcvarsall_bat)
        continue
    vc_toolset_dir = os.path.join(vs_install_dir,
                                  "Tools",
                                  "MSVC")
    for toolset in os.listdir(vc_toolset_dir):
        if not re.match(r"\d+\.\d+.\d+.", toolset):
            logger.debug("%s is not avalid toolset dir", toolset)
            continue
        logger.debug("found toolset: %s", toolset)
        if toolset not in INSTALLED_MSVC:
            INSTALLED_MSVC[toolset] = []
        INSTALLED_MSVC[toolset].append(
            dict(
                toolset=toolset,
                vs_ver=vs_ver,
                vs_install=vs_install,
                vs_install_dir=vs_install_dir,
                vcvarsall_bat=vcvarsall_bat,
                vc_toolset_dir=vc_toolset_dir,
            )
        )
        continue
    continue


def find_msvc(toolset=None,
              logger=logger):

    toolsets = sorted([x for x in INSTALLED_MSVC.keys()
                       if not toolset or x.startswith(toolset)
                       ], reverse=True)
    if not toolsets:
        raise RuntimeError("toolset '%s' not found" % toolset)
    return INSTALLED_MSVC[toolsets[0]][0]


class MSVC:
    def __init__(self, installed, arch):
        self.installed = installed
        self.arch = arch

    def __repr__(self):
        return "<MSVC toolset=%s;arch=%s>" % (self.toolset, self.arch)

    @property
    def toolset(self):
        return self.installed["toolset"]

    @property
    def shell_setvars(self):
        return "\"%s\" %s -vcvars_ver=%s" % (
            self.installed["vcvarsall_bat"],
            self.arch,
            self.installed["toolset"])


def get_msvc(arch, toolset=None):
    return MSVC(find_msvc(toolset=toolset), arch)


if __name__ == "__main__":
    if logger:
        logger.setLevel(0)
    print get_msvc("x86")
    pass
