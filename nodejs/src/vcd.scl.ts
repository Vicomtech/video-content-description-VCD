/**
VCD (Video Content Description) library v5.0.1

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a library to create and manage VCD content version 5.0.1.
VCD is distributed under MIT License. See LICENSE.

*/

import internal from "stream";


class Sensor {
    name: string;
    description: string;
    uri: string;
    type: string;
    properties: object;
    constructor(name: string, description: string, uri: string, properties: object) {
        this.name = name;
        this.description = description;
        this.uri = uri;
        this.type = this.constructor.name;  // TODO: check name of class (other option is Sensor.name)
        this.properties = properties;
    }

    public isCamera(): boolean {
        if(this.type == "CameraPinhole" || this.type == "CameraFisheye" || this.type == "CameraEquirectangular")
            return true;
        return false;
    }

    public isLidar(): boolean {
        if(this.type == "Lidar")
            return true;
        return false;
    }
}

class Camera extends Sensor {
    width: number;
    height: number;

    
}