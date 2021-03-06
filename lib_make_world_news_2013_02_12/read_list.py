# -*- mode: python; coding: utf-8 -*-
#
# Copyright 2013 Andrej A Antonov <polymorphm@gmail.com>.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

assert str is not bytes

def read_list(path, read_words=None):
    if read_words is None:
        read_words = False
    
    with open(path, encoding='utf-8', errors='replace') as fd:
        for line in filter(None, map(lambda s: s.strip(), fd)):
            if read_words:
                for word in line.split():
                    # TODO: use ``yield from ...`` for Python 3.3+
                    yield word
            else:
                yield line

def map_read_list(map_func, *args, **kwargs):
    for line in filter(None, map(map_func, read_list(*args, **kwargs))):
        # TODO: use ``yield from ...`` for Python 3.3+
        yield line
