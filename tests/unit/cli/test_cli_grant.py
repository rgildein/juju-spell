from unittest import mock

from juju_spell.cli.grant import ACL_CHOICES, GrantCMD


def test_grant_cmd_fill_parser():
    """Test add additional CLI arguments with BaseCMD."""
    parser = mock.MagicMock()
    GrantCMD(config=None).fill_parser(parser)

    parser.add_argument.assert_has_calls(
        [
            mock.call("--username", type=str, help="username to grant", required=True),
            mock.call(
                "--acl",
                type=str,
                choices=ACL_CHOICES,
                help="Access control. e.g., {}.".format(",".join(ACL_CHOICES)),
                default=False,
                required=True,
            ),
        ]
    )
