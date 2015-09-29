def test_abi_signatures(LogsEvents):
    assert LogsEvents.SingleIndex.abi_signature == 3842580050
    assert LogsEvents.SingleIndex.encoded_abi_signature == '\xe5\t\x1eR'

    assert LogsEvents.DoubleIndex.abi_signature == 2525890609
    assert LogsEvents.DoubleIndex.encoded_abi_signature == '\x96\x8e\x081'
