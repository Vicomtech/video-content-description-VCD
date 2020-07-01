import { VCD } from '../vcd.core'

test('some_test', () => {
    let vcd = new VCD();

    // Create an Action
    let uid_action = vcd.addAction("", "Walking", [0, 10]);
        
    expect(vcd.getNumActions()).toBe(1)
    expect(vcd.getFrameIntervals().length).toBe(1)
    expect(vcd.getFrameIntervals()[0]['frame_start']).toBe(0)
    expect(vcd.getFrameIntervals()[0]['frame_end']).toBe(10)
    
    // Extend the time interval
    vcd.updateAction(uid_action, 11);
    expect(vcd.getNumActions()).toBe(1)
    expect(vcd.getFrameIntervals()[0]['frame_start']).toBe(0)
    expect(vcd.getFrameIntervals()[0]['frame_end']).toBe(11)
    expect(vcd.getAction(uid_action)['frame_intervals'][0]['frame_start']).toBe(0)
    expect(vcd.getAction(uid_action)['frame_intervals'][0]['frame_end']).toBe(11)

    console.log(vcd.stringify())
});
