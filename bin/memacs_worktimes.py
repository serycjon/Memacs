#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from memacs.worktimes import WorktimesMemacs

PROG_VERSION_NUMBER = u"0.1"
PROG_VERSION_DATE = u"2018-01-31"
PROG_SHORT_DESCRIPTION = u"Memacs for worktimes"
PROG_TAG = u"worktimes"
PROG_DESCRIPTION = u"""
This Memacs module will parse output of Tasker worktime tasks.

sample csv file:
doma_clock_in; 1517303292
cmp_clock_in; 1517306563
doma_clock_out; 1517305338
cmp_clock_out; 1517311599
cmp_clock_in; 1517314013
doma_clock_in; 1517333741
cmp_clock_out; 1517332153

Then an Org-mode file is generated.
"""
COPYRIGHT_YEAR = "2018"
COPYRIGHT_AUTHORS = """Jonas Serych <jonas.serych@gmail.com>"""

if __name__ == "__main__":
    memacs = WorktimesMemacs(
        prog_version=PROG_VERSION_NUMBER,
        prog_version_date=PROG_VERSION_DATE,
        prog_description=PROG_DESCRIPTION,
        prog_short_description=PROG_SHORT_DESCRIPTION,
        prog_tag=PROG_TAG,
        copyright_year=COPYRIGHT_YEAR,
        copyright_authors=COPYRIGHT_AUTHORS
        )
    memacs.handle_main()
