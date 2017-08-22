#!python
"""
Write to stdout the script that will be or was submitted by ``jq submit`` for
a specified queue entry.
"""

from . import GenerateClimosQueueEntry
from .gcsub import make_qsub_script, make_qsub_test_script


def output_generate_climos_script(session, input_filepath, test_job):
    entry = (
        session.query(GenerateClimosQueueEntry)
            .filter(GenerateClimosQueueEntry.input_filepath == input_filepath)
            .first()
    )

    if test_job:
        script = make_qsub_test_script(entry)
    else:
        script = make_qsub_script(entry)

    print(script)
