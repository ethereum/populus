import itertools
import click


def select_chain(project):
    chain_options = set(project.config.chains.keys())

    choose_chain_msg = "\n".join(itertools.chain((
        "Available Chains",
        "----------------",
    ), (
        "{0} - {1}".format(chain_index, chain_name)
        for chain_index, chain_name in enumerate(sorted(chain_options))
    ), (
        "",
        "Enter ether the name, or number of the desired chain"
    )))
    chain_name = click.prompt(choose_chain_msg)
    if chain_name in chain_options:
        return chain_name
    elif chain_name.isdigit() and int(chain_name) < len(chain_options):
        return sorted(chain_options)[int(chain_name)]
    else:
        raise click.Abort(
            "Invalid choice: {0}.  Please choose from one of the "
            "provided options.".format(chain_name)
        )
