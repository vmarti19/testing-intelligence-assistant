"""
title: IND-FTR-Flash Rate
goal: Verify indicator is working as per requirement when a flash state is active
author: jochoa5
type: Functional
feature: Indicators
function: Generic

start:
    - Normal operation
sequence: |-
    1. Loop for each flash logic applicable
        1. > Set random valid ignition status
        1. Loop for each flash condition for VOPS configuration (if applicable)
            1. > Enable indicator randomly
            1. > Activate indicator with specific condition
            1. ✓ Verify indicator active in correct flash state
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
                    with test.step(f'{indicator.name} {indicator.color} Activate {function}'):
                        for logic_index, logic in enumerate(indicator.logic.select('[?active && !fault]')):
                            test.markdown(f'{function} logical combination {logic_index + 1}')
                            test.assert_(indicator.enable(), fail=f'Indicator {indicator.name} could not be enabled, step aborted')
                            test.markdown('Set random valid ignition status')
                            DUT.ignition(random.choice(indicator.power_mode))
                            test.assert_(indicator.activate(logic), fail=f'Indicator {indicator.name} could not be activated, step aborted')
                            indicator.check(indicator.name, 'active', color=indicator.color, _type='flash', freq=DUT['FLASH_RATES'][''.join(filter(str.isdigit, function))]['frequency'])
                            test.assert_(indicator.deactivate(), fail=f'Indicator {indicator.name} could not be deactivated, step aborted')
                            indicator.check(indicator.name, 'inactive')
                            indicator.disable()
                else:
                    test.markdown(f'Flash rate not applicable for functionality {index + 1} of {indicator.name} ')
