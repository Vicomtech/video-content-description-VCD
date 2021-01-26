import { VCD } from 'vcd-ts'
import vcd430_sample_file from '../tests/etc/vcd430_test_create_search_mid.json'


let message: string = "=====================\nTesting NPM package vcd-ts\n======================"
console.log(message)

// Create VCD object from json content
let myVCD = new VCD(vcd430_sample_file, true)
console.log(myVCD.stringify(false, false))

