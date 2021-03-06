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


def reset_generate_climos_queue_entry(session, input_filepath, target_status):
    """Reset a climo queue entry status to `status`

    :param input_filepath (str): filepath of entry to be reset
    :param target_status (str): status to reset entry to (must be one of valid
        status values)
    """
    q = (
        session.query(GenerateClimosQueueEntry)
            .filter(GenerateClimosQueueEntry.input_filepath
                    .like('%{}%'.format(input_filepath)))
    )
    entries = q.all()

    # Transitions from current status to process previous status
    previous_status = {
        'SUCCESS': 'RUNNING',
        'ERROR': 'RUNNING',
        'RUNNING': 'SUBMITTED',
        'SUBMITTED': 'NEW',
        'HOLD': 'NEW',
    }

    def single_step_to(status, entry):
        """Single-step reset to `status` from next later status."""
        logger.debug('{} -> {}'.format(entry.status, status))
        if status == 'NEW':
            assert entry.status in {'SUBMITTED', 'HOLD'}
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

    def step_to(target_status, entry):
        # Check validity of proposed reset.
        # Note: This will fail on valid resets if ``previous_status`` is incorrectly
        # defined. Just sayin'.
        status = entry.status
        while status != target_status:
            try:
                status = previous_status[status]
            except KeyError:
                logger.error('Cannot reset status from {} to {}'
                             .format(entry.status, target_status))
                return

        # Perform the transitions from current status to target status.
        status = entry.status
        while status != target_status:
            try:
                status = previous_status[status]
                single_step_to(status, entry)
            except ValueError:
                logger.error('Cannot step from status {} to {}'
                             .format(entry.status, status))
            except AssertionError:
                logger.error('Cannot step from status {} to {}'
                             .format(entry.status, status))

    for entry in entries:
        response = 'x'
        while response not in ['', 'y', 'n']:
            response = (
                input('{}\nreset? (Y/n) '.format(entry.input_filepath))
                    .strip().lower())
            if response in ['', 'y']:
                step_to(target_status, entry)

    session.commit()
    return 0
