try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='cmipdata',
    version='0.6',
    author='Neil C. Swart',
    author_email='Neil.Swart@canada.ca',
    packages=['cmipdata'],
    scripts=[],
    url='https://github.com/swartn/cmipdata',
    download_url='https://github.com/swartn/cmipdata/archive/v0.6.zip',
    keywords = ['climate', 'data', 'CMIP5', 'CMIP6', 'NetCDF', 'analysis', 'processing'],
    license='LICENSE.txt',
    description='Processing tools for large ensembles of CMIP type netcdf data',
    long_description=open('README.rst').read(),
    install_requires=[
        'cdo >=1.2.5',
        'netCDF4 >=1.1.6',
        'numpy >=1.2.1',
        'matplotlib >=1.4.3',
    ],    
)


