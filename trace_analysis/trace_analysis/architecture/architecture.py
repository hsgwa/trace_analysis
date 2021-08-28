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

from __future__ import annotations

from typing import List, Optional

from trace_analysis.node import Node
from trace_analysis.communication import VariablePassing, Communication
from trace_analysis.architecture.interface import (
    ArchitectureImporter,
    ArchitectureExporter,
    PathAlias,
    ArchitectureInterface,
)
from trace_analysis.util import Util
from . import YamlArchitectureExporter, YamlArchitectureImporter, LttngArchitectureImporter
from trace_analysis.record import LatencyComposer

IGNORE_TOPICS = ["/parameter_events", "/rosout"]


class Architecture(ArchitectureInterface):
    def __init__(self):
        self._nodes: List[Node] = []
        self._path_aliases: List[PathAlias] = []
        self._communications: List[Communication] = []

    def export_file(self, file_path: str, file_type: str):
        assert file_type in ["yml", "yaml"]

        exporter: ArchitectureExporter
        if file_type in ["yml", "yaml"]:
            exporter = YamlArchitectureExporter()

        exporter.exec(self, file_path)

    def import_file(
        self,
        file_path: str,
        file_type: str,
        latency_composer: Optional[LatencyComposer],
        ignore_topics=IGNORE_TOPICS,
    ):
        # 小文字に揃える
        assert file_type in ["ctf", "lttng", "yml", "yaml"]

        importer: ArchitectureImporter
        if file_type in ["lttng", "ctf"]:
            importer = LttngArchitectureImporter(latency_composer)
        elif file_type in ["yml", "yaml"]:
            importer = YamlArchitectureImporter(latency_composer)

        importer.exec(file_path, ignore_topics)

        self._nodes = importer.nodes
        self._path_aliases = importer.path_aliases
        self._communications = importer.communications
        self._variable_passings = importer.variable_passings

    @property
    def nodes(self) -> List[Node]:
        return self._nodes

    @property
    def path_aliases(self) -> List[PathAlias]:
        return self._path_aliases

    @property
    def communications(self) -> List[Communication]:
        return self._communications

    @property
    def variable_passings(self) -> List[VariablePassing]:
        return Util.flatten([node.variable_passings for node in self._nodes])
