import os
import shutil

from flask import (
    Flask,
    current_app,
)

from populus.utils import (
    get_build_dir,
    ensure_path_exists,
)


POPULUS_ASSET_PATH = os.path.join(os.path.dirname(__file__), 'assets')
POPULUS_TEMPLATES_PATH = os.path.join(os.path.dirname(__file__), 'templates')


def get_build_assets_dir(project_dir):
    build_dir = get_build_dir(project_dir)
    return os.path.abspath(os.path.join(build_dir, 'assets'))


def get_html_dir(project_dir):
    html_dir = os.path.abspath(os.path.join(project_dir, './html'))
    return html_dir


def index_view():
    html_dir = get_html_dir(current_app.populus_project_dir)
    document_path = os.path.join(html_dir, 'index.html')
    with open(document_path) as document_file:
        document = document_file.read()
    return document


def write_default_index_html_document(dest_path):
    src_path = os.path.join(POPULUS_TEMPLATES_PATH, 'index.html')
    shutil.copy(src_path, dest_path)


def get_flask_app(project_dir):
    static_folder = os.path.join(project_dir, 'build', 'assets')
    app = Flask(__name__, static_folder=static_folder, static_url_path='/static')
    app.populus_project_dir = project_dir

    app.route('/')(index_view)
    return app


js_contracts_template = """
var contracts = contracts || {{}};

function makeContracts() {{
    var contractData = {contract_data};
    var contractNames = Object.keys(contractData);
    for (var i=0; i < contractNames.length; i++) {{
        var contractName = contractNames[i];
        contracts[contractName] = web3.eth.contract(contractData[contractName].info.abiDefinition);
    }}
}};
makeContracts();
"""


def get_contracts_js_path(project_dir):
    build_dir = get_build_dir(project_dir)
    return os.path.join(build_dir, 'contracts.js')


def compile_js_contracts(project_dir):
    build_dir = get_build_dir(project_dir)

    contracts_json_path = os.path.join(build_dir, 'contracts.json')
    with open(contracts_json_path) as contracts_json_file:
        contracts_json = contracts_json_file.read()

    js_contracts = js_contracts_template.format(contract_data=contracts_json)

    js_contracts_path = get_contracts_js_path(project_dir)

    with open(js_contracts_path, 'w') as js_contracts_file:
        js_contracts_file.write(js_contracts)

    return js_contracts_path


def get_static_assets_dir(project_dir):
    return os.path.abspath(os.path.join(project_dir, 'assets'))


def project_has_assets(project_dir):
    project_assets_path = get_static_assets_dir(project_dir)
    return os.path.exists(project_assets_path)


def collect_static_assets(project_dir):
    project_assets_path = get_static_assets_dir(project_dir)

    build_dir = get_build_dir(project_dir)
    build_assets_path = os.path.join(build_dir, 'assets')
    ensure_path_exists(build_assets_path)
    build_js_assets_path = os.path.join(build_assets_path, 'js')
    ensure_path_exists(build_js_assets_path)

    # Put the contracts json in place.
    contracts_js_path = os.path.join(get_build_dir(project_dir), 'contracts.js')
    shutil.copy(contracts_js_path, build_js_assets_path)

    search_paths = (
        POPULUS_ASSET_PATH,
        project_assets_path,
    )

    for base_assets_dir in search_paths:
        prefix_length = len(base_assets_dir)
        for (dirpath, dirnames, filenames) in os.walk(base_assets_dir):
            asset_dir = os.path.join(build_assets_path, dirpath[prefix_length + 1:])
            ensure_path_exists(asset_dir)

            for filename in filenames:
                asset_path = os.path.abspath(os.path.join(dirpath, filename))
                shutil.copy(asset_path, asset_dir)
