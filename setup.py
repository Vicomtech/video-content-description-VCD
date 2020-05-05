import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vcd",
    version="4.1.0",
    author="Marcos Nieto",
    author_email="mnieto@vicomtech.org",
    description="Video Content Description (VCD) library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Vicomtech/video-content-description-VCD",
	project_urls={
		"VCD project": "https://vcd.vicomtech.org"
	},
    packages=setuptools.find_packages(),
    install_requires=[
        'jsonschema>=3.2',
        'protobuf',
		'numpy'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
		"Topic :: Scientific/Engineering :: Artificial Intelligence"
    ],
    python_requires='>=3.6',
)