"""
title: IND-FTR-Warning Process Mask
goal: Verify indicator is not displayed during the warning mask time
author: johcoa5
type: Functional
feature: Indicators
function: Generic

start:
    - Normal operation
sequence: |-
    1. > Enable indicator randomly (if applicable)
    1. > Activate indicator randomly
    1. Loop for each allowed power mode for warning process mask
        1. > Set a valid ignition transition from Off to allowed power mode
        1. ✓ Verify indicator in active or inactive state as per requirements
        1. ✓ Verify indicator in active state after warning process mask time if mask applies
        1. > Set a valid ignition transition from Acc to allowed power mode
        1. ✓ Verify indicator in active or inactive state as per requirements
        1. ✓ Verify indicator in active state after warning process mask time if mask applies
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
                if indicator.warning_process_mask:
                    with test.step(f'{indicator.name} {indicator.color} warning process mask test case: {index + 1}'):
                        test.assert_(indicator.enable(), fail=f'Indicator {indicator.name} could not be enabled, step aborted')
                        test.assert_(indicator.activate(), fail=f'Indicator {indicator.name} could not be activated, step aborted')
                        for from_ignition in indicator.off_states:
                            for to_ignition in indicator.proveout_mask_allowed_ignition:
                                test.markdown(f'Set ignition transition from {from_ignition} to {to_ignition}')
                                DUT.ignition_cycle(from_ignition, to_ignition, IgnitionType.fast)
                                indicator.check(indicator.name, ['inactive', 'active'], time=DUT[indicator.warning_process_mask], color=indicator.color)
                        indicator.deactivate()
                        indicator.disable()
                else:
                    with test.step(f'{indicator.name} {indicator.color} warning process mask negative test case: {index + 1}'):
                        test.assert_(indicator.enable(), fail=f'Indicator {indicator.name} could not be enabled, step aborted')
                        test.assert_(indicator.activate(), fail=f'Indicator {indicator.name} could not be activated, step aborted')
                        for from_ignition in indicator.off_states:
                            for to_ignition in indicator.proveout_mask_allowed_ignition:
                                test.markdown(f'Set ignition transition from {from_ignition} to {to_ignition}')
                                DUT.ignition_cycle(from_ignition, to_ignition, IgnitionType.fast)
                                indicator.check(indicator.name, 'active', color=indicator.color)
                        indicator.deactivate()
                        indicator.disable()
