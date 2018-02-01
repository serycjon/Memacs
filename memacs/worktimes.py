#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import logging
import time, datetime
import pytz
from lib.memacs import Memacs
from lib.orgformat import OrgFormat
from lib.reader import CommonReader, UnicodeCsvReader
from lib.orgproperty import OrgProperties


class WorktimesMemacs(Memacs):
    def _parser_add_arguments(self):
        """
        overwritten method of class Memacs

        add additional arguments
        """
        Memacs._parser_add_arguments(self)

        self._parser.add_argument(
            "-f", "--file", dest="worktimescsvfile",
            action="store", required=True,
            help="path to worktimes csv file")

    def _parser_parse_args(self):
        """
        overwritten method of class Memacs

        all additional arguments are parsed in here
        """
        Memacs._parser_parse_args(self)
        if not (os.path.exists(self._args.worktimescsvfile) or \
                     os.access(self._args.worktimescsvfile, os.R_OK)):
            self._parser.error("input file not found or not readable")

    def _parse_entry(self, row):
        tag, time = row
        time = int(time.strip())
        if tag.endswith("_clock_in"):
            place_tag = tag[:-len("_clock_in")]
            event = "in"
        elif tag.endswith("_clock_out"):
            place_tag = tag[:-len("_clock_out")]
            event = "out"
        else:
            logging.error('worktimes: invalid tag {}'.format(tag))
            sys.exit(1)

        return {'place': place_tag,
                'event': event,
                'time': time }

    def _process_range(self, start, stop):
        start_dt = time.localtime(start['time'])
        start_timestamp = OrgFormat.datetime(start_dt)

        stop_dt = time.localtime(stop['time'])
        stop_timestamp = OrgFormat.datetime(stop_dt)

        range_timestamp = '{}-{}'.format(start_timestamp, stop_timestamp)

        duration = stop['time'] - start['time']
        d = divmod(duration, 86400)  # days
        h = divmod(d[1], 3600)  # hours
        m = divmod(h[1], 60)  # minutes
        s = m[1]  # seconds

        duration_string = '{:d}:{:02d}'.format(24*d[0] + h[0], m[0])
        output = "Stayed at: {} for {}".format(start['place'], duration_string)

        data_for_hashing = output + range_timestamp
        properties = OrgProperties(data_for_hashing=data_for_hashing)
        properties.add("PLACE", start['place'])
        properties.add("DURATION", duration_string)
        
        self._writer.write_org_subitem(output=output,
                                       timestamp=range_timestamp,
                                       properties=properties,
                                       tags=[start['place']])
    
    def _main(self):
        """
        gets called automatically from Memacs class.

        read the lines from worktimes csv file,
        parse and write them to org file
        """

        parsed = []
        with open(self._args.worktimescsvfile, 'r') as fin:
            reader = UnicodeCsvReader(fin, delimiter=';')

            for row in reader:
                parsed.append(self._parse_entry(row))

        # sort the events by time
        parsed.sort(key=lambda x: x['time'])

        # go through entries and extract clock_in clock_out pairs
        opened = {}
        for i in range(len(parsed)):
            place, event = parsed[i]['place'], parsed[i]['event']

            if place in opened:
                if event == 'out':
                    self._process_range(opened[place], parsed[i])
                    del opened[place]
                else:
                    logging.error('worktimes: clocking in to already clocked in place ({}). Current: {}, Previous: {}'.
                                  format(place, time, opened[place]['time']))
                    sys.exit(1)
            else:
                if event == 'in':
                    opened[place] = parsed[i]
                else:
                    logging.error('worktimes: clocking out without previously clocking in {}, {}'.
                                  format(place, time))
                    sys.exit(1)

        if len(opened) != 0:
            for place, opening in opened.iteritems():
                now = int(time.time())
                if opening['time'] != parsed[-1]['time']:
                    if now - opening['time'] > 60 * 40:
                        logging.error('worktimes: not clocked out from \'{}\' from {}'.format(place, opening['time']))
                        sys.exit(1)
                    else:
                        logging.error('worktimes: not clocked out from \'{}\' from {}, but still hoping.'.
                                      format(place, opening['time']))
                        continue
                artificial_end = {'place': place,
                                  'event': 'out',
                                  'time': now}
                self._process_range(opening, artificial_end)
