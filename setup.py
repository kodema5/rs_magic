import setuptools

with open("readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rs_magic",
    version="0.0.1",
    author="kodema5",
    author_email="kodema5@outlook.com",
    description="%%RS magic",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kodema5/jupyter-rs-magic",
    packages=setuptools.find_packages(),
    install_requires=[
        'cffi',
        'pixiedust',
        'pixiedust_node',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)