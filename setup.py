import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Check version
with open(file="vcd.version") as f:
    vcd_version = f.readlines()[0]   # e.g. "5.0.1"    

setuptools.setup(
    name="vcd",
    version=vcd_version,
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
		'numpy>=1.19.0,<1.19.4',
        'opencv-python'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
		"Topic :: Scientific/Engineering :: Artificial Intelligence"
    ],
    python_requires='>=3.6',
)