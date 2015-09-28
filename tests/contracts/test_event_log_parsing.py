

single_index_data = {
    'val_a': 'test-val_a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
    'val_b': 12345,
}
single_index_entry = {
    'data': '0x746573742d76616c5f61000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000003039',
    'blockHash': '0x8ee4122228d99b29bd837e372c15f7fce8d4fc6f92d95a237e7ef04f44aba0e4',
    'transactionHash': '0x6c1cb2754147be0a6772657e1798a0b1c2c0bb9131d7badea3ae3fed4c6f103e',
    'transactionIndex': '0x1',
    'logIndex': '0x0',
    'address': '0xc305c901078781c232a2a521c2af7980f8385ee9',
    'type': 'mined',
    'topics': [
        '0xe5091e521791fb0fb6be999dcb6d5031d9f0a8032185b13790f8d2f95e163b1f',
        '0x746573742d6b6579000000000000000000000000000000000000000000000000',
    ],
    'blockNumber': '0x0',
}

double_index_data = {
    'val_a': 'test-val_a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
    'val_b': 12345,
}
double_index_topics = {
    # HTF does this work?
}
double_index_log_entry = {
    'data': '0x746573742d76616c5f61000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000003039',
    'blockHash': '0x72ce3ebf50d4da33a796c289b1423b4d17454d7d966041017ee640a09cb539ed',
    'transactionHash': '0xc282d4f8a7f92904ed63275022cca848311056cab40d18b2bfb2dad9186faadb',
    'transactionIndex': '0x1',
    'logIndex': '0x0',
    'address': '0xc305c901078781c232a2a521c2af7980f8385ee9',
    'type': 'mined',
    'topics': [
        '0x968e08311bcc13cd5d4feae6a3c87bedb195ab51905c8ec75a10580b5b5854c7',
        '0x746573742d6b65792d6100000000000000000000000000000000000000000000',
        '0x746573742d6b65792d6200000000000000000000000000000000000000000000',
    ],
    'blockNumber': '0x0',
}


def test_log_data_parsing_a(LogsEvents):
    data = LogsEvents.DoubleIndex.get_log_data(double_index_log_entry)
    assert data == single_index_data


def test_log_data_parsing_b(LogsEvents):
    data = LogsEvents.SingleIndex.get_log_data(double_index_log_entry)
    assert data == double_index_data
