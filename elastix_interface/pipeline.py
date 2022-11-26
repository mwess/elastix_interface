from dataclasses import dataclass
import logging
import os
import shutil
from typing import List, Union

from cmd import Cmd

@dataclass
class Pipeline():

    fixed_image_path: str
    moving_image_path: str
    output_directory: str
    parameter_file_path: str
    use_existing_file: bool = True
    parameter_chain: List[str] = []

    def __init__(self):
        pass

    def add_parameter_block(self, parameter_block: Union[str, List[str]]):
        if self.parameter_chain is None:
            self.parameter_chain = []
        if isinstance(parameter_block, str):
            self.parameter_chain.append([parameter_block])
        else:
            self.parameter_chain += parameter_block

    def add_headline(self, headline: str):
        self.parameter_chain.add_headline(headline)

    def add_parameter(self, parameter:str):
        self.parameter_chain[-1].add_parameter(parameter)

    def parse_parameter_block(self, parameter_block: str):
        pm_block = ParameterBlock.parse_multiline_string(parameter_block)
        self.parameter_chain.append(pm_block)
    
    def new_building_block(self):
        self.parameter_chain.append(ParameterBlock())

    def __backup_file(self, filename):
        backup_filename = self.__get_backup_filename(filename)
        shutil.move(filename, backup_filename)

    def __get_backup_filename(self, filename, backup_suffix='bck'):
        """
        Builds the filename for the backup. Has the format: param_filenamea_{number}.bck
        """
        curr_idx = 0
        fname = None
        while True:
            fname = f'{filename}_{curr_idx}.{backup_suffix}'
            if not os.path.exists(fname):
                return fname
            else:
                curr_idx += 1

    def write_parameter_file(self, overwrite=True):
        if os.path.exists(self.parameter_file_path):
            logging.warn(f'File {self.parameter_file_path} already exists.')
            if not overwrite:
                self.__backup_file(self.parameter_file_path)
        with open(self.parameter_file_path, 'w') as f:
            f.write(str(self.parameter_chain))

    def execute_pipeline(self):
        self.write_parameter_file()
        cmd = Cmd(self.fixed_image_path,
                self.moving_image_path,
                self.output_directory,
                self.parameter_file_path)
        ret = cmd.execute_command()
        return ret
    
        
class ParameterBlock:

    headline: str
    parameters: List[str]

    def __init__(self, headline: Union[None, str] = None, parameters: List[str]=None):
        if isinstance(headline, str):
            self.headline = self.format_headline(headline)
        if isinstance(parameters, list):
            self.parameters = self.format_parameters(parameters)
        
    def format_headline(self, headline: str):
        """
        Enforces that the headline string is a comment.
        """
        if not headline.startswith('//'):
            headline = '// ' + headline
        return headline

    def format_parameters(self, parameters: List[str]):
        """
        Enforces the format for commands in an elastix parameter file.
        """
        formated_parameters = []
        for line in parameters:
            formated_parameters.append(self.format_parameter(line))
        return formated_parameters
    
    def format_parameter(self, parameter: str):
        if not parameter.startswith('('):
            parameter = '(' + parameter
        if not parameter.endswith(')'):
            parameter = parameter + ')'
        return parameter

    def add_parameter(self, parameter: str):
        self.parameters.append(self.format_parameter(parameter))

    def add_headline(self, headline: str):
        self.headline = self.format_headline(headline)

    def __str__(self):
        out = self.headline + '\n'
        out += '\n'.join(self.parameters)
        return out

    @classmethod
    def parse_multiline_string(cls, mls):
        lines = [x.strip() for x in mls.split('\n') if len(x) > 0]
        if lines[0].startswith('//'):
            headline = lines[0]
            parameters = lines[1:]
        else:
            headline = None
            parameters = lines
        return cls(headline=headline, parameters=parameters)