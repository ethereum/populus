from collections import (
    defaultdict,
    namedtuple,
)

from cytoolz import (
    valmap,
)

from populus.utils.epoch import (
    epoc_time_now,
)


ContractMeta = namedtuple('ContractMeta', ['address', 'timestamp'])


class TimeStampedRegistrar:

    def __init__(self, output_cls):
        self.data = defaultdict(dict)
        self.output_cls = output_cls

    def insert(self, name, val):
        self.data[name].update({
            val: {'timestamp': epoc_time_now()}
        })

    def __contains__(self, item):
        return item in self.data

    def __getitem__(self, name):
        val = self.data.__getitem__(name)
        data = valmap(lambda x: x['timestamp'], val)
        return map(lambda args: self.output_cls(*args), data.items())
