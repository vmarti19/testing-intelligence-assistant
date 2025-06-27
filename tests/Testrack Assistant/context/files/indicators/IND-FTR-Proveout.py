"""
title: IND-FTR-Proveout
goal: Verify indicator is displayed while proveout bulb check is active
author: johcoa5
type: Functional
feature: Indicators
function: Generic

start:
    - Normal operation
sequence: |-
    1. Loop for each logic condition available
        1. > Enable indicator randomly
        1. > Deactivate indicator randomly
        1. Loop for each allowed power mode for proveout
            1. > Set a valid ignition transition from Off to allowed power mode
            1. ✓ Verify indicator in active or inactive state as per requirements
            1. ✓ Verify indicator in inactive state after bulbcheck time if bulbcheck applies
            1. > Set a valid ignition transition from Acc to allowed power mode
            1. ✓ Verify indicator in active or inactive state as per requirements
            1. ✓ Verify indicator in inactive state after bulbcheck time if bulbcheck applies
        1. > Disable indicator randomly

options:
    cycles: 1
    coverage: 1
    indicators: []
"""

from prj import IgnitionType, Indicator
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
                if indicator.bulbcheck is not None:
                    with test.step(f'{indicator.name} {indicator.color} bulbcheck proveout test case: {index + 1}'):
                        test.assert_(indicator.enable(), fail=f'Indicator {indicator.name} could not be enabled, step aborted')
                        test.assert_(indicator.deactivate(), fail=f'Indicator {indicator.name} could not be deactivated, step aborted')
                        for after_ign in indicator.off_states:
                            for ignition in indicator.proveout_mask_allowed_ignition:
                                test.markdown(f'Set a valid ignition transition from {after_ign} to {ignition}')
                                DUT.ignition_cycle(after_ign, ignition, IgnitionType.fast)
                                indicator.check(indicator.name, ['active', 'inactive'], time=DUT[indicator.bulbcheck], color=indicator.color)
                        indicator.disable()
                else:
                    with test.step(f'{indicator.name} {indicator.color} bulbcheck proveout negative test case: {index + 1}'):
                        test.assert_(indicator.enable(), fail=f'Indicator {indicator.name} could not be enabled, step aborted')
                        test.assert_(indicator.deactivate(), fail=f'Indicator {indicator.name} could not be deactivated, step aborted')
                        for after_ign in indicator.off_states:
                            for ignition in indicator.proveout_mask_allowed_ignition:
                                test.markdown(f'Set a valid ignition transition from {after_ign} to {ignition}')
                                DUT.ignition_cycle(after_ign, ignition, IgnitionType.fast)
                                indicator.check(indicator.name, 'inactive', color=indicator.color)
                        indicator.disable()
