"""
title: IND-FTR-Low Voltage
goal: Verify indicator activates or deactivates as per requirement under high voltage conditions and its recovery
author: jochoa5
type: Functional
feature: Indicators
function: Generic

start:
    - Normal operation
sequence: |-
    1. Loop for each LVSD logic applicable
        1. > Set random valid ignition status
        1. > Enable indicator randomly
        1. > Activate indicator randomly
        1. > Set the applicable low voltage flag
        1. ✓ Verify indicator in inactive state
        1. > Return to nominal voltage
        1. ✓ Verify indicator in active state
        1. > Deactivate indicator randomly
        1. > Disable indicator randomly

options:
    cycles: 1
    coverage: 1
    indicators: []
"""
import random

from prj import Indicator
from track import Test

with Test() as test:  # noqa: PLR1702

    DUT = test.DUT
    DUT.normal_operation()

    @test.cycle
    def block():
        for indicator in Indicator.items():
            for index, function in enumerate(indicator.inputs_process):
                indicator.process(function)
                if function and 'Flash' in function:
                    continue
                with test.step(f'{indicator.name} {indicator.color} Check the Low Voltage flag case: {index + 1}'):
                    for voltage_flag in indicator.volts:
                        if voltage_flag and 'LV' in voltage_flag:
                            test.assert_(indicator.enable(), fail=f'Indicator {indicator.name} could not be enabled, step aborted')
                            test.markdown('Set random valid ignition status')
                            DUT.ignition(random.choice(indicator.power_mode))
                            test.assert_(indicator.activate(), fail=f'Indicator {indicator.name} could not be activated, step aborted')
                            test.markdown('Set the applicable low voltage flag')
                            DUT.power_supply.flag(voltage_flag)
                            indicator.check(indicator.name, 'inactive', color=indicator.color)
                            test.step('Return to low voltage recovery threshold')
                            DUT.power_supply.flag(voltage_flag, 'recovery')
                            indicator.check(indicator.name, 'active', color=indicator.color)
                            indicator.deactivate()
                            indicator.disable()
                        else:
                            test.markdown(f'Low voltage flag is not applicable for indicator {indicator.name}')
