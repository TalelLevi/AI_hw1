import os
from typing import *
from dataclasses import dataclass

from framework import *


__all__ = [
    'ApartmentWithSymptomsReport', 'Ambulance', 'Laboratory', 'MDAProblemInput'
]


@dataclass(frozen=True)
class ApartmentWithSymptomsReport(Serializable):
    report_id: int
    reporter_name: str
    location: Junction
    nr_roommates: int

    def __repr__(self):
        return f'{self.reporter_name} ({self.nr_roommates})'

    def __hash__(self):
        return hash((self.report_id, self.location, self.nr_roommates))

    def __eq__(self, other):
        if not isinstance(other, ApartmentWithSymptomsReport):
            return False
        return self.report_id == other.report_id and \
               self.location == other.location and \
               self.nr_roommates == other.nr_roommates


@dataclass(frozen=True)
class Ambulance(Serializable):
    initial_nr_matoshim: int
    taken_tests_storage_capacity: int
    initial_location: Junction

    def __hash__(self):
        return hash((self.taken_tests_storage_capacity, self.initial_location))

    def __eq__(self, other):
        if not isinstance(other, Ambulance):
            return False
        return self.taken_tests_storage_capacity == other.taken_tests_storage_capacity and self.initial_location == other.initial_location


@dataclass(frozen=True)
class Laboratory(Serializable):
    lab_id: int
    name: str
    max_nr_matoshim: int
    location: Junction

    def __hash__(self):
        return hash((self.lab_id, self.max_nr_matoshim, self.location))

    def __eq__(self, other):
        if not isinstance(other, Laboratory):
            return False
        return self.lab_id == other.lab_id and self.max_nr_matoshim == other.max_nr_matoshim and \
               self.location == other.location


@dataclass(frozen=True)
class MDAProblemInput:
    input_name: str
    reported_apartments: Tuple[ApartmentWithSymptomsReport, ...]
    ambulance: Ambulance
    laboratories: Tuple[Laboratory, ...]

    @classmethod
    def load_from_file(cls, input_file_name: str, streets_map: StreetsMap) -> 'MDAProblemInput':
        """
        Loads and parses a MDA-problem-input from a file. Usage example:
        >>> problem_input = MDAProblemInput.load_from_file('big_MDA.in', streets_map)
        """

        with open(Consts.get_data_file_path(input_file_name), 'r') as input_file:
            input_type = input_file.readline().strip()
            if input_type != cls.__name__:
                raise ValueError(f'Input file `{input_file_name}` is not a valid {cls.__name__}.')
            try:
                input_name = input_file.readline().strip()
                reported_apartments = tuple(
                    ApartmentWithSymptomsReport.deserialize(serialized_reported_apartment, streets_map=streets_map)
                    for serialized_reported_apartment in input_file.readline().rstrip('\n').split(';'))
                ambulance = Ambulance.deserialize(input_file.readline().rstrip('\n'), streets_map=streets_map)
                laboratories = tuple(
                    Laboratory.deserialize(ser_lab, streets_map=streets_map)
                    for ser_lab in input_file.readline().rstrip('\n').split(';'))
            except:
                raise ValueError(f'Invalid input file `{input_file_name}`.')
        return MDAProblemInput(
            input_name=input_name, reported_apartments=reported_apartments,
            ambulance=ambulance, laboratories=laboratories)

    def store_to_file(self, input_file_name: str):
        with open(Consts.get_data_file_path(input_file_name), 'w') as input_file:
            lines = [
                self.__class__.__name__,
                str(self.input_name.strip()),
                ';'.join(reported_apartment.serialize() for reported_apartment in self.reported_apartments),
                self.ambulance.serialize(),
                ';'.join(laboratory.serialize() for laboratory in self.laboratories),
            ]
            for line in lines:
                input_file.write(line + '\n')

    @staticmethod
    def load_all_inputs(streets_map: StreetsMap) -> Dict[str, 'MDAProblemInput']:
        """
        Loads all the inputs in the inputs directory.
        :return: list of inputs.
        """
        inputs = {}
        input_file_names = [f for f in os.listdir(Consts.DATA_PATH)
                            if os.path.isfile(os.path.join(Consts.DATA_PATH, f)) and f.split('.')[-1] == 'in']
        for input_file_name in input_file_names:
            try:
                problem_input = MDAProblemInput.load_from_file(input_file_name, streets_map)
                inputs[problem_input.input_name] = problem_input
            except:
                pass
        return inputs
