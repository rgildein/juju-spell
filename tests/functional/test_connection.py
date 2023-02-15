import json

OK_EXIT_CODE = 0
ARGPARSING_ERROR_EXIT_CODE = 127


def test_help(juju_spell_run):
    """Test printing --help."""
    help_flag = juju_spell_run("--help")
    assert help_flag.exit_code == OK_EXIT_CODE

    help_default = juju_spell_run()
    assert help_default.exit_code == ARGPARSING_ERROR_EXIT_CODE

    assert help_flag.stdout == help_default.stdout


def test_connection_ping(juju_spell_run):
    """Test connection with ping command to each controller."""
    result = juju_spell_run("ping")

    assert result.exit_code == OK_EXIT_CODE
    result_json = json.loads(result.stdout)
    for controller in result_json:
        assert controller["success"] is True
        assert controller["output"] == "accessible"
