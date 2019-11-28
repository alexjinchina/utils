import os
import logging
import re

import common
from common import *


VS_VERS = ["2019", "2017"]
VS_INSTALL_TYPES = ["BuildTools", "Community"]
VC_ARCH = ["x86", "x64"]


def find_msvc(vs_vers=VS_VERS,
              vs_install_types=VS_INSTALL_TYPES,
              vs_arch=VC_ARCH
              ):
    PROGRAMFILES_X86 = os.environ["PROGRAMFILES(X86)"]

    msvc = {}
    for vs_ver, vs_install in [(vs_ver, vs_install)
                               for vs_ver in vs_vers
                               for vs_install in vs_install_types]:
        debug("checking %s(%s) ...", vs_ver, vs_install)
        vs_install_dir = os.path.join(
            PROGRAMFILES_X86,
            "Microsoft Visual Studio", vs_ver, vs_install, "VC")
        if not os.path.isdir(vs_install_dir):
            continue
        debug("install found: %s .", vs_install_dir)

        vcvarsall_bat = os.path.join(vs_install_dir,
                                     "Auxiliary",
                                     "Build", "vcvarsall.bat")
        if not os.path.isfile(vcvarsall_bat):
            debug("vcvarsall.bat not found. %s", vcvarsall_bat)
            continue
        vc_toolset_dir = os.path.join(vs_install_dir,
                                      "Tools",
                                      "MSVC")
        for toolset in os.listdir(vc_toolset_dir):
            if not re.match(r"\d+\.\d+.\d+.", toolset):
                debug("%s is not avalid toolset dir", toolset)
                continue
            debug("found toolset: %s", toolset)
            if toolset not in msvc:
                msvc[toolset] = []
            msvc[toolset].append(
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
    return msvc


if __name__ == "__main__":
    logger.setLevel(logging.NOTSET)
    print find_msvc()
    pass
