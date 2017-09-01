#!python

"""
Toggle the state of an entry in the ``generate_climos`` queue between
states ``NEW`` and ``HOLD``.
"""

from jobqueueing import GenerateClimosQueueEntry


def set_gc_entry_status(session, input_filepath, target_status):
    q = (
        session.query(GenerateClimosQueueEntry)
            .filter(GenerateClimosQueueEntry.input_filepath
                    .like('%{}%'.format(input_filepath)))
    )
    if target_status == 'HOLD':
        q = q.filter(GenerateClimosQueueEntry.status == 'NEW')
        cmd = 'hold'
    elif target_status == 'NEW':
        q = q.filter(GenerateClimosQueueEntry.status == 'HOLD')
        cmd = 'unhold'
    else:
        raise ValueError(
            "Expected target status to be one of 'NEW', 'HOLD', but got '{}'"
                .format(target_status)
        )
    entries = q.all()

    for entry in entries:
        response = 'x'
        while response not in ['', 'y', 'n']:
            response = (
                input('{}\n{}? (Y/n) '.format(entry.input_filepath, cmd))
                .strip().lower())
            if response in ['', 'y']:
                entry.status = target_status

    session.commit()
    return 0


def hold_gc_entry(session, input_filepath):
    return set_gc_entry_status(session, input_filepath, 'HOLD')


def unhold_gc_entry(session, input_filepath):
    return set_gc_entry_status(session, input_filepath, 'NEW')
