"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const vcd_ts_1 = require("vcd-ts");
const vcd430_test_create_search_mid_json_1 = __importDefault(require("../tests/etc/vcd430_test_create_search_mid.json"));
let message = "Testing NPM package vcd-ts";
console.log(message);
let myVCD = new vcd_ts_1.VCD(vcd430_test_create_search_mid_json_1.default, true);
console.log(myVCD.stringify(false, false));
