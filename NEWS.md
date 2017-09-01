# News / Release Notes

## 0.2.5

*2017 Sep 01*

* Fix bugs and improve functionality of ``jq reset``. Now does partial match on filepath
  and interactively confirms reset of each matching file.

## 0.2.4

*2017 Sep 01*

* Add status HOLD and ``jq hold`` and ``jq unhold`` commands.

## 0.2.3

*2017 Aug 29*

* Fix error introduced into ``jq list``

## 0.2.2

*2017 Aug 29*

* Add ``jq summarize`` command: Output summary by status of queue entries.

## 0.2.1

*2017 Aug 28*

* Improvements to ``jq list``:
  * Add arg --compact arg: 1 line per queue entry.
  * Add arg --filepath-replace: Filepath replacement via regex to enable arbitrary rewriting of filepaths for 
    easier viewing/analysis.

## 0.2.0

*2017 Aug 22*

* Add ``jq script`` command to output script that would be submitted by ``jq submit``.


## 0.1.0

*2017 Aug 21*

* Initial release of jobqueueing scripts as a separate project.
* Previous "releases" were part of [CE backend](https://github.com/pacificclimate/climate-explorer-backend)
  but those releases were not specific to jobqueueing and did not document it.
* A >90% solar eclipse occurred today in Victoria, B.C. This probably does not affect the software.
