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


class Filter:
    """Static class for filter."""

    filtered_clouds: list

    @staticmethod
    def filter_clouds(filter_input: str) -> list:
        """Filter the clouds according to filter rules.

        @param filter_input: input string from the --filter parameter
        @return: list of clouds
        """
        Filter.filtered_clouds = filter_input.split(",")
        return Filter.filtered_clouds
