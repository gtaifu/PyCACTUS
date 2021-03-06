from setuptools import setup, find_packages
from distutils.version import StrictVersion
from importlib import import_module
import re


def get_version(verbose=1):
    """ Extract version information from source code """

    try:
        with open('pycactus/version.py', 'r') as f:
            for ln in f:
                print("line read: ", ln)
                trim_ln = ln.strip()
                if (len(trim_ln) > 0 and trim_ln[0] == '#'):
                    continue
                m = re.search('.* ''(.*)''', ln)
                version = (m.group(1)).strip('\'')
    except Exception as E:
        print(E)
        version = 'none'
    if verbose:
        print('get_version: %s' % version)
    return version


setup(name='pycactus',
      version=get_version(),
      use_2to3=False,
      description='A functional eQASM simulator without timing modeling',
      author='Xiang Fu',
      author_email='gtaifu@gmail.com',
      packages=['pycactus'],
      install_requires=['quantumsim==0.2.0', 'bitstring', 'ply']
      )
