export class VCD4 {
	private data: any = {}
	private schema: any = {}
	
	private lastUID: any = {}
	private objectDataNames: any = {}
	private actionDataNames: any = {}
	
	constructor(vcdFile = "") {
		// Main VCD data
		this.data = { 'vcd': {} };
		this.data['vcd']['frames'] = {};
		this.data['vcd']['version'] = "4.2.0";
		this.data['vcd']['frame_intervals'] = [];

		// Schema information
		this.schema = {};

		// Additional auxiliary structures
		this.lastUID = {};
		this.lastUID['object'] = -1;
		this.lastUID['action'] = -1;
		this.lastUID['event'] = -1;
		this.lastUID['context'] = -1;
		this.lastUID['relation'] = -1;

		this.objectDataNames = {};  // Stores names of ObjectData, e.g. "age", or "width" per Object
		this.actionDataNames = {};  // Stores names of ActionData, e.g. "age", or "width" per Action
	}
	
	printInfo() {
		console.log("This is a VCD4 content\n");
		console.log("\tversion: " + this.data['vcd']['version']);
	}
}