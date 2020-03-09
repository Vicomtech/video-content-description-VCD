import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vcd",
    version="4.0.0",
    author="Marcos Nieto",
    author_email="mnieto@vicomtech.org",
    description="Video Content Description (VCD) library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Vicomtech/video-content-description-VCD",
    packages=setuptools.find_packages(),
    install_requires=[
        'json-schema',
        'protobuf'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)