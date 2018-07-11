import os

from populus.utils.compile import process_import_remappings

beginning_paths = {
    'import-path-in-source/={0}'.format('actual-path/'),
    'import-path-in-source={0}'.format('actual-path'),
    'source-file.sol:import-path-in-source/={0}'.format('actual-path/'),
    'source-file.sol:import-path-in-source={0}'.format('actual-path'),
}

abs_path = os.path.abspath('actual-path')

expected_paths = {
    'import-path-in-source/={0}'.format(abs_path + '/'),
    'import-path-in-source={0}'.format(abs_path),
    'source-file.sol:import-path-in-source/={0}'.format(abs_path + '/'),
    'source-file.sol:import-path-in-source={0}'.format(abs_path),
}

final_paths = process_import_remappings(beginning_paths)

def print_paths(list, name):
    print(name)
    for path in list:
        print('\t ' + path)

print_paths(beginning_paths, 'beginning_paths')
print_paths(expected_paths, 'expected_paths')
print_paths(final_paths, 'final_paths')


assert set(final_paths) == set(expected_paths)
