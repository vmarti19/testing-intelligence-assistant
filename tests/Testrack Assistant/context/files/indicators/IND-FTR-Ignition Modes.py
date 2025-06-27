"""
title: IND-FTR-Ignition Modes
goal: Verify indicator only activates in valid ignition modes
author: jochoa5
type: Functional
feature: Indicators
function: Generic

start:
    - Normal operation
sequence: |-
    1. Loop for each logic of the indicator
        1. > Enable indicator randomly
        1. > Activate indicator randomly
        1. Loop for set ignition status
            1. ✓ Verify indicator in active state if ignition mode is applicable, inactive if power mode is not applicable
            1. > Set ignition to RUN state
        1. > Deactivate indicator randomly
        1. > Disable indicator randomly

options:
    cycles: 1
    coverage: 1
    indicators: []
"""

from prj import Ignition, IgnitionType, Indicator
from track import Test, Time

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
                with test.step(f'{indicator.name} {indicator.color} case: {index + 1}'):
                    test.assert_(indicator.enable(), fail=f'Indicator {indicator.name} could not be enabled, step aborted')
                    test.assert_(indicator.activate(), fail=f'Indicator {indicator.name} could not be activated, step aborted')
                    for ignition in Ignition:
                        test.markdown(f'Ignition status: {ignition.name.title()}')
                        DUT.ignition_cycle('Off', ignition, IgnitionType.no_wait) if ignition.name.title() == 'Start' else DUT.ignition(ignition)
                        if ignition.name.title() in indicator.power_mode:
                            if (ignition.name.title() == 'Start') and indicator.warning_process_mask is not None:
                                Time.wait(DUT[indicator.warning_process_mask], 'Warning process Mask')
                            indicator.check(indicator.name, 'active', color=indicator.color)
                        else:
                            indicator.check(indicator.name, 'inactive')
                        test.markdown('Set ignition to RUN state')
                        DUT.ignition('run')
                    indicator.deactivate()
                    indicator.disable()
