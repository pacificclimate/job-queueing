#!python
"""
Reset the status of a queue entry.

Typically this script is used to reset the status to NEW, making the entry
eligible for submission again.
This is useful when an error has occurred in the processing of a submitted job,
and we wish to re-submit the job after addressing the problem.

Downside: History of reset job is replaced. It will take a more sophisticated
approach if we wish never to lose past history.
"""

from jobqueueing.script_helpers import logger
from jobqueueing import GenerateClimosQueueEntry
from jobqueueing import gcq_statuses


def reset_generate_climos_queue_entry(session, input_filepath, status):
    """Reset a climo queue entry status to `status`

    :param input_filepath (str): filepath of entry to be reset
    :param status (str): status to reset entry to (must be one of valid
        status values)
    """
    entry = session.query(GenerateClimosQueueEntry)\
        .filter(GenerateClimosQueueEntry.input_filepath == input_filepath)\
        .first()

    if not entry:
        logger.error(
            'Could not find generate_climos queue entry matching input file {}.'
            ' Skipping.'
            .format(input_filepath))
        return 1

    def single_step_to(status, entry):
        """Single-step reset to `status` from next later status."""
        logger.debug('Stepping from status {} to {}'
                     .format(entry.status, status))
        if status == 'NEW':
            assert entry.status == 'SUBMITTED'
            entry.status = 'NEW'
            entry.submitted_time = None
            entry.pbs_job_id = None

        elif status == 'SUBMITTED':
            assert entry.status == 'RUNNING'
            entry.status = 'SUBMITTED'
            entry.started_time = None

        elif status == 'RUNNING':
            assert entry.status in {'SUCCESS', 'ERROR'}
            entry.status = 'RUNNING'
            entry.completed_time = None
            entry.completion_message = None

        else:
            raise ValueError

    rev_statuses = list(reversed(gcq_statuses))
    from_i = rev_statuses.index(entry.status)
    to_i = rev_statuses.index(status)
    if to_i <= from_i:
        logger.error('Cannot reset status from {} to {}'
                     .format(entry.status, status))
        return 1
    # Iterate through statuses in reverse order from predecessor of 
    # `entry.status` to `status`.
    # Example: for an entry in SUCCESS status, iterate from RUNNING to NEW.
    for i, status in enumerate(rev_statuses):
        if from_i < i <= to_i:
            try:
                single_step_to(status, entry)
            except ValueError:
                logger.error('Cannot reset status from {} to {}'
                             .format(entry.status, status))
                return 1
            except AssertionError:
                logger.error('Cannot step from status {} to {}'
                             .format(entry.status, status))
                return 1

    session.commit()
    return 0
