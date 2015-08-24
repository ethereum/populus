import os
from flask import Flask


app = Flask(__name__)


def get_html_document(project_dir, path):
    html_root = os.path.join(project_dir, './html')
    document_path = os.path.join(html_root, path)
    with open(document_path) as document_file:
        document = document_file.read()
    return document


@app.route('/')
def index():
    return get_html_document(os.getcwd(), 'index.html')


POPULUS_ASSET_PATH = os.path.join(os.path.dirname(__file__), 'assets')


def get_static_asset(project_dir, path):
    asset_root = os.path.join(project_dir, './assets')
    project_asset_path = os.path.join(asset_root, path)

    if os.path.exists(project_asset_path):
        path_to_load = project_asset_path
    else:
        path_to_load = os.path.join(POPULUS_ASSET_PATH, path)

    with open(path_to_load) as asset_file:
        asset = asset_file.read()
    return asset


@app.route('/static-2/<path:asset_path>')
def static2(asset_path):
    return get_static_asset(os.getcwd(), asset_path)


from populus.utils import get_build_dir


@app.route('/static-3/contracts.js')
def contracts():
    build_dir = get_build_dir(os.getcwd())
    contracts_json_path = os.path.join(build_dir, 'contracts.json')
    with open(contracts_json_path) as contracts_json_file:
        contracts_json = contracts_json_file.read()

    return "var contract_abis = {0};".format(contracts_json)
