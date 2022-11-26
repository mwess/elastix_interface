import logging
import subprocess

SUCCESS = 0

class Cmd():

    fixed_image_path: str
    moving_image_path: str
    output_directory: str
    parameter_file_path: str

    def __init__(self):
        pass


    def build_command(self):
        command = ['elastix']
        command += ['-f', self.fixed_image_path]
        command += ['-m', self.moving_image_path]
        command += ['-p', self.parameter_file_path]
        command += ['-out', self.output_directory]
        return command

    def execute_command(self):
        command = self.build_command()
        ret = subprocess.run(command, capture_output=True) # pylint: disable=subprocess-run-check
        if ret.returncode == SUCCESS:
            logging.info(ret.stdout)
            result_str_ = f'Sync request {self.index} successful.'
            self.rsync_success = True
        else:
            logging.info(ret.stderr)
            result_str_ = f'Sync reqiest {self.index} failed.'
        logging.info(result_str_)
        return self.rsync_success


