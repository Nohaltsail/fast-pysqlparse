from setuptools import setup, find_packages
import os
import sys
from configparser import ConfigParser
from setuptools.command.bdist_wheel import bdist_wheel as _bdist_wheel


conf = ConfigParser()
conf.read("build.conf")
PYTHON_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}"


VERSION = conf.get("VERSION", "version")
if os.name == "nt":
    PLATFORM_TAG = "win_amd64"
    # Windows 上的文件名模板，如 "pysqlparser.cp{pyver}-win_amd64.pyd"
    LIB_TEMPLATE = conf.get("WINDOWS", "3.10").replace("310", "{pyver}")
else:
    PLATFORM_TAG = "manylinux1_x86_64"  # 或其他合适的 Linux 平台标签
    # Linux 上的文件名模板，如 "pysqlparser.cpython-{pyver}m-x86_64-linux-gnu.so"
    LIB_TEMPLATE = conf.get("LINUX", "3.10").replace("310", "{pyver}")

# 根据当前 Python 版本生成实际的库文件名
PY_VER_NO_DOT = f"{sys.version_info.major}{sys.version_info.minor}"
LIB_FILENAME = LIB_TEMPLATE.format(pyver=PY_VER_NO_DOT)


class BdistWheel(_bdist_wheel):
    def finalize_options(self):
        super().finalize_options()

    def get_tag(self):
        python, abi, plat = super().get_tag()
        abi = f"cp{PY_VER_NO_DOT}"  # ABI 标签（与 Python 版本一致
        plat = PLATFORM_TAG
        python = f"cp{PY_VER_NO_DOT}"
        return python, abi, plat


setup(
    name="pysqlparse",
    version=VERSION,
    packages=find_packages(),
    package_data={'pysqlparse': [LIB_FILENAME]},
    include_package_data=True,
    description="Python SQL Parser",
    author="CYSun",
    author_email="changyinsun@hillstonenet.com",
    classifiers=[
        f"Programming Language :: Python :: {PYTHON_VERSION}",
        "Operating System :: Microsoft :: Windows" if os.name == "nt" else "Operating System :: POSIX :: Linux",
    ],
    python_requires=f">={PYTHON_VERSION}",
    cmdclass={'bdist_wheel': BdistWheel},
)
