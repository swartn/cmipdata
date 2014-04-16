try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='cmipdata',
    version='0.0.1dev',
    author='Neil C. Swart',
    author_email='Neil.Swart@ec.gc.ca',
    packages=['cmipdata'],
    scripts=[],
    url='',
    license='LICENSE.txt',
    description='Processing tools for large ensembles of CMIP type netcdf data',
    long_description=open('README.txt').read(),
)


