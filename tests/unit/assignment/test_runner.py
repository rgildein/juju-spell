# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2023 Canonical Ltd.
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
"""Tests for assignment.runner."""
import argparse
from unittest import mock
from unittest.mock import MagicMock

import pytest

from juju_spell.assignment.runner import get_result, run_serial
from juju_spell.commands.base import Result


@pytest.mark.parametrize(
    "controller_config, output, exp_result",
    [
        (
            MagicMock(),
            Result(True, "test-string-value", None),
            {
                "context": mock.ANY,
                "success": True,
                "output": "test-string-value",
                "error": None,
            },
        ),
        (
            MagicMock(),
            Result(False, "test-string-value", None),
            {
                "context": mock.ANY,
                "success": False,
                "output": "test-string-value",
                "error": None,
            },
        ),
        (
            MagicMock(),
            Result(True, 1234, None),
            {"context": mock.ANY, "success": True, "output": 1234, "error": None},
        ),
        (
            MagicMock(),
            Result(False, None, Exception("test")),
            {
                "context": mock.ANY,
                "success": False,
                "output": None,
                "error": mock.ANY,
            },
        ),
    ],
)
def test_get_result(controller_config, output, exp_result):
    """Test for get_result."""
    result = get_result(controller_config, output)
    assert result == exp_result


@pytest.mark.asyncio
@mock.patch("juju_spell.assignment.runner.get_controller", new_callable=mock.AsyncMock)
@mock.patch("juju_spell.assignment.runner.get_result")
@pytest.mark.parametrize(
    "steps",
    [
        [],  # no controller
        [(MagicMock(), None, "OK", "OK")],
        [
            (MagicMock(), None, "run_output-1", "run_output-1"),
            (MagicMock(), "pre_check-1", None, "pre_check-1"),
            (MagicMock(), None, "run_output-2", "run_output-2"),
            (MagicMock(), "pre_check-2", None, "pre_check-2"),
            (MagicMock(), None, "run_output-3", "run_output-3"),
            (MagicMock(), "pre_check-3", None, "pre_check-3"),
        ],
    ],
)
async def test_run_serial(mock_get_result, mock_get_controller, steps):
    """Test run in serial."""
    config = mock.MagicMock()
    config.controllers = [controller_config for controller_config, _, _, _ in steps]
    command = mock.AsyncMock()
    command.pre_check.side_effect = [pre_check for _, pre_check, _, _ in steps]
    command.run.side_effect = [run for _, _, run, _ in steps if run]
    exp_result = [output for _, _, _, output in steps]
    # get_result returns output itself
    mock_get_result.side_effect = lambda controller_config, output: output

    result = await run_serial(config, command, argparse.Namespace())

    assert result == exp_result

    for controller_config, _, run_output, exp_output in steps:
        mock_get_controller.assert_has_awaits(
            [mock.call(controller_config, config.connection.get.return_value)]
        )
        command.pre_check.assert_has_awaits(
            [
                mock.call(
                    controller=mock_get_controller.return_value,
                    controller_config=controller_config,
                )
            ]
        )
        if run_output is not None:
            command.run.assert_has_awaits(
                [
                    mock.call(
                        controller=mock_get_controller.return_value,
                        controller_config=controller_config,
                    )
                ]
            )

        mock_get_result.assert_has_calls([mock.call(controller_config, exp_output)])
