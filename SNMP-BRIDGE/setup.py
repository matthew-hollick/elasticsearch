"""Setup script for the SNMP-Bridge package."""

from setuptools import find_packages
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

setup(
    name="snmp-bridge",
    version="0.1.0",
    author="Hedgehog Analytics",
    author_email="info@hedgehoganalytics.example",
    description="A bridge between SNMP data and Elasticsearch",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/matthewhollick/elasticsearch/SNMP-BRIDGE",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "snmp-bridge=snmp_bridge.__main__:main",
        ],
    },
)
