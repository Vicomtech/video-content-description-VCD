import { VCD } from 'vcd-ts'
import openlabel100_sample_file from '../tests/etc/openlabel100_test_create_search_mid.json'


let message: string = "=====================\nTesting NPM package vcd-ts\n======================"
console.log(message)

// Create VCD object from json content
let myVCD = new VCD(openlabel100_sample_file, true)
console.log(myVCD.stringify(false, false))

