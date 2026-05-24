from astrbot_plugin_link_preview.status import event_group_id
from astrbot_plugin_link_preview.status import event_message_id


class FakeMessage:
    group_id = "10001"
    message_id = "20002"


class FakeEvent:
    message_obj = FakeMessage()


def test_event_group_id_from_message_obj():
    assert event_group_id(FakeEvent()) == "10001"


def test_event_message_id_from_message_obj():
    assert event_message_id(FakeEvent()) == "20002"
