import setuptools
import subprocess


def get_git_version():
    return subprocess.run(
        ["git", "describe", "--abbrev=0"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    requirements = [line.strip() for line in fh.readlines()]

setuptools.setup(
    name="pyszuru",
    version=get_git_version(),
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
    python_requires=">=3.8",
    keywords=[
        "szurubooru",
        "booru",
    ],
)
