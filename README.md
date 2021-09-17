![VCD Video Content Description](https://github.com/Vicomtech/video-content-description-VCD/blob/master/doc/logo/VCD_logo_2020.png?raw=true)
# Video Content Description (VCD)

VCD is a metadata format designed to enable the description of scene information, particularly efficient for discrete data series, such as image or point-cloud sequences from sensor data.
Originally, VCD focused on video content data, but has been extended to provide structures to describe, potentially, any type of information of a scene.

VCD is defined as a structure of data, and as such, can be represented as a JSON Schema, or a Google's Protocol Buffer proto file.

The syntax(see [openlabel_schema_json-v1.0.0.json](https://github.com/Vicomtech/video-content-description-VCD/blob/master/schema/openlabel_schema_json-v1.0.0.json)), as a JSON Schema file, contains the full description of the VCD structure. This schema follows the ASAM OpenLABEL standard.

![VCD](https://github.com/Vicomtech/video-content-description-VCD/blob/master/doc/logo/image.svg?raw=true)

## Details

More details can be found at the project's website: https://vcd.vicomtech.org

## Install

### Python

Using pip (Python >3.6)):

```
pip install vcd
```

VCD can be also used cloning this repository. And adding the files to a location the Python environment recognizes.
You can also use the provided [setup.py](https://github.com/Vicomtech/video-content-description-VCD/blob/master/setup.py) file to install if from the source:

```
pip uninstall vcd
python setup.py build
python setup.py install
```

To install previous versions of vcd, you can specify it via pip:

```
pip install vcd==4.3.1
```

NOTE: VCD version 4.3.1 requires Python 3.8.

### Typescript

NPM packages can be used

```
npm install vcd-ts
```

## Usage

### Python

VCD Python API exposes functions to load, create, manipulate and serialize VCD content. 

The recommended way to learn VCD is throuhg the samples at the [test folder](https://github.com/Vicomtech/video-content-description-VCD/blob/master/tests).

As a basic example, VCD can be used in a Python script as follows:

```python
import vcd.core as core
import vcd.types as types

# Create a VCD instance
myVCD = core.VCD()

# Add Objects, Actions, etc.
uid1 = myVCD.add_object(name='ped1', semantic_type='#Pedestrian')
myVCD.add_object_data(uid=uid1, object_data=types.bbox(name="head", val=[0, 0, 100, 200]))

...

# Serialize
myVCD.stringify(pretty=False, validation=True)
```

The API contains useful functions that ensures the produced content is compliant with the syntax. Nevertheless, the VCD class allows the user to access directly the content, in the form of a Python dictionary.

```python
import vcd.core as core

# Load a VCD file
myVCD = core.vcd('./tests/etc/openlabel100_test_scene_KITTI_Tracking_3.json')

# Access data directly
metadata = myVCD.data['vcd']['metadata']

# Modify data directly
myVCD['vcd']['objects'][3]['type'] = "#Car"
...

# Serialize
stringified_vcd = myVCD.stringify(pretty=False, validation=True)
``` 

This can be useful some times, but it is not recommended, as the dictionary may deviate from a valid VCD syntax. To check if a content is valid, the API exposes a validation function:

```python
# Validate
myVCD.validate(stringified_vcd)
``` 

This validation function is optionally called when saving to JSON files.

### Typescript

The Typescript API follows entirely the Python API, and thus [core.py](https://github.com/Vicomtech/video-content-description-VCD/blob/master/vcd/core.py) and [vcd.core.ts](https://github.com/Vicomtech/video-content-description-VCD/blob/master/nodejs/src/vcd.core.ts) are mostly equivalent.
The testing scripts in Typescript and in Python use the same base JSON files.

See examples in [nodejs/src/\__tests\__](https://github.com/Vicomtech/video-content-description-VCD/blob/master/nodejs/src/__tests__)

## Versions

VCD is a toolkit with APIs in various programming languages (Python, Typescript, C++) which allows anyone to create, read, update and delete labels that follow the ASAM OpenLABEL standard v1.0.0. 

Last version is VCD 5.0.0 compliant with OpenLABEL 1.0.0.

Main changes at VCD 5.0.0 from VCD 4.3.1:
* VCD schema is now OpenLABEL schema 1.0.0
* Added support for scenario tagging
* Improved performance
* Addition of C++ API (lite version)
* Enhanced support for Quaternions

Main changes at VCD 4.3.1 from VCD 4.3.0:
* Bug fixing (npm package)
* Multi-value attributes (vec of strings)
* Additional properties true for all attributes
* Customizable intrinsics

Main changes at VCD 4.3.0 from VCD 4.2.0 are:
* Integrated SCL (Scene Configuration Library) into VCD
* Automatic drawing functions for multi-sensor set-ups (e.g. topview)
* Improved API functions for offline VCD edition
* Added Typescript API for web applications
* Common set of test files for Python and Typescript APIs
* Simplified Relations construction
* Preliminar work on Ontology connection with Neo4j

Main changes at VCD 4.2.1 from VCD 4.1.0 are:
* Improved Frame-message creation
* Enhanced API for adding Relations and RDFs
* Added examples for semantic labeling
* General bug fixing and better frame interval management

Main changes at VCD 4.1.0 from VCD 4.0.0 are:
* Enhanced JSON schema self-documentation
* Explicit definition of timestamping and sync information
* Explicit definition of intrinsics parameters for cameras
* Explicit definition of extrinsics parameters for stream (as 4x4 pose matrices)
* Explicit definition of odometry entries
* Reviewed samples and converters

Main changes at VCD 4.0.0 from VCD 3.3.0 are:
* Python API
* Mixed-mode instead of Element-wise or Frame-wise mode: 'Objects', 'Actions', contain the static data, while 'Frames' contain the dynamic part with pointers to the static data
* Elements can contain multiple frameIntervals, instead of just one. This allows to manage "gaps".
* The API has been simplified, and only VCD objects can be created
* The concept of ObjectDataContainer has disappeared, now all information is within "ObjectData" structures
* Frames are listed in the JSON as a dict(), not as an array. Keys are the frame nums.
* Elements are listed in the JSON as a dict(), not as an array. Keys are the uid of elements.
* Timestamp information is now optional for the user, who can insert it as frameProperties (along with intrinsics)
* Relations are timeless: are completely defined by the rdf.subjects and rdf.objects
* All fields in JSON are lowercase, e.g. 'vcd', 'objects'.
* Stringify_frame can be executed to create messages asking for dynamic-only or full (static plus dynamic) information
 
VCD has evolved as follows:

* VCD 1.0 (2013)
* VCD 2.0 (2014)
    * Integrated into Viulib library (module viulib_evaluation)
    * Element-wise and Frame-wise modes
    * XML and JSON serialization via ASL library
* VCD 3.0 (2018)
    * Independent C++ library
    * Element-wise and Frame-wise modes
    * Multi-sensor support
    * JSON serialization via ASL library
    * Pixel-wise loss-less compression modes
    * Comparison routines
* VCD 4.0 (2019)
    * Python API
    * Element and Frame-wise mode simultaneously
    * Multi-sensor and multi-interval
    * Native Python JSON serialization
    * Google's Protocol Buffer serialization
    * Object data 'num' for single numbers, 'vec' for arrays of numbers
* VCD 4.1-3 (2020-2021)
    * Explicit definition of intrinsics, extrinsics and odometry
    * Enhanced timestamping and sync information
    * Enhanced semantics management (RDF triplets)
    * Integrated SCL and complex calibration set-ups
    * Drawing functions
    * Preliminar work on Ontology and Neo4j connection
    * Multi-value attributes ('vec' of strings)
    * Typescript API
    * NPM and Pypi packages
* VCD 5.0.0 (2021)
    * VCD as toolkit to produce OpenLABEL compliant labels
    * Addition of C++ lite version
    * General improvements and consistency (Python, Typescript)


## Related projects

VCD has been used in the following projects: Cloud-LSVA, VI-DAS, inLane, P-REACT, EWISA, Viulib, begirale, SmaCS, HEADSTART, ACCURATE.

If your project also uses VCD, let us know!

## OpenLABEL

Along with the development of VCD, we are participating in the definition of the incoming labeling standard for the automotive sector: ASAM OpenLABEL.

https://www.asam.net/project-detail/asam-openlabel-v100

VCD 5.0.0 is shaped to be compliant with the format defined in OpenLABEL v1.0.0.
VCD is the first labeling toolset compliant with the standard and used during the ellaboration of the standard to produce samples and create the JSON schema.

## Credits

Vicomtech created VCD in 2013, and since, has maintained VCD syntax and libraries. Developments of VCD were supported and funded by the European Commission (EC) Horizon 2020 programme (project [Cloud-LSVA] (http://cloud-lsva.eu), grant agreement 688099).

VCD was registered at the "Registro territorial de la propiedad intelectual de la comunidad autonoma del Pais Vasco", under number 55-354-17, by the Basque Governement, at 2017/07/07.

Main developers:
* Marcos Nieto - mnieto@vicomtech.org
* Orti Senderos - osenderos@vicomtech.org
* Jon Goenetxea - jgoenetxea@vicomtech.org

Contributors:
Thanks to Andoni Mujika, Paola Cañas, Eider Irigoyen, Juan Diego Ortega, Peter Leskovsky, Mikel Garcia, Gonzalo Pierola, Stefano Masneri, Lorena Garcia, Itziar Urbieta and many others in Vicomtech.

Also thanks to Nicola Croce (Deepen.ai), Jason Zhang (Warwick University), Tim Raedsch (Understand.ai) and other colleagues in ASAM for their ideas and comments during the ellaboration of the OpenLABEL v1.0.0 standard.

Finally, special thanks to Oihana Otaegui, as head of the ITS & Engineering department in Vicomtech. Without her lead this project would have never been possible. She believed in the VCD idea and supported me to carry on. Thanks Oihana! ; )


## License

Copyright (c) 2021 Vicomtech

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Citation

Part of the work carried out to make VCD a reality has been published in Elsevier SoftwareX journal. If you find VCD useful and want to cite it in your publications, please use the following citation (the paper pdf can be accessed [here](https://www.sciencedirect.com/science/article/pii/S2352711020303666)).

M. Nieto, O. Senderos, and O. Otaegui, "Boosting AI applications: Labeling format for complex datasets," SoftwareX, 2021, p. 100653, vol. 13 (https://doi.org/10.1016/j.softx.2020.100653).
