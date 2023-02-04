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
from unittest import mock
from unittest.mock import MagicMock

import pytest

from juju_spell.assignment.runner import get_result
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
