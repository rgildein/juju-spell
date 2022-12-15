# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2022 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Tests for base cli functions."""
import argparse
from unittest.mock import MagicMock, patch

import pytest

from multijuju.config import Config, Controller


def test_fill_parser(test_cmd):
    """Test add additional CLI arguments."""
    parser = MagicMock()
    test_cmd.fill_parser(parser)

    parser.add_argument.assert_called_once_with(
        "--silent", default=False, action="store_true", help="This will skip all the confirm check."
    )


def _create_test_controller(name: str) -> Controller:
    """Create test controller."""
    return Controller(
        name=name,
        customer="test-customer",
        owner="test-owner",
        endpoint="10.1.1.99:17070",
        ca_cert="ca-cert",
        username="test-user",
        password="test-password",
        model_mapping={},
    )


@pytest.mark.parametrize(
    "parsed_args, exp_parsed_args",
    [
        ({"silent": False}, {"silent": False}),
        ({"silent": False, "filter": Config([])}, {"silent": False, "filter": Config([])}),
        (
            {"silent": False, "filter": Config([_create_test_controller("test-1"), _create_test_controller("test-2")])},
            {"silent": False, "filter": Config(["test-1", "test-2"])},
        ),
    ],
)
def test_safe_parsed_args_output(parsed_args, exp_parsed_args, test_cmd):
    """Test removing sensitive information from output."""
    parsed_args = argparse.Namespace(**parsed_args)
    exp_parsed_args = argparse.Namespace(**exp_parsed_args)
    assert test_cmd.safe_parsed_args_output(parsed_args) == exp_parsed_args


@pytest.mark.parametrize(
    "parsed_args, confirm_return_value, executed",
    [
        ({"silent": False}, True, True),
        ({"silent": False}, False, False),
        ({"silent": True}, True, True),
        ({"silent": True}, False, True),
    ],
)
def test_run(parsed_args, confirm_return_value, executed, test_cmd):
    """Test BaseCMD run."""
    parsed_args = argparse.Namespace(**parsed_args)
    test_cmd.before = mock_before = MagicMock()
    test_cmd.execute = mock_execute = MagicMock()
    test_cmd.format_output = mock_format_output = MagicMock()
    test_cmd.after = mock_after = MagicMock()

    with patch("multijuju.cli.base.confirm", return_value=confirm_return_value):
        test_cmd.run(parsed_args)

    if executed:
        mock_before.assert_called_once_with(parsed_args)
        mock_execute.assert_called_once_with(parsed_args)
        mock_format_output.assert_called_once_with(mock_execute.return_value)
        mock_after.assert_called_once_with(parsed_args)
    else:
        mock_before.assert_not_called()
        mock_execute.assert_not_called()
        mock_format_output.assert_not_called()
        mock_after.assert_not_called()
