"""
title: IND-NET-Never Received
goal: Verify feature activates or deactivates to input conditions that include a never received state
author: jochoa5
type: Functional
feature: Indicators
function: Generic

start:
    - Normal operation
sequence: |-
    1. Loop for each never received condition of the icon
        1. > Set random valid ignition status
        1. > Enable indicator randomly
        1. > Set indicator to any status different from expected at never received
        1. > Set indicator to never received state
        1. ✓ Verify indicator in active or inactive state as per requirements
        1. > Disable indicator randomly

options:
    cycles: 1
    coverage: 1
    indicators: []
"""
import random

from prj import Indicator
from track import Test

with Test() as test:

    DUT = test.DUT
    DUT.normal_operation()

    @test.cycle
    def block():
        for indicator in Indicator.items():
            for index, function in enumerate(indicator.inputs_process):
                indicator.process(function)
                if function and 'Flash' in function:
                    continue
                with test.step(f'{indicator.name} {indicator.color} Never Received case: {index + 1}'):
                    for _input in indicator.logic.select('[?fault && input[?nreceived]]'):
                        test.markdown('Set random valid ignition status')
                        DUT.ignition(random.choice(indicator.power_mode))
                        test.assert_(indicator.enable(), fail=f'Indicator {indicator.name} could not be enabled, step aborted')
                        indicator.never_received(_input)
                        indicator.disable()
