"""
List entries in the `generate_climos` queue.
"""

import os.path
import re

from jobqueueing.script_helpers import logger
from jobqueueing import GenerateClimosQueueEntry


def list_entries(
        session,
        input_filepath=None,
        pbs_job_id=None,
        status=None,
        filepath_replace=None,
        compact=None,
        full=None
):
    """
    List entries in generate_climos queue.

    :param session: database session
    :param input_filepath (str): list only entries with input_filepath that
        partially matches this value
    :param pbs_job_id (str): list only entries with PBS job id that
        partially matches this value
    :param status (str): list only entries with status that
        exactly matches this value
    :param full (bool): If True, generate full listing with all parameters
        for each entry. Otherwise generate compact listing.
    :return:
    """
    q = session.query(GenerateClimosQueueEntry)\
        .order_by(GenerateClimosQueueEntry.added_time)
    if input_filepath:
        q = q.filter(GenerateClimosQueueEntry.input_filepath
                     .like('%{}%'.format(input_filepath)))
    if pbs_job_id:
        q = q.filter(GenerateClimosQueueEntry.pbs_job_id
                     .like('%{}%'.format(pbs_job_id)))
    if status:
        q = q.filter(GenerateClimosQueueEntry.status == status)
    entries = q.all()

    print('{} queue entries matched'.format(len(entries)))

    def mapped_filepath(filepath):
        if filepath_replace is None:
            return filepath
        return re.sub(filepath_replace[0], filepath_replace[1], filepath)

    if compact:
        for entry in entries:
            print(
                '{}: {} ({!s:4.4})'.format(
                    mapped_filepath(entry.input_filepath),
                    entry.status,
                    entry.pbs_job_id or ''
                ),
            )

    elif full:
        for entry in entries:
            print('{}:'.format(mapped_filepath(entry.input_filepath)))
            for attr in '''
                    py_venv
                    output_directory
                    convert_longitudes
                    split_vars
                    split_intervals
                    ppn
                    walltime
                    status
                    added_time
                    submitted_time
                    pbs_job_id
                    started_time
                    completed_time
                    completion_message
                    '''.split():
                print('    {} = {}'.format(attr, getattr(entry, attr)))

    else:
        title_fmt = ('  {:<16.16}'
                     ' | {:<9.9}'
                     ' | {:<16.16}'
                     ' | {:<4.4}'
                     ' | {:<16.16}'
                     ' | {:<16.16}')
        print(title_fmt.format(
            'Added time', 'Status', 'Submitted time', 'JID',
            'Started time', 'Completed time'
        ))
        print(title_fmt.format(*(('-'*100,) * 20)))
        for entry in entries:
            # print('{}:'.format(os.path.basename(entry.input_filepath)))
            print('{}:'.format(mapped_filepath(entry.input_filepath)))
            e = {name: getattr(entry, name)
                 for name in ('added_time',
                              'status',
                              'submitted_time',
                              'pbs_job_id',
                              'started_time',
                              'completed_time'
                             )}
            print("  {e[added_time]!s:.16}"
                  " | {e[status]:<9}"
                  " | {e[submitted_time]!s:<16.16}"
                  " | {e[pbs_job_id]!s:4.4}"
                  " | {e[started_time]!s:<16.16}"
                  " | {e[completed_time]!s:<16.16}"
                  .format(e={key: value if value else '--'
                           for key, value in e.items()}))
