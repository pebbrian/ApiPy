import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyApiManager",
    version="0.0.1",
    author="Brian Pierre-Emmanuel",
    author_email="pebrian@outlook.fr",
    description="A api manager for jarvis mining website.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pebbrian/PyApiManager",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=[
        'requests',
    ],
)
