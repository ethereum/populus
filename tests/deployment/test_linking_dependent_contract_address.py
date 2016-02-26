import os

from populus.utils import (
    load_contracts,
)
from populus.deployment import (
    package_contracts,
    link_contract_dependency,
)



PROJECTS_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'projects')
project_dir = os.path.join(PROJECTS_DIR, 'test-01')


def test_linking_contract_dependencies():
    deployed_addr = '0x3abbae0d139b953491f292dc5c49a350bcb18f8d'

    contracts = package_contracts(load_contracts(project_dir))
    PiggyBank = contracts.PiggyBank
    ledger_lib = contracts.AccountingLib(deployed_addr, 'PLACEHOLDER')

    pre_length = len(contracts.PiggyBank._config.code)

    assert deployed_addr not in PiggyBank._config.code
    assert '__AccountingLib_________________________' in PiggyBank._config.code

    link_contract_dependency(PiggyBank, ledger_lib)

    assert '__AccountingLib_________________________' not in PiggyBank._config.code
    assert '_' not in PiggyBank._config.code

    # 0x prefixed version shouldn't be there.
    assert deployed_addr not in PiggyBank._config.code
    assert deployed_addr[2:] in PiggyBank._config.code
    assert len(contracts.PiggyBank._config.code) == pre_length
