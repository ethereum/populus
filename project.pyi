from populus.config import (
    ChainConfig,
    CompilerConfig,
    Config,
)

from populus.compilation.backends.base import (
    BaseCompilerBackend,
)

from populus.chain.base import (
    BaseChain,
)

from typing import (
    Dict,
    List,
    Optional,
)

class Project:
    project_dir:str = None
    config_file_path:str = None
    user_config_file_path:str = None

    def __init__(self,
                 project_dir: Optional[str]=None,
                 user_config_file_path: Optional[str]=None):
        ...
    #
    # Config
    #

    # _project_config = None
    # _user_config = None
    # _config_schema = None

    def load_config(self) -> None:
        ...

    def _reset_configs_cache(self) -> None:
        ...

    def reload_config(self) -> None:
        ...

    @property
    def user_config(self) -> Config:
        ...

    @property
    def project_config(self) -> Config:
        ...

    def merge_user_and_project_configs(self, user_config: Config, project_config: Config) -> Config:
        ...

    @property
    def config(self) -> Config:
        ...

    @config.setter
    def config(self, value) -> None:
        ...

    def clean_config(self) -> None:
        ...

    #
    # Project
    #
    @property
    def tests_dir(self) -> str:
        ...

    #
    # Contracts
    #
    @property
    def compiled_contracts_asset_path(self) -> str:
        ...

    @property
    @to_tuple
    def contracts_source_dirs(self) -> List[str]:
        ...

    @property
    def build_asset_dir(self) -> str:
        ...

    # _cached_compiled_contracts_mtime = None
    # _cached_compiled_contracts = None

    @to_tuple
    def get_all_source_file_paths(self):
        ...

    def is_compiled_contract_cache_stale(self) -> bool:
        ...

    def fill_contracts_cache(self, compiled_contracts: Dict, contracts_mtime: int|float) -> None:
        ...

    @property
    def compiled_contract_data(self) -> Dict:
        ...

    #
    # Compiler Backend
    #
    def get_compiler_backend(self) -> BaseCompilerBackend:
        ...

    #
    # Local Blockchains
    #
    def get_chain_config(self, chain_name: str) -> ChainConfig:
        ...

    def get_chain(self, chain_name: str, chain_config: Optional[Config]=None) -> BaseChain:
        ...

    @property
    def base_blockchain_storage_dir(self) -> str:
        ...
