import pathlib
from setuptools import setup

# pip install twine
# pip install wheel
# python setup.py sdist bdist_wheel
# twine check dist/*
# pip install --upgrade begs

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="grintor-hooks",
    version="0.0.1",
    description="Some pre-commit hooks",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/grintor/grintor-hooks",
    author="Chris Wheeler",
    author_email="grintor@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    entry_points={
            'console_scripts': [
                    'detect_aws_secrets=grintor_hooks.detect_aws_secrets:main',
            ]
    },
    include_package_data=False,
    packages=["grintor_hooks"],
    install_requires=[],
)