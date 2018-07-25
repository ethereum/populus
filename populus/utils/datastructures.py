from collections import (
    defaultdict,
)

from cytoolz import (
    valmap,
)

from populus.utils.epoch import (
    epoc_time_now,
)


class ContractMeta:
    def __init__(self, address, timestmap):
        self.address = address
        self.timestamp = timestmap


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
        data = valmap(lambda x: x['timestamp'], val).items()
        return map(lambda args: self.output_cls(*args), data)
