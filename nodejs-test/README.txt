This project aims to test the NPM package created for VCD.
So this project is not packaged itself as an NPM package, but rather it is assumed to be executed with the Node.js runtime environment.

1.- Node.js needs to be installed (https://nodejs.org/en/download/)

2.- Check typescript is installed
npm install -g typescript
tsc --version

3.- Compile the VCD package if not done already:
cd ../nodejs
npm run build

4.- Load local NPM package (note the VCD package is under folder 'nodejs'). Make sure you have compiled the VCD package before:
cd ../nodejs-test
npm install --save-dev ..\nodejs

3.- Compile (creates a vcd-tester.js)
npm run build 

5.- Run script calling Node.js
node vcd-tester.js
