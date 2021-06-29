import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="qtutils",
    version="0.1",
    author="Alberto Tosato",
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
    # package_dir={"": "qtutils"},
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires=[
        'pyqtgraph', 'xarray', 'matplotlib', 'xrft'
    ],
)