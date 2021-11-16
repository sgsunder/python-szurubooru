import os
import re
import setuptools
import subprocess


def get_version():
    if "GITHUB_REF" in os.environ:
        m = re.match(r"refs\/tags\/([\d\.]+)", os.environ["GITHUB_REF"])
        if m:
            return m.group(1)
    return subprocess.run(
        ["git", "describe", "--abbrev=0"],
        stdout=subprocess.PIPE,
        universal_newlines=True,
        check=True,
    ).stdout.strip()


with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    requirements = [line.strip() for line in fh.readlines()]

setuptools.setup(
    name="pyszuru",
    version=get_version(),
    author="Shyam Sunder",
    author_email="sgsunder1@gmail.com",
    description="Python interface for szurubooru",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sgsunder/python-szurubooru",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements,
    python_requires=">=3.6",
    keywords=[
        "szurubooru",
        "booru",
    ],
)
