from distutils.core import setup
from Cython.Build import cythonize
setup(ext_modules = cythonize(["encode.py"],language_level = "3"))