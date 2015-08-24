import os
import re
import subprocess

from populus.utils import ensure_path_exists


POPULUS_DIR = os.path.abspath(os.path.dirname(__file__))


def get_blockchains_dir(project_dir):
    return os.path.abspath(os.path.join(project_dir, 'chains'))


def get_geth_data_dir(project_dir, name):
    blockchains_dir = get_blockchains_dir(project_dir)
    return os.path.join(blockchains_dir, name)


def geth_wrapper(data_dir, cmd="geth", genesis_block=None, extra_args=None):
    if genesis_block is None:
        genesis_block = os.path.join(POPULUS_DIR, 'genesis-test.json')
    command = [cmd, '--datadir', data_dir]

    if extra_args:
        command.extend(extra_args)

    proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc


def geth_accounts(*args, **kwargs):
    extra_args = kwargs.get('extra_args', [])
    extra_args.extend('account', 'list')

    kwargs['extra_args'] = extra_args

    proc = geth_wrapper(*args, **kwargs)
    stdoutdata, stderrdata = p.communicate()

    if proc.returncode:
        raise subprocess.CalledProcessError('Error calling to `geth`:\n{0}'.format(stderrdata))
    accounts = parse_geth_accounts(stdoutdata)
    return accounts


account_regex = re.compile('\{([a-f0-9]{40})\}')


def parse_geth_accounts(raw_accounts_output):
    accounts = account_regex.findall(raw_accounts_output)
    return tuple('0x' + account for account in accounts)
