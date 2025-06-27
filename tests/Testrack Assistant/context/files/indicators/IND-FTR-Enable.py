"""
title: IND-FTR-Enable
goal: Validate logic that transitions the indicator to an active state
author: jochoa5
type: Functional
feature: Indicators
function: Generic

start:
    - Normal operation
sequence: |-
    1. Loop for each logic applicable for enable case
        1. > Set random valid ignition status
        1. > Enable indicator with specific condition
        1. > Activate indicator randomly
        1. ✓ Verify indicator in active state
        1. > Deactivate indicator randomly
        1. ✓ Verify indicator in inactive state
    1. Loop for each logic applicable for activate case
        1. > Set random valid ignition status
        1. > Enable indicator randomly
        1. > Activate indicator with specific condition
        1. ✓ Verify indicator in active state
        1. > Deactivate indicator randomly
        1. ✓ Verify indicator in inactive state
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
                with test.step(f'{indicator.name} {indicator.color} Enable case: {index + 1}'):
                    if indicator.config is not None:
                        for config in indicator.config.select('[?active]'):
                            test.assert_(indicator.enable(config), fail=f'Indicator {indicator.name} could not be enabled, enable step aborted')
                            test.markdown('Set random valid ignition status')
                            DUT.ignition(random.choice(indicator.power_mode))
                            test.assert_(indicator.activate(), fail=f'Indicator {indicator.name} could not be activated, enable step aborted')
                            indicator.check(indicator.name, 'active', color=indicator.color)
                            test.assert_(indicator.deactivate(), fail=f'Indicator {indicator.name} could not be deactivated, enable step aborted')
                            indicator.check(indicator.name, 'inactive')
                    else:
                        test.markdown(f'indicator {indicator.name} is not configurable')

                with test.step(f'{indicator.name} {indicator.color} Activate case: {index + 1}'):
                    for logic in indicator.logic.select('[?active && !fault]'):
                        test.assert_(indicator.enable(), fail='Indicator could not be enabled, activate step aborted')
                        test.markdown('Set random valid ignition status')
                        DUT.ignition(random.choice(indicator.power_mode))
                        test.assert_(indicator.activate(logic), fail=f'Indicator {indicator.name} could not be activated, activate step aborted')
                        indicator.check(indicator.name, 'active', color=indicator.color)
                        test.assert_(indicator.deactivate(), fail=f'Indicator {indicator.name} could not be deactivated, activate step aborted')
                        indicator.check(indicator.name, 'inactive')
                    indicator.disable()
