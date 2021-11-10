"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const vcd_ts_1 = require("vcd-ts");
const openlabel100_test_create_search_mid_json_1 = __importDefault(require("../tests/etc/openlabel100_test_create_search_mid.json"));
let message = "=====================\nTesting NPM package vcd-ts\n======================";
console.log(message);
// Create VCD object from json content
let myVCD = new vcd_ts_1.VCD(openlabel100_test_create_search_mid_json_1.default, true);
console.log(myVCD.stringify(false, false));
