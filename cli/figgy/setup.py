import re
from setuptools import setup, find_packages
import platform

# Platform Constants
LINUX, MAC, WINDOWS = "Linux", "Darwin", "Windows"

SHORT_DESCRIPTION = "Figgy is a free and opensource serverless application config framework designed to bring " \
                    "simplicity, security, and resilience to application config management. Figgy is built on top of" \
                    " AWS ParameterStore and leverages native AWS constructs such as AWS IAM, KMS, among other " \
                    "services to ensure a simple and elegant integration with your AWS environment."

with open('../../README.md', 'r') as readme:
    LONG_DESCRIPTION = readme.read()

with open('config/constants.py') as file:
    contents = file.read()
    VERSION = re.search(r'^VERSION\s*=\s*["\'](.*)["\']', contents, re.MULTILINE)
    GITHUB = re.search(r'^FIGGY_GITHUB\s*=\s*["\'](.*)["\']', contents, re.MULTILINE)

VERSION = VERSION.group(1)
GITHUB = GITHUB.group(1)
FIGGY_WEBSITE = "https://figgy.dev"

with open('./requirements.txt', 'r') as file:
    requirements = file.readlines()

if platform.system() == WINDOWS:
    with open('./requirements-windows.txt', 'r') as file:
        requirements += file.readlines()
elif platform.system() == LINUX:
    with open('./requirements-linux.txt', 'r') as file:
        requirements += file.readlines()
elif platform.system() == MAC:
    with open('./requirements-darwin.txt', 'r') as file:
        requirements += file.readlines()

setup(
    name="figgy-cli",
    packages=find_packages() + ['.'],
    entry_points={
        "console_scripts": ['figgy = figgy:main']
    },
    version=VERSION,
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Jordan Mance",
    author_email="jordan@figgy.dev",
    url=FIGGY_WEBSITE,
    python_requires='>=3.7',
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ]
)