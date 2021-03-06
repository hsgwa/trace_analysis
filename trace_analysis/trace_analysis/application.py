# Copyright 2021 Research Institute of Systems Planning, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from typing import List, Dict

from itertools import product

from .util import Util

from trace_analysis.architecture import Architecture
from trace_analysis.node import Node
from trace_analysis.communication import VariablePassing, Communication
from trace_analysis.callback import CallbackBase
from trace_analysis.architecture.interface import PathAlias
from trace_analysis.path import Path
from trace_analysis.graph_search import CallbackPathSercher


class Application:
    def __init__(self, arch: Architecture):
        self.nodes: List[Node] = arch.nodes
        self.communications: List[Communication] = arch.communications
        self.variable_passings: List[VariablePassing] = arch.variable_passings
        self._path_searcher = CallbackPathSercher(
            arch.nodes, arch.communications, arch.variable_passings
        )
        self.path: Dict[str, Path] = self._to_paths(arch.path_aliases)
        self._set_node_paths(self.nodes)

    @property
    def paths(self) -> List[Path]:
        return list(self.path.values())

    def search_paths(
        self, start_callback_unique_name: str, end_callback_unique_name: str
    ) -> List[Path]:
        callbacks_paths: List[List[CallbackBase]] = self._path_searcher.search(
            start_callback_unique_name, end_callback_unique_name
        )
        paths: List[Path] = [self._to_path(callbacks) for callbacks in callbacks_paths]
        return paths

    def _to_path(self, callbacks: List[CallbackBase]) -> Path:
        return Path(callbacks, self.communications, self.variable_passings)

    def _to_callback(self, unique_name: str):
        return Util.find_one(self.callbacks, lambda x: x.unique_name == unique_name)

    def _set_node_paths(self, nodes):
        for node in nodes:
            for start_callback, end_callback in product(node.callbacks, node.callbacks):
                node.paths += self.search_paths(
                    start_callback.unique_name, end_callback.unique_name
                )

    def _to_paths(self, path_aliases: List[PathAlias]) -> Dict[str, Path]:
        path: Dict[str, Path] = {}
        for alias in path_aliases:
            callbacks = [self._to_callback(name) for name in alias.callback_names]
            path[alias.path_name] = self._to_path(callbacks)
        return path

    @property
    def callbacks(self) -> List[CallbackBase]:
        return Util.flatten([list(node.callbacks) for node in self.nodes])
