import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="data_sourcery",
    version="0.5",
    author="Tiago Paranhos Lima",
    author_email="tiago@tiagoprnl.me",
    description="Get data (e.g. images) from sources.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tiagoprn/data_sourcery/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Natural Language :: English",
        "Topic :: Utilities",
        "Development Status :: 5 - Production/Stable"
    ],
)
