"""Indicators module"""

from __future__ import annotations

from typing import ClassVar

import prj as p
import track as l
from loguru import logger
from track.data import pool
from track.vision import Check


class Indicator:
    """Ford telltales/RTTs class"""

    _items: ClassVar[dict[str, Indicator]] = {}
    _vision: Check = None

    @classmethod
    def items(cls) -> list[Indicator]:
        """"Get a list of indicators to be executed"""
        if cls._vision is None:
            cls._vision = Check()
        if not cls._items:
            try:
                with pool.connection() as conn, conn.cursor() as cursor:
                    if not l.test.header.options.indicators:
                        cursor.execute('SELECT name, logic FROM ford_clusters.indicators_stss WHERE variant @> %s;', [[l.DUT.variant]])
                    else:
                        cursor.execute('SELECT name, logic FROM ford_clusters.indicators_stss WHERE variant @> %s AND ARRAY[name] <@ %s;', ([l.DUT.variant], l.test.header.options.indicators))
                    while row := cursor.fetchone():
                        cls._items[row[0]] = Indicator(row[1], row[0])
            except (Exception) as ex:
                logger.error(ex)
        return cls._items.values()

    def __init__(self, data: dict, name: str) -> None:
        """"Initialize an indicator with name and data from feature"""
        self.__dict__ = data
        self.ind_name = name
        self.name, self.value = self._get_name_cfg(data)
        self.volts = self.generic['volt'] if self.generic['volt'] is not None else []
        self.config = p.Logic(self.generic['config']) if self.generic['config'] != 'true' else None
        if self.config.is_error if self.config is not None else False:
            logger.error(f'Error in config json for indicator: {self.name}')
        self.proveout_mask_allowed_ignition = ['Start', 'Run']
        self.off_states = ['Off', 'Acc']
        self._logic_activation = None
        self.inputs_process_logic = {}
        self.inputs_process = self._to_dictionary(self.logic_activation)
        self.signal_list = []

    @property
    def inputs_processing(self) -> dict:
        """"Get indicator logics data"""
        try:
            return self.inputs_process[self._logic_activation]
        except (Exception) as e:
            logger.error('Functions associated to feature {} not found', self.name)
            logger.debug(e)

    @staticmethod
    def _to_dictionary(iterable: object) -> dict:
        """"Return dictionary from indicator activations solid or flash"""
        to_dictionary_ = {}
        for index, item in enumerate(iterable):
            if str(next(iter(to_dictionary_), None)) == item['type']:
                to_dictionary_[item['type'] + str(index)] = item
            else:
                to_dictionary_[item['type']] = item
        return to_dictionary_

    @inputs_processing.setter
    def inputs_processing(self, condition: dict) -> None:
        """"Enable the indicator activation type"""
        self._logic_activation = condition
        self.logic = p.Logic({'logic': self.inputs_processing['logic']['logic'], 'override': self.inputs_processing['logic']['override']})
        if self.logic.is_error:
            logger.error(f'Error in logic json for indicator: {self.name}')

    @property
    def rtt_mode(self) -> str:
        """Return string with the RTT type, solid or flash"""
        return self.inputs_processing['type']

    @property
    def power_mode(self) -> tuple:
        """Return tuple with the available power modes"""
        return self.inputs_processing['pwr']

    @staticmethod
    def _get_name_cfg(data: dict) -> str:
        for indicator in data['indicator']:
            return indicator['name'], indicator['value'] if indicator['value'] is not None else None
        return None

    @staticmethod
    def _get_volts(data: dict) -> tuple[str]:
        for generic in data['generic']:
            return generic['volt']
        return None

    def process(self, input_process: dict | None = None) -> None:
        """Function to obtain dynamic json"""
        if input_process is not None:
            self.inputs_processing = input_process

    def enable(self, condition: dict | None = None) -> bool:
        """Function to enable indicator with random or specific condition"""
        if self.config.is_error if self.config is not None else False:
            logger.error(f'Error in config json for indicator: {self.name}')
        else:
            l.DUT.ignition('run')
            try:
                if self.config is not None:
                    if condition is None:
                        l.test.markdown('Enable indicator randomly')
                        config_response = self.config.set('[?active]')
                    else:
                        l.test.markdown('Enable indicator with specific condition')
                        config_response = self.config.set(condition)
                else:
                    logger.info('Indicator{} is not configurable', self.name)
                    return True
            except (Exception) as e:
                logger.error(e)
                return False
        return not self.config.is_error and config_response

    def disable(self, condition: dict | None = None) -> bool:
        """Function to disable indicator with random or specific condition"""
        if self.config.is_error if self.config is not None else False:
            logger.error(f'Error in config json for indicator: {self.name}')
        else:
            l.DUT.ignition('run')
            try:
                if self.config is not None:
                    if condition is None:
                        l.test.markdown('Disable indicator randomly')
                        config_response = self.config.set('[?!active]')
                    else:
                        l.test.markdown('Disable indicator with specific condition')
                        config_response = self.config.set(condition)
                else:
                    logger.info('Indicator{} is not configurable', self.name)
                    return True
            except (Exception) as e:
                logger.error(e)
                return False
        return not self.config.is_error and config_response

    def activate(self, condition: dict | None = None) -> bool:
        """Function to activate indicator with random or specific condition"""
        if self.logic.is_error:
            logger.error(f'Error in logic json for indicator: {self.name}')
        else:
            try:
                if self.logic is not None:
                    if condition is None:
                        l.test.markdown('Activate indicator randomly')
                        self.logic.set('[?active && !fault]')
                    else:
                        l.test.markdown('Activate indicator with specific condition')
                        self.logic.set(condition)
                else:
                    logger.info('Indicator{} has wrong logic', self.name)
                return True
            except (Exception) as e:
                logger.error(e)
                return False
        return False

    def deactivate(self, condition: dict | None = None) -> bool:
        """Function to deactivate indicator with random or specific conditions"""
        if self.logic.is_error:
            logger.error(f'Error in logic json for indicator: {self.name}')
        else:
            try:
                if condition is None:
                    l.test.markdown('Deactivate indicator randomly')
                    self.logic.set('[?!active && !fault]')
                else:
                    l.test.markdown('Deactivate indicator with specific condition')
                    self.logic.set(condition)
                return True
            except (Exception) as e:
                logger.error(e)
                return False
        return False

    def check(self, ind: str, state: list, _type: str = 'pattern', color: str | None = None, freq: int | None = None, time: int | None = None) -> bool:
        """Execute the vision check to obtain a Pass or Fail"""
        if _type == 'generic':
            obj = self._vision.add(self.ind_name, ind, reaction=800, duration=100, state=state, type=_type)
            self._vision.now(obj)
        elif ',' in ind:
            patterns = ind.split(',')
            for pattern in patterns:
                obj = self._vision.add(self.ind_name, pattern, reaction=300, duration=1000, state=state, type=_type, color=color)
                self._vision.now(obj)
            l.test.markdown(f'Verify indicators in {state} state')
        elif _type == 'pattern':
            if time is not None:
                time_wait = l.Time.stamp()
                time_end = time_wait + time
                start = self._vision.add(self.ind_name, ind, reaction=300, duration=1000, state=state[0], type=_type, color=color)
                end = self._vision.add(self.ind_name, ind, reaction=100, duration=1000, state=state[1], type=_type, color=color)
                self._vision.now(start, stamp=time_wait)
                self._vision.now(end, stamp=time_end)
                l.test.markdown(f'Verify indicator in {state[0]} state and check again in {state[1]} state after {time}ms ')
            else:
                obj = self._vision.add(self.ind_name, ind, reaction=300, duration=1000, state=state, type=_type, color=color)
                self._vision.now(obj)
                l.test.markdown(f'Verify indicator in {state} state')
        elif _type == 'flash':
            obj = self._vision.add(self.ind_name, ind, reaction=800, duration=2000, state=state, type=_type, color=color, frequency=freq)
            self._vision.now(obj)
            l.test.markdown(f'Verify indicator in {state} state')
        return self._vision.execute()

    def missing(self, logic: dict) -> None:
        """Subscribe Indicator signals to handler to check indicator missing and recovery status"""
        msg_list = []

        def handler(event: str, stage: any) -> None:
            if event == 'missing':
                if (logic['active'] is False and stage == 'counter_expired') or (logic['active'] and stage == 'recovery'):
                    self.check(self.name, 'inactive')
                elif (logic['active'] and stage == 'counter_expired') or (logic['active'] is False and stage == 'recovery'):
                    self.check(self.name, 'active', color=self.color)

        for condition in logic['input']:
            signal_ = condition['name']
            p.Signal(signal_).subscribe('missing', handler)
            msg = p.Signal(signal_).message_name
            if msg not in msg_list:
                if logic['active'] is False:
                    self.activate()
                    self.check(self.name, 'active', color=self.color)
                    p.Signal(signal_).stop()
                    self.deactivate()
                else:
                    p.Signal(signal_).stop()
                msg_list.append(msg)

    def invalid(self, logic: dict) -> None:
        """Subscribe indicator signals to handler to check indicator invalid and recovery status"""

        def handler(event: str, stage: any) -> None:
            if event == 'invalid':
                if (logic['active'] and stage == 'recovery') or (logic['active'] is False and stage == 'counter_expired'):
                    self.check(self.name, 'inactive')
                elif (logic['active'] is False and stage == 'recovery') or (logic['active'] and stage == 'counter_expired'):
                    self.check(self.name, 'active', color=self.color)

        for condition in logic['input']:
            signal_ = condition['name']
            if signal_ not in self.signal_list:
                p.Signal(signal_).subscribe('invalid', handler)
                self.signal_list.append(signal_)
            if logic['active'] is False:
                self.activate()
                self.check(self.name, 'active', color=self.color)
                p.Signal(signal_).invalid(item=condition['value'])
                self.deactivate()
            else:
                p.Signal(signal_).invalid(item=condition['value'])

    def never_received(self, logic: dict) -> None:
        """Subscribe indicator signals to handler to check indicator never received and recovery status"""

        def handler(event: str, stage: any) -> None:
            if event == 'nreceived':
                if (logic['active'] is False and stage == 'counter_expired') or (logic['active'] and stage == 'recovery'):
                    self.check(self.name, 'inactive')
                elif (logic['active'] and stage == 'counter_expired') or (logic['active'] is False and stage == 'recovery'):
                    self.check(self.name, 'active', color=self.color)

        msg_list = []
        for condition in logic['input']:
            signal_ = condition['name']
            p.Signal(signal_).subscribe('nreceived', handler)
            msg = p.Signal(signal_).message_name
            if msg not in msg_list:
                if not logic['active']:
                    self.activate()
                    self.check(self.name, 'active', color=self.color)
                    p.Signal(signal_).never_received()
                    self.deactivate()
                else:
                    p.Signal(signal_).never_received()
                msg_list.append(msg)
