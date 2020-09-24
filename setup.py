import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyszuru",
    version="0.1.0",
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
    python_requires=">=3.8",
)
