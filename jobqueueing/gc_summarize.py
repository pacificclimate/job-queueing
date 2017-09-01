"""
Summarize entries in the ``generate_climos`` queue.
"""

from sqlalchemy import func

from jobqueueing.script_helpers import logger
from jobqueueing import GenerateClimosQueueEntry


def summarize_entries(
        session,
        input_filepath,
):
    q = (
        session.query(GenerateClimosQueueEntry.status,
                      func.count(GenerateClimosQueueEntry.status).label('num')
                      )
            .group_by(GenerateClimosQueueEntry.status)
            .order_by(GenerateClimosQueueEntry.status)
    )

    if input_filepath:
        q = q.filter(GenerateClimosQueueEntry.input_filepath
                     .like('%{}%'.format(input_filepath)))

    counts = q.all()
    for count in counts:
        print('{count.status}: {count.num}'.format(count=count))
