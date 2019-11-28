import os
import re


import logging
logger = logging.getLogger("find_msvc")


VS_VERS = ["2019", "2017"]
VS_INSTALL_TYPES = ["BuildTools", "Community"]
VC_ARCH = ["x86", "x64"]


def find_msvc(vs_vers=VS_VERS,
              vs_install_types=VS_INSTALL_TYPES,
              vs_arch=VC_ARCH,
              logger=logger
              ):

    PROGRAMFILES_X86 = os.environ["PROGRAMFILES(X86)"]

    msvc = {}
    for vs_ver, vs_install in [(vs_ver, vs_install)
                               for vs_ver in vs_vers
                               for vs_install in vs_install_types]:
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
    if logger:
        logger.setLevel(0)
    print find_msvc()
    pass
