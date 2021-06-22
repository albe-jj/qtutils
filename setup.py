import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="qtutils",
    version="0.1",
    author="Alberto Tosat",
    author_email="albe.jj@gmail.com",
    description="Measurement and analysis software",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/albe-jj/qtutils",
    project_urls={
        "Bug Tracker": "https://github.com/albe-jj/qtutils/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where=None),
    python_requires=">=3.6",
)