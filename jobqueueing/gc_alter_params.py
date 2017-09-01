#!python
"""
Alter generate_climos params and PBS params of queue entries.

Altered entry must be in status NEW.

WARNING: All entries with a partial match to the postional arg (input_filepath)
will be updated.
"""

from jobqueueing.script_helpers import logger
from jobqueueing import GenerateClimosQueueEntry


updatable_params = '''
    py_venv
    output_directory
    convert_longitudes
    split_vars
    split_intervals
    ppn
    walltime
'''.split()


def update_generate_climos_queue_entries_with_params(
        session,
        input_filepath,
        **kwargs
):
    """

    :param session: datatbase session
    :param input_filepath (str): select all entires with input_filepath
        partially matching this string
    :param **kwargs (dict): Parameters to update.
        Variable `updatable_params` defines the names of these parameters
        (which are the keys of the dict).
        Parameters with a None value are not updated.
    :return (int): exit status
    """
    entries = (
        session.query(GenerateClimosQueueEntry)
        .filter(GenerateClimosQueueEntry.status == 'NEW')
        .all()
    )

    for entry in entries:
        if input_filepath in entry.input_filepath:
            for attr in updatable_params:
                update_value = kwargs.get(attr, None)
                if update_value is not None:
                    logger.debug('Updating {} to {}'.format(attr, update_value))
                    setattr(entry, attr, update_value)

    session.commit()
    return 0
