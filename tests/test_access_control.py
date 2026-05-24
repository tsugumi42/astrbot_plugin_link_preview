from astrbot_plugin_link_preview.access_control import access_allowed
from astrbot_plugin_link_preview.access_control import parse_id_list


class FakeMessage:
    def __init__(self, *, group_id="", user_id="", raw_message=None):
        self.group_id = group_id
        self.user_id = user_id
        self.raw_message = raw_message or {}


class FakeEvent:
    def __init__(self, message):
        self.message_obj = message


def test_parse_id_list_accepts_commas_spaces_and_newlines():
    assert parse_id_list("1, 2\n3，4") == {"1", "2", "3", "4"}


def test_group_private_only_blocks_group():
    event = FakeEvent(FakeMessage(group_id="100"))
    assert not access_allowed(event, group_mode="private_only")


def test_group_whitelist_allows_only_listed_group():
    event = FakeEvent(FakeMessage(group_id="100"))
    assert access_allowed(event, group_mode="whitelist", group_ids="100,200")
    assert not access_allowed(event, group_mode="whitelist", group_ids="300")


def test_group_blacklist_blocks_listed_group():
    event = FakeEvent(FakeMessage(group_id="100"))
    assert not access_allowed(event, group_mode="blacklist", group_ids="100,200")


def test_private_blacklist_takes_priority():
    event = FakeEvent(FakeMessage(user_id="42"))
    assert not access_allowed(event, private_mode="all", private_blacklist="42")


def test_private_whitelist_takes_priority():
    event = FakeEvent(FakeMessage(user_id="42"))
    assert access_allowed(event, private_mode="none", private_whitelist="42")


def test_private_friends_allows_friend_subtype():
    event = FakeEvent(FakeMessage(user_id="42", raw_message={"sub_type": "friend"}))
    assert access_allowed(event, private_mode="friends")


def test_private_friends_blocks_group_or_stranger():
    event = FakeEvent(FakeMessage(user_id="42", raw_message={"sub_type": "group"}))
    assert not access_allowed(event, private_mode="friends")
