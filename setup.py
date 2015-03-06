#!/usr/bin/env python
from setuptools import setup

setup(
    name='withings-devices',
    version='0.1',
    description="Library for the Withings Devices",
    author='Cyril Peponnet',
    author_email='cyril@peponnet.fr',
    url="https://github.com/CyrilPeponnet/withings-devices",
    license = "GPLv3 License",
    packages = ['withingsdevices'],
    install_requires = ['requests'],
    keywords="withings-devices",
    zip_safe = True
)
