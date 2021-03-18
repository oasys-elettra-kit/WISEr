#! /usr/bin/env python3
# from importlib.machinery import SourceFileLoader
# import types
from importlib.machinery import SourceFileLoader
import os
import subprocess

try:
    from setuptools import find_packages, setup
except AttributeError:
    from setuptools import find_packages, setup

NAME = 'LibWiser'

VERSION = '0.10.1'
ISRELEASED = True

DESCRIPTION = 'Wiser kernel library'
README_FILE = os.path.join(os.path.dirname(__file__), 'README.txt')
LONG_DESCRIPTION = open(README_FILE).read()
AUTHOR = 'Michele Manfredda, Lorenzo Raimondi, Aljosa Hafner'
AUTHOR_EMAIL = 'michele.manfredda@elettra.eu, lorenzo.raimondi@elettra.eu'
URL = 'https://github.com/oasys-elettra-kit/WISEr'
DOWNLOAD_URL = 'https://github.com/oasys-elettra-kit/WISEr'
MAINTAINER = 'Michele Manfredda'
MAINTAINER_EMAIL = 'michele.manfredda@elettra.eu'
LICENSE = 'GPLv3'

KEYWORDS = [
    'wavefront propagation',
    'simulation'
]

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Environment :: Plugins',
    'Programming Language :: Python :: 3',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Intended Audience :: Education',
    'Intended Audience :: Science/Research',
    'Intended Audience :: Developers'
]

INSTALL_REQUIRES = (
    'setuptools',
    'numpy',
    'scipy',
    'engineering_notation',
    'numba',
    'pathlib'
)

SETUP_REQUIRES = (
    'setuptools'
)


# Return the git revision as a string
def git_version():
    """Return the git revision as a string.

    Copied from numpy setup.py
    """
    def _minimal_ext_cmd(cmd):
        # construct minimal environment
        env = {}
        for k in ['SYSTEMROOT', 'PATH']:
            v = os.environ.get(k)
            if v is not None:
                env[k] = v
        # LANGUAGE is used on win32
        env['LANGUAGE'] = 'C'
        env['LANG'] = 'C'
        env['LC_ALL'] = 'C'
        out = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=env).communicate()[0]
        return out

    try:
        out = _minimal_ext_cmd(['git', 'rev-parse', 'HEAD'])
        GIT_REVISION = out.strip().decode('ascii')
    except OSError:
        GIT_REVISION = "Unknown"

    return GIT_REVISION


def write_version_py(filename='LibWiser/version.py'):
    # Copied from numpy setup.py
    cnt = """
# THIS FILE IS GENERATED FROM OASYS SETUP.PY
short_version = '%(version)s'
version = '%(version)s'
full_version = '%(full_version)s'
git_revision = '%(git_revision)s'
release = %(isrelease)s

if not release:
    version = full_version
    short_version += ".dev"
"""
    FULLVERSION = VERSION
    if os.path.exists('.git'):
        GIT_REVISION = git_version()
    elif os.path.exists('LibWiser/version.py'):
        # must be a source distribution, use existing version file
        version = SourceFileLoader("LibWiser.version", "LibWiser/version.py").load_module()

        # version = SourceFileLoader("LibWiser.version", "LibWiser/version.py")
        GIT_REVISION = version.git_revision
    else:
        GIT_REVISION = "Unknown"

    if not ISRELEASED:
        FULLVERSION += '.dev0+' + GIT_REVISION[:7]

    a = open(filename, 'w')
    try:
        a.write(cnt % {'version': VERSION,
                       'full_version': FULLVERSION,
                       'git_revision': GIT_REVISION,
                       'isrelease': str(ISRELEASED)})
    finally:
        a.close()


PACKAGES = find_packages(exclude=('*.tests', '*.tests.*', 'tests.*', 'tests'))

PACKAGE_DATA = {
}

#import shutil, sys

#from distutils.core import setup
#from distutils.extension import Extension

#ext_modules=[
#    Extension("wiselib2.Rayman",               ["wiselib2/Rayman.pyx"]),
#    Extension("orangecontrib.xrdanalyzer.controller.fit.fitters.fitter_minpack",       ["orangecontrib/xrdanalyzer/controller/fit/fitters/fitter_minpack.pyx"]),
#    Extension("orangecontrib.xrdanalyzer.controller.fit.fitters.fitter_minpack_util",  ["orangecontrib/xrdanalyzer/controller/fit/fitters/fitter_minpack_util.pyx"]),
#]


def setup_package():
    write_version_py()

    #from Cython.Distutils import build_ext

    setup(
        name=NAME,
        version=VERSION,
        description=DESCRIPTION,
        long_description_content_type = 'text/markdown',
        long_description=LONG_DESCRIPTION,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        url=URL,
        download_url=DOWNLOAD_URL,
        license=LICENSE,
        keywords=KEYWORDS,
        classifiers=CLASSIFIERS,
        packages=PACKAGES,
        package_data=PACKAGE_DATA,
        # extra setuptools args
        zip_safe=False,  # the package can run out of an .egg file
        include_package_data=True,
        install_requires=INSTALL_REQUIRES,
        setup_requires=SETUP_REQUIRES,
        #cmdclass = {'build_ext': build_ext},
        #ext_modules = ext_modules,
    )

if __name__ == '__main__':
    setup_package()
