# Copyright 2019 Robert Bosch GmbH
# Copyright 2020 Christophe Bedard
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

"""Module for trace events processor and ROS 2 model creation."""

from typing import Dict
from typing import Set
from typing import Tuple

from tracetools_read import get_field

from tracetools_analysis.processor import EventHandler
from tracetools_analysis.processor import EventMetadata
from tracetools_analysis.processor import HandlerMap
from .data_model import Ros2DataModel


class Ros2Handler(EventHandler):
    """
    ROS 2-aware event handling class implementation.

    Handles a trace's events and builds a model with the data.
    """

    def __init__(
        self,
        **kwargs,
    ) -> None:
        """Create a Ros2Handler."""
        # Link a ROS trace event to its corresponding handling method

        handler_map: HandlerMap = {}

        handler_map["ros2:rcl_init"] = self._handle_rcl_init
        handler_map["ros2:rcl_node_init"] = self._handle_rcl_node_init
        handler_map["ros2:rcl_publisher_init"] = \
            self._handle_rcl_publisher_init
        handler_map["ros2:rcl_subscription_init"] = \
            self._handle_rcl_subscription_init
        handler_map["ros2:rclcpp_subscription_init"] = \
            self._handle_rclcpp_subscription_init
        handler_map["ros2:rclcpp_subscription_callback_added"] = \
            self._handle_rclcpp_subscription_callback_added
        handler_map["ros2:rcl_service_init"] = \
            self._handle_rcl_service_init
        handler_map["ros2:rclcpp_service_callback_added"] = \
            self._handle_rclcpp_service_callback_added
        handler_map["ros2:rcl_client_init"] = \
            self._handle_rcl_client_init
        handler_map["ros2:rcl_timer_init"] = \
            self._handle_rcl_timer_init
        handler_map["ros2:rclcpp_timer_callback_added"] = \
            self._handle_rclcpp_timer_callback_added
        handler_map["ros2:rclcpp_timer_link_node"] = \
            self._handle_rclcpp_timer_link_node
        handler_map["ros2:rclcpp_callback_register"] = \
            self._handle_rclcpp_callback_register
        handler_map["ros2:callback_start"] = \
            self._handle_callback_start
        handler_map["ros2:callback_end"] = \
            self._handle_callback_end
        handler_map["ros2:rcl_lifecycle_state_machine_init"] = \
            self._handle_rcl_lifecycle_state_machine_init
        handler_map["ros2:rcl_lifecycle_transition"] = \
            self._handle_rcl_lifecycle_transition
        handler_map["ros2:rclcpp_publish"] = \
            self._handle_rclcpp_publish
        handler_map["ros2:message_construct"] = \
            self._handle_message_construct
        handler_map["ros2:rclcpp_intra_publish"] = \
            self._handle_rclcpp_intra_publish
        handler_map["ros2:dispatch"] = \
            self._handle_dispatch
        handler_map["ros2:dispatch_intra_process"] = \
            self._handle_dispatch_intra_process
        handler_map["ros2_hook:take_type_erased"] = \
            self._handle_take_type_erased
        handler_map["ros2_hook:on_data_available"] = \
            self._handle_on_data_available
        handler_map["ros2:rcl_publish"] = \
            self._handle_rcl_publish
        handler_map["ros2_hook:dds_write"] = \
            self._handle_dds_write
        handler_map["ros2_hook:dds_bind_addr_to_stamp"] = \
            self._handle_dds_bind_addr_to_stamp
        handler_map["ros2_hook:dds_bind_addr_to_addr"] = \
            self._handle_dds_bind_addr_to_addr

        super().__init__(
            handler_map=handler_map,
            data_model=Ros2DataModel(),
            **kwargs,
        )

        # Temporary buffers
        self._callback_instances: Dict[int, Tuple[Dict, EventMetadata]] = {}

    @staticmethod
    def required_events() -> Set[str]:
        return {
            "ros2:rcl_init",
        }

    @property
    def data(self) -> Ros2DataModel:
        return super().data  # type: ignore

    def _handle_rcl_init(
        self,
        event: Dict,
        metadata: EventMetadata,
    ) -> None:
        context_handle = get_field(event, "context_handle")
        timestamp = metadata.timestamp
        pid = metadata.pid
        version = get_field(event, "version")
        self.data.add_context(context_handle, timestamp, pid, version)

    def _handle_rcl_node_init(
        self,
        event: Dict,
        metadata: EventMetadata,
    ) -> None:
        handle = get_field(event, "node_handle")
        timestamp = metadata.timestamp
        tid = metadata.tid
        rmw_handle = get_field(event, "rmw_handle")
        name = get_field(event, "node_name")
        namespace = get_field(event, "namespace")
        self.data.add_node(handle, timestamp, tid, rmw_handle, name, namespace)

    def _handle_rcl_publisher_init(
        self,
        event: Dict,
        metadata: EventMetadata,
    ) -> None:
        handle = get_field(event, "publisher_handle")
        timestamp = metadata.timestamp
        node_handle = get_field(event, "node_handle")
        rmw_handle = get_field(event, "rmw_publisher_handle")
        topic_name = get_field(event, "topic_name")
        depth = get_field(event, "queue_depth")
        self.data.add_publisher(
            handle, timestamp, node_handle, rmw_handle, topic_name, depth
        )

    def _handle_rcl_subscription_init(
        self,
        event: Dict,
        metadata: EventMetadata,
    ) -> None:
        handle = get_field(event, "subscription_handle")
        timestamp = metadata.timestamp
        node_handle = get_field(event, "node_handle")
        rmw_handle = get_field(event, "rmw_subscription_handle")
        topic_name = get_field(event, "topic_name")
        depth = get_field(event, "queue_depth")
        self.data.add_rcl_subscription(
            handle,
            timestamp,
            node_handle,
            rmw_handle,
            topic_name,
            depth,
        )

    def _handle_rclcpp_subscription_init(
        self,
        event: Dict,
        metadata: EventMetadata,
    ) -> None:
        subscription_pointer = get_field(event, "subscription")
        timestamp = metadata.timestamp
        handle = get_field(event, "subscription_handle")
        self.data.add_rclcpp_subscription(
            subscription_pointer, timestamp, handle)

    def _handle_rclcpp_subscription_callback_added(
        self,
        event: Dict,
        metadata: EventMetadata,
    ) -> None:
        subscription_pointer = get_field(event, "subscription")
        timestamp = metadata.timestamp
        callback_object = get_field(event, "callback")
        self.data.add_callback_object(
            subscription_pointer, timestamp, callback_object)

    def _handle_rcl_service_init(
        self,
        event: Dict,
        metadata: EventMetadata,
    ) -> None:
        handle = get_field(event, "service_handle")
        timestamp = metadata.timestamp
        node_handle = get_field(event, "node_handle")
        rmw_handle = get_field(event, "rmw_service_handle")
        service_name = get_field(event, "service_name")
        self.data.add_service(
            handle, timestamp, node_handle, rmw_handle, service_name)

    def _handle_rclcpp_service_callback_added(
        self,
        event: Dict,
        metadata: EventMetadata,
    ) -> None:
        handle = get_field(event, "service_handle")
        timestamp = metadata.timestamp
        callback_object = get_field(event, "callback")
        self.data.add_callback_object(handle, timestamp, callback_object)

    def _handle_rcl_client_init(
        self,
        event: Dict,
        metadata: EventMetadata,
    ) -> None:
        handle = get_field(event, "client_handle")
        timestamp = metadata.timestamp
        node_handle = get_field(event, "node_handle")
        rmw_handle = get_field(event, "rmw_client_handle")
        service_name = get_field(event, "service_name")
        self.data.add_client(handle, timestamp, node_handle,
                             rmw_handle, service_name)

    def _handle_rcl_timer_init(
        self,
        event: Dict,
        metadata: EventMetadata,
    ) -> None:
        handle = get_field(event, "timer_handle")
        timestamp = metadata.timestamp
        period = get_field(event, "period")
        tid = metadata.tid
        self.data.add_timer(handle, timestamp, period, tid)

    def _handle_rclcpp_timer_callback_added(
        self,
        event: Dict,
        metadata: EventMetadata,
    ) -> None:
        handle = get_field(event, "timer_handle")
        timestamp = metadata.timestamp
        callback_object = get_field(event, "callback")
        self.data.add_callback_object(handle, timestamp, callback_object)

    def _handle_rclcpp_timer_link_node(
        self,
        event: Dict,
        metadata: EventMetadata,
    ) -> None:
        handle = get_field(event, "timer_handle")
        timestamp = metadata.timestamp
        node_handle = get_field(event, "node_handle")
        self.data.add_timer_node_link(handle, timestamp, node_handle)

    def _handle_rclcpp_callback_register(
        self,
        event: Dict,
        metadata: EventMetadata,
    ) -> None:
        callback_object = get_field(event, "callback")
        timestamp = metadata.timestamp
        symbol = get_field(event, "symbol")
        self.data.add_callback_symbol(callback_object, timestamp, symbol)

    def _handle_callback_start(
        self,
        event: Dict,
        metadata: EventMetadata,
    ) -> None:
        # Add to dict
        callback = get_field(event, "callback")
        timestamp = metadata.timestamp
        is_intra_process = get_field(
            event, "is_intra_process", raise_if_not_found=False
        )
        self.data.add_callback_start_instance(
            timestamp, callback, is_intra_process)

    def _handle_callback_end(
        self,
        event: Dict,
        metadata: EventMetadata,
    ) -> None:
        # Fetch from dict
        callback = get_field(event, "callback")
        timestamp = metadata.timestamp
        self.data.add_callback_end_instance(timestamp, callback)

    def _handle_rcl_lifecycle_state_machine_init(
        self,
        event: Dict,
        metadata: EventMetadata,
    ) -> None:
        node_handle = get_field(event, "node_handle")
        state_machine = get_field(event, "state_machine")
        self.data.add_lifecycle_state_machine(state_machine, node_handle)

    def _handle_rcl_lifecycle_transition(
        self,
        event: Dict,
        metadata: EventMetadata,
    ) -> None:
        timestamp = metadata.timestamp
        state_machine = get_field(event, "state_machine")
        start_label = get_field(event, "start_label")
        goal_label = get_field(event, "goal_label")
        self.data.add_lifecycle_state_transition(
            state_machine, start_label, goal_label, timestamp
        )

    def _handle_rclcpp_publish(
        self,
        event: Dict,
        metadata: EventMetadata,
    ) -> None:
        publisher_handle = get_field(event, "publisher_handle")
        timestamp = metadata.timestamp
        message = get_field(event, "message")
        self.data.add_rclcpp_publish_instance(
            timestamp, publisher_handle, message)

    def _handle_rcl_publish(
        self,
        event: Dict,
        metadata: EventMetadata,
    ) -> None:
        publisher_handle = get_field(event, "publisher_handle")
        timestamp = metadata.timestamp
        message = get_field(event, "message")
        self.data.add_rcl_publish_instance(
            timestamp, publisher_handle, message)

    def _handle_message_construct(
        self,
        event: Dict,
        metadata: EventMetadata,
    ) -> None:
        original_message = get_field(event, "original_message")
        constructed_message = get_field(event, "constructed_message")
        timestamp = metadata.timestamp
        self.data.add_message_construct_instance(
            timestamp, original_message, constructed_message
        )

    def _handle_rclcpp_intra_publish(
        self,
        event: Dict,
        metadata: EventMetadata,
    ) -> None:
        message = get_field(event, "message")
        publisher_handle = get_field(event, "publisher_handle")
        timestamp = metadata.timestamp
        self.data.add_rclcpp_intra_publish_instance(
            timestamp, publisher_handle, message
        )

    def _handle_dispatch(
        self,
        event: Dict,
        metadata: EventMetadata,
    ) -> None:
        callback_object = get_field(event, "callback")
        message = get_field(event, "message")
        timestamp = metadata.timestamp
        self.data.add_dispatch_instance(timestamp, callback_object, message)

    def _handle_dispatch_intra_process(
        self,
        event: Dict,
        metadata: EventMetadata,
    ) -> None:
        callback_object = get_field(event, "callback")
        message = get_field(event, "message")
        timestamp = metadata.timestamp
        self.data.add_dispatch_intra_process_instance(
            timestamp, callback_object, message
        )

    def _handle_take_type_erased(
        self,
        event: Dict,
        metadata: EventMetadata,
    ) -> None:
        message = get_field(event, "message")
        source_stamp = get_field(event, "source_stamp")
        timestamp = metadata.timestamp
        self.data.add_take_type_erased_instance(
            timestamp, source_stamp, message)

    def _handle_on_data_available(
        self,
        event: Dict,
        metadata: EventMetadata,
    ) -> None:
        timestamp = metadata.timestamp
        source_stamp = get_field(event, "source_stamp")
        self.data.add_on_data_available_instance(timestamp, source_stamp)

    def _handle_dds_write(
        self,
        event: Dict,
        metadata: EventMetadata,
    ) -> None:
        timestamp = metadata.timestamp
        message = get_field(event, "message")
        self.data.add_dds_write_instance(timestamp, message)

    def _handle_dds_bind_addr_to_stamp(
        self,
        event: Dict,
        metadata: EventMetadata,
    ) -> None:
        timestamp = metadata.timestamp
        addr = get_field(event, "addr")
        source_stamp = get_field(event, "source_stamp")
        self.data.add_dds_bind_addr_to_stamp(timestamp, addr, source_stamp)

    def _handle_dds_bind_addr_to_addr(
        self,
        event: Dict,
        metadata: EventMetadata,
    ) -> None:
        timestamp = metadata.timestamp
        addr_from = get_field(event, "addr_from")
        addr_to = get_field(event, "addr_to")
        self.data.add_dds_bind_addr_to_addr(timestamp, addr_from, addr_to)

    def _handle_ros_time(
        self,
        event: Dict,
        metadata: EventMetadata,
    ) -> None:
        rostime = get_field(event, "stamp")
        stamp = metadata.timestamp
        self.data.add_ros_time(stamp, rostime)
