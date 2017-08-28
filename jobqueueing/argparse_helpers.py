"""
Helpers for setting up argument parsing for jobqueueing
"""
import os
from argparse import ArgumentTypeError
import re

from dateutil import parser as dateparser

from jobqueueing import gcq_statuses


log_level_choices = 'NOTSET DEBUG INFO WARNING ERROR CRITICAL'.split()


def strtobool(string):
    return string.lower() in {'true', 't', 'yes', '1'}


def walltime(string):
    if not re.match(r'(\d{1,2}:)?(\d{2}:)*\d{2}', string):
        raise ArgumentTypeError("'{}' is not a valid walltime value")
    return string


def add_global_arguments(parser):
    group = parser.add_argument_group('Global arguments')
    JQ_DATABASE = os.environ.get('JQ_DATABASE', None)
    group.add_argument(
        '-d', '--database',
        required=not bool(JQ_DATABASE),
        default=JQ_DATABASE,
        help='Filepath to queue management database.'
             'Defaults to value of environment variable JQ_DATABASE. '
             'You must either define the env var or set the value of this '
             'option in the command line.',
    )
    group.add_argument(
        '-L', '--loglevel', help='Logging level',
                       choices=log_level_choices, default='INFO')
    return group


def add_gcadd_arguments(parser):
    group = parser.add_argument_group('Add arguments')
    group.add_argument(
        '-f', '--force', action='store_true',
        help='Force addition of a new queue entry even if one for this '
             'input filename already exists')
    return group


def add_execution_environment_arguments(parser, required=True):
    group = parser.add_argument_group('Execution environment arguments')
    JQ_PY_VENV = os.environ.get('JQ_PY_VENV', None)
    group.add_argument(
        '-P', '--py-venv', dest='py_venv',
        required=required and not bool(JQ_PY_VENV),
        default=JQ_PY_VENV,
        help='Path to Python virtual env containing scripts. ' +
             ('Defaults to value of environment variable JQ_PY_VENV. '
             'You must either define the env var or set the value of this '
             'option in the command line.' if required else '')
    )
    return group


def add_generate_climos_arguments(parser, o_required=True, flag_default=True):
    group = parser.add_argument_group('generate_climos arguments')
    group.add_argument(
        'input_filepath', help='File to queue')
    group.add_argument(
        '-o', '--output-directory',
        required=o_required, dest='output_directory',
        help='Path to directory where output files will be placed')
    group.add_argument(
        '-g', '--convert-longitudes', type=strtobool,
        dest='convert_longitudes', default=flag_default,
        help='Transform longitude range from [0, 360) to [-180, 180)')
    group.add_argument(
        '-v', '--split-vars', type=strtobool,
        dest='split_vars', default=flag_default,
        help='Generate a separate file for each dependent variable in the file')
    group.add_argument(
        '-i', '--split-intervals', type=strtobool,
        dest='split_intervals', default=flag_default,
        help='Generate a separate file for each climatological period')
    return group


def add_pbs_arguments(parser, ppn_default=1, walltime_default='10:00:00'):
    group = parser.add_argument_group('PBS arguments')
    group.add_argument(
        '-p', '--ppn', type=int,
        dest='ppn', default=ppn_default,
        help='Processes per node')
    group.add_argument(
        '-w', '--walltime', type=str,
        dest='walltime', default=walltime_default,
        help='Maximum wall time')
    return group


def add_script_arguments(parser):
    group = parser.add_argument_group('Script arguments')
    group.add_argument(
        'input_filepath', help='Input filepath (full match)')
    group.add_argument(
        '--test-job', dest='test_job', action='store_true',
        help='Submit a test job that performs no work')
    return group


def add_submit_arguments(parser):
    group = parser.add_argument_group('Submit arguments')
    group.add_argument(
        '-n', '--number', type=int, dest='number', default=1,
        help='Number of files to submit')
    group.add_argument(
        '--test-job', dest='test_job', action='store_true',
        help='Submit a test job that performs no work')
    return group


def add_ext_submit_arguments(parser):
    group = parser.add_argument_group('External submission arguments')
    group.add_argument(
        '-s', '--submitted', type=dateparser.parse,
        help='Date/time that job was submitted to PBS without use of gcsub')
    group.add_argument(
        '-j', '--job-id', dest='pbs_job_id', type=str,
        help='PBS job id of submission')
    return group


def add_listing_arguments(parser):
    group = parser.add_argument_group('Listing control arguments')
    mutex_group = parser.add_mutually_exclusive_group()
    mutex_group.add_argument(
        '-C', '--compact', action='store_true',
        help='Display compact listing')
    mutex_group.add_argument(
        '-F', '--full', action='store_true',
        help='Display full listing')
    group.add_argument(
        '-f', '--filepath-replace', dest='filepath_replace', nargs=2,
        help='Search/replace filepath string for more readable listing'
    )
    group.add_argument(
        '-i', '--input-filepath', dest='input_filepath',
        help='Input filepath (partial match)')
    group.add_argument(
        '-j', '--job-id', dest='pbs_job_id', type=str,
        help='PBS job id of submission')
    group.add_argument(
        '-s', '--status', help='Status of queue entry',
        choices=gcq_statuses)
    return group


def add_reset_arguments(parser):
    group = parser.add_argument_group('Reset arguments')
    group.add_argument(
        'input_filepath', help='Input filepath (full match)')
    group.add_argument(
        '-s', '--status', help='Status of queue entry',
        choices=gcq_statuses, default='NEW')
    return group
