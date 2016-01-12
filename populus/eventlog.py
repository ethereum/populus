
import threading

DEFAULT_POLL_PERIOD = 1.0  # seconds
MIN_POLL_PERIOD = 0.1  # seconds


class EventLogMonitor:
    """ Event Log Monitor Class
        This class manages setting up filters and issuing
        callbacks when the blockchain issues logs from transactions.
    """
    def __init__(
            self, client, poll_period=DEFAULT_POLL_PERIOD
    ):
        """ @param client RPC client to access the blockchain.
            @param poll_period polling period in seconds.
        """
        if poll_period < MIN_POLL_PERIOD:
            raise ValueError("Polling Period must be greater than %f seconds" % MIN_POLL_PERIOD)

        self.client = client
        self._period = poll_period

        # Information about filters available
        # Key is the filter number
        # Value is a list of tuples
        #    Each tuple is {
        #          addr, event, func LogCallback
        #          }
        self._flock = threading.Lock()
        self._filters = {}

        self._timerEnabled = False

    def start_timer(self):
        self._timerEnabled = True
        self._start_timer()

    def stop_timer(self):
        self._timerEnabled = False

    def _start_timer(self):
        self._timer = threading.Timer(
            self._period, EventLogMonitor._timer_handler, [self]
        )
        self._timer.daemon = True
        self._timer.start()

    def get_client(self):
        return(self.client)

    def add_filter(self, address, cb, eventTopics=None):
        """
        Add a new event log filter associated with a particular
        type of log from the blockchain.
        @param address Contract address we are watching for.
        @param cb callback function that accepts kw.
           Must be a callable object.
        @param eventTopics a list of topic strings or None
        @return filter ID that was returned via the ethereum RPC that
           identifies this filter.
        """
        with self._flock:
            filt_id = self.client.new_filter(
                address=address, topics=eventTopics
            )
            self._filters[filt_id] = (address, eventTopics, cb)
            return(filt_id)

    def remove_filter(self, filt_id):
        """ Remove an existing event log filter
            @param filt_id filter ID that was returned
        """
        with self._flock:
            del self._filters[filt_id]

    def poll(self):
        """ Poll for filter changes from all of the known
            filters.
            [Thread-Safe]
        """
        with self._flock:
            for filt_id in self._filters.keys():
                addr, event, cb = self._filters[filt_id]
                changes = self.client.get_filter_changes(filt_id)
                if len(changes) > 0:
                    for receipt in changes:
                        try:
                            cb(receipt=receipt, address=addr, topics=event)
                        except Exception as exc:
                            msg = "Filter[%s]: Failed CB: %s" % (filt_id, str(exc))
                            print(msg)

    def _timer_handler(self):
        """ Periodic polling timer for the event log acquisition
            We check all our known filter ids for changes and
            invoke the callback as we get that data.
        """
        if not self._timerEnabled:
            return
        # Poll for the latest logs
        self.poll()
        # Restart the timer
        self._start_timer()

    # Internal Methods
    # This is primarily so we can use the with statement
    def _cleanup(self):
        for filt_id in self._filters.keys():
            self.client.uninstall_filter(filt_id)

    def __enter__(self):
        return(self)

    def __exit__(self, exc_type, exc_value, traceback):
        """
        """
        self._cleanup()
