import dateutil.parser

from elastalert.ruletypes import RuleType



# elastalert.util includes useful utility functions
# such as converting from timestamp to datetime obj
from blist import sortedlist

from elastalert.util import ts_to_dt
from elastalert.util import new_get_event_ts


class EventWindow(object):
    """ A container for hold event counts for rules which need a chronological ordered event window. """

    def __init__(self, timeframe, onRemoved=None, getTimestamp=new_get_event_ts('@timestamp')):
        self.timeframe = timeframe
        self.onRemoved = onRemoved
        self.get_ts = getTimestamp
        self.data = sortedlist(key=self.get_ts)
        self.running_count = 0

    def clear(self):
        self.data = sortedlist(key=self.get_ts)
        self.running_count = 0

    def append(self, event):
        """ Add an event to the window. Event should be of the form (dict, count).
        This will also pop the oldest events and call onRemoved on them until the
        window size is less than timeframe. """
        self.data.add(event)
        self.running_count += event[1]

        while self.duration() >= self.timeframe:
            oldest = self.data[0]
            self.data.remove(oldest)
            self.running_count -= oldest[1]
            self.onRemoved and self.onRemoved(oldest)

    def duration(self):
        """ Get the size in timedelta of the window. """
        if not self.data:
            return datetime.timedelta(0)
        return self.get_ts(self.data[-1]) - self.get_ts(self.data[0])

    def count(self):
        """ Count the number of events in the window. """
        return self.running_count

    def mean(self):
        """ Compute the mean of the value_field in the window. """
        if len(self.data) > 0:
            datasum = 0
            datalen = 0
            for dat in self.data:
                if "placeholder" not in dat[0]:
                    datasum += dat[1]
                    datalen += 1
            if datalen > 0:
                return datasum / float(datalen)
            return None
        else:
            return None

    def __iter__(self):
        return iter(self.data)

    def append_middle(self, event):
        """ Attempt to place the event in the correct location in our deque.
        Returns True if successful, otherwise False. """
        rotation = 0
        ts = self.get_ts(event)

        # Append left if ts is earlier than first event
        if self.get_ts(self.data[0]) > ts:
            self.data.appendleft(event)
            self.running_count += event[1]
            return

        # Rotate window until we can insert event
        while self.get_ts(self.data[-1]) > ts:
            self.data.rotate(1)
            rotation += 1
            if rotation == len(self.data):
                # This should never happen
                return
        self.data.append(event)
        self.running_count += event[1]
        self.data.rotate(-rotation)

class Threshold(RuleType):

    # By setting required_options to a set of strings
    # You can ensure that the rule config file specifies all
    # of the options. Otherwise, ElastAlert will throw an exception
    # when trying to load the rule.
    required_options = set(['rx_pack_thres', 'tx_pack_thres', 'timeframe'])

    # add_data will be called each time Elasticsearch is queried.
    # data is a list of documents from Elasticsearch, sorted by timestamp,
    # including all the fields that the config specifies with "include"
    def add_data(self, data):
        for document in data:

            #rx_pack_thres = self.rules['rx_pack_thres']
            rx_packtes = document['rx_packets']
            tx_packtes = document['tx_packets']

            if rx_packets < self.rules['rx_pack_thres'] or tx_packets < self.rules['tx_pack_thres']:
                # To add a match, use self.add_match
                self.add_match(document)

            # # To access config options, use self.rules
            # if document['username'] in self.rules['usernames']:

            #     # Convert the timestamp to a time object
            #     login_time = document['@timestamp'].time()

            #     # Convert time_start and time_end to time objects
            #     time_start = dateutil.parser.parse(self.rules['time_start']).time()
            #     time_end = dateutil.parser.parse(self.rules['time_end']).time()

            #     # If the time falls between start and end
            #     if login_time > time_start and login_time < time_end:

            #         # To add a match, use self.add_match
            #         self.add_match(document)

    # The results of get_match_str will appear in the alert text
    def get_match_str(self, match):
        return "%s rx_packets, and/or tx_packets %s above thresholds: rx %s and tx %s" % (match['rx_packets'], match['tx_packets'],
                                                   self.rules['rx_pack_thres'],
                                                   self.rules['tx_pack_thres'])

    # garbage_collect is called indicating that ElastAlert has already been run up to timestamp
    # It is useful for knowing that there were no query results from Elasticsearch because
    # add_data will not be called with an empty list
    def garbage_collect(self, timestamp):
        pass



class Threshold2(RuleType):
    """ A rule that matches if num_events number of events occur within a timeframe """
    required_options = frozenset(['num_events', 'timeframe', 'rx_pack_thres', 'tx_pack_thres'])

    def __init__(self, *args):
        super(Threshold2, self).__init__(*args)
        self.ts_field = self.rules.get('timestamp_field', '@timestamp')
        self.get_ts = new_get_event_ts(self.ts_field)
        self.attach_related = self.rules.get('attach_related', False)

    def add_count_data(self, data):
        """ Add count data to the rule. Data should be of the form {ts: count}. """
        if len(data) > 1:
            raise EAException('add_count_data can only accept one count at a time')

        (ts, count), = list(data.items())

        event = ({self.ts_field: ts}, count)
        self.occurrences.setdefault('all', EventWindow(self.rules['timeframe'], getTimestamp=self.get_ts)).append(event)
        self.check_for_match('all')

    def add_terms_data(self, terms):
        for timestamp, buckets in terms.items():
            for bucket in buckets:
                event = ({self.ts_field: timestamp,
                          self.rules['query_key']: bucket['key']}, bucket['doc_count'])
                self.occurrences.setdefault(bucket['key'], EventWindow(self.rules['timeframe'], getTimestamp=self.get_ts)).append(event)
                self.check_for_match(bucket['key'])

    def add_data(self, data):
        if 'query_key' in self.rules:
            qk = self.rules['query_key']
        else:
            qk = None

        for event in data:
            if qk:
                key = hashable(lookup_es_key(event, qk))
            else:
                # If no query_key, we use the key 'all' for all events
                key = 'all'

            # Store the timestamps of recent occurrences, per key
            self.occurrences.setdefault(key, EventWindow(self.rules['timeframe'], getTimestamp=self.get_ts)).append((event, 1))
            self.check_for_match(key, end=False)

        # We call this multiple times with the 'end' parameter because subclasses
        # may or may not want to check while only partial data has been added
        if key in self.occurrences:  # could have been emptied by previous check
            self.check_for_match(key, end=True)

    def check_for_match(self, key, end=False):
        # Match if, after removing old events, we hit num_events.
        # the 'end' parameter depends on whether this was called from the
        # middle or end of an add_data call and is used in subclasses
        if self.occurrences[key].count() >= self.rules['num_events'] and self.occurrences['rx_packets']>= self.rule[rx_pack_thres] and self.occurrences['tx_packets']>= self.rule[tx_pack_thres]:
            event = self.occurrences[key].data[-1][0]
            if event[self.rules['field1']]>= self.rules['rx_pack_thres']:
                if self.attach_related:
                    event['related_events'] = [data[0] for data in self.occurrences[key].data[:-1]]
                self.add_match(event)
                self.occurrences.pop(key)

    def garbage_collect(self, timestamp):
        """ Remove all occurrence data that is beyond the timeframe away """
        stale_keys = []
        for key, window in self.occurrences.items():
            if timestamp - lookup_es_key(window.data[-1][0], self.ts_field) > self.rules['timeframe']:
                stale_keys.append(key)
        list(map(self.occurrences.pop, stale_keys))

    def get_match_str(self, match):
        lt = self.rules.get('use_local_time')
        match_ts = lookup_es_key(match, self.ts_field)
        starttime = pretty_ts(dt_to_ts(ts_to_dt(match_ts) - self.rules['timeframe']), lt)
        endtime = pretty_ts(match_ts, lt)
        message = 'At least %d events occurred between %s and %s with %s rx_packets and %s tx_packets\n\n' % (self.rules['num_events'],
                                                                         starttime,
                                                                         endtime, 
                                                                         match['rx_packets'],
                                                                         match['tx_packets'])
        return message


