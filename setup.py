from setuptools import setup, find_packages

setup(
    name="penumbra-parser",
    version="0.1.0",
    packages=find_packages(),
    install_requires=open("parser/requirements.txt").readlines(),
    python_requires=">=3.9",
)
