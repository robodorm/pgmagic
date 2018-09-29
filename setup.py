from setuptools import setup, find_packages

setup(
    name='pgmagic',
    version="2018-09.1",
    include_package_data=True,
    packages=find_packages(),
    install_requires=open("requirements.txt").read()
)
