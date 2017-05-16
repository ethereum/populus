import json


class ContractKeyMapping(object):
    def __init__(self, contracts=None):
        if contracts is None:
            contracts = {}

        invalid_syms = [sym for (_, sym) in contracts.keys() if ':' in sym]
        if len(invalid_syms) > 0:
            raise ValueError('Invalid symbols containing `:` found: {}'.format(invalid_syms))

        self.contracts = contracts


    def to_dict(self):
        return {':'.join(k): v for k, v in self.contracts.items()}

    @classmethod
    def from_dict(cls, dct):
        contracts = {}

        for k, v in dct.items():
            if isinstance(k, tuple):
                path, sym = k
            else:
                path, _, sym = k.rpartition(':')
            contracts[(path, sym)] = v

        return cls(contracts)


    def normalize_key(self, key, return_on_no_match=False):
        if isinstance(key, list):
            key = tuple(key)

        if key in self.contracts:
            return key

        if isinstance(key, str):
            kpath, _, ksym = key.rpartition(':')
        else:
            kpath, ksym = key

        key_matches = [
            (path, sym) for (path, sym) in self.contracts.keys()
            if (not kpath or not path or kpath == path) and sym == ksym
        ]

        if len(key_matches) == 0:
            if return_on_no_match:
                if isinstance(key, str):
                    path, _, sym = key.rpartition(':')
                    return (path, sym)
                return key
            raise KeyError('No matches found for index {}'.format(key))

        if len(key_matches) > 1:
            raise KeyError('Multiple matches found for index {}: {}'.format(key, key_matches))

        return key_matches[0]


    def __getitem__(self, key):
        return self.contracts[self.normalize_key(key)]

    def __setitem__(self, key, value):
        self.contracts[self.normalize_key(key, return_on_no_match=True)] = value

    def __contains__(self, key):
        return self.normalize_key(key, return_on_no_match=True) in self.contracts

    def __len__(self):
        return len(self.contracts)

    def __delitem__(self, key):
        del self.contracts[self.normalize_key(key)]

    def __iter__(self):
        return iter(self.contracts)

    def get(self, key, default=None):
        return self.contracts.get(self.normalize_key(key, return_on_no_match=True), default)

    def items(self):
        return self.contracts.items()

    def keys(self):
        return self.contracts.keys()

    def values(self):
        return self.contracts.values()


class ContractKeyMappingEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ContractKeyMapping):
            return obj.to_dict()
        return json.JSONEncoder.default(self, obj)


class DefaultContractKeyMapping(ContractKeyMapping):
    def __init__(self, default_factory, contracts=None):
        super().__init__(contracts)
        self.default_factory = default_factory

    def __getitem__(self, key):
        sup = super()
        if not sup.__contains__(key):
            sup.__setitem__(key, self.default_factory())
        return sup.__getitem__(key)
