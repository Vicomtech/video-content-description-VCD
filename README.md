# Video Content Description (VCD)

VCD is a metadata format designed to enable the description of scene information, particularly efficient for discrete data series, such as image or point-cloud sequences from sensor data.
Originally, VCD focused on video content data, but has been extended to provide structures to describe, potentially, any type of information of a scene.

VCD is defined as a structure of data, and as such, can be represented as a JSON Schema, or a Google's Protocol Buffer proto file.

The syntax(see ./schema/vcd_schema_json-v4.0.0.json), as a JSON Schema file, contains the full description of the VCD structure.


## Details

More details can be found at the project's website: https://vcd.vicomtech.org

## Install

Using pip:

```
pip install vcd
```

VCD can be also used cloning this repository. And adding the files to a location the Python environment recognizes.

## Usage

VCD Python API exposes functions to load, create, manipulate and serialize VCD content. Samples and use cases can be found in the test folder( see ./tests/).

As a basic example, VCD can be used in a Python script as follows:

```python
import vcd.core as core
import vcd.types as types

# Create a VCD instance
myVCD = core.vcd()

# Add Objects, Actions, etc.
uid = myVCD.add_object(name='someName', type='#Pedestrian')

...

# Serialize
myVCD.stringify(pretty=False, validation=True)
```

The API contains useful functions that ensures the produced content is compliant with the syntax. Nevertheless, the VCD class allows the user to access directly the content, in the form of a Python dictionary.

```python
import vcd.core as core
import vcd.types as types

# Load a VCD file
myVCD = core.vcd('./tests/etc/vcd400_semantics_fw.json')

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


## Versions

VCD is defined as a syntax, and as such, different versions imply differences in the syntax or data structure. In addition, each version has a dedicated library version compatible with it.

Last version is VCD 4.0.0.

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
    * Python library
    * Element and Frame-wise mode simultaneously
    * Multi-sensor and multi-interval
    * Native Python JSON serialization
    * Google's Protocol Buffer serialization
    * Object data 'num' for single numbers, 'vec' for arrays of numbers

## Related projects

VCD has been used in the following projects: Cloud-LSVA, VI-DAS, inLane, P-REACT, EWISA, Viulib, begirale, SmaCS, HEADSTART.

## Credits

Vicomtech created VCD in 2013, and since, has maintained VCD syntax and libraries. Developments of VCD were supported and funded by the European Commission (EC) Horizon 2020 programme (project [Cloud-LSVA] (http://cloud-lsva.eu), grant agreement 688099).

VCD was registered at the "Registro territorial de la propiedad intelectual de la comunidad autonoma del Pais Vasco", under number 55-354-17, by the Basque Governement, at 2017/07/07.

Main developers:
* Marcos Nieto - mnieto@vicomtech.org
* Orti Senderos - osenderos@vicomtech.org

Contributors:
Thanks to Peter Leskovsky, Mikel Garcia, Gonzalo Pierola, Stefano Masneri, Lorena Garcia and many others in Vicomtech. 

## License

Copyright (c) 2020 Vicomtech

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
