# # pylint: disable=C0111
# import os
# from unittest.mock import Mock

# import pytest

# from lib.slackapi import SlackAPI


# @pytest.fixture
# def slack_client_mock():
#     mock = Mock()
#     mock.usergroups_list.return_value = {
#         "usergroups": [
#             {"name": "group1", "id": "group1id"},
#             {"name": "my-group", "id": "my-groupid"},
#         ]
#     }
#     mock.chat_postMessage.return_value = {"ok": "true"}
#     return mock


# @pytest.fixture
# def slack(slack_client_mock):
#     return SlackAPI("someapitoken", slack_client_mock)


# def test_init_uses_environment_by_default():
#     os.environ["SLACK_API_TOKEN"] = "myapitoken"
#     slack = SlackAPI()
#     assert slack.api_token == "myapitoken"


# def test_init_accepts_parameters():
#     slack = SlackAPI("anotherapitoken")
#     assert slack.api_token == "anotherapitoken"


# def test_send_message_sends_a_message_successfully(slack, slack_client_mock):
#     slack.send_message("my-channel", text="hello world")

#     slack_client_mock.chat_postMessage.assert_called_once_with(
#         channel="my-channel", text="hello world"
#     )


# def test_send_message_raises_exception_on_error(slack, slack_client_mock):
#     slack_client_mock.chat_postMessage.return_value = {
#         "ok": False,
#         "error": "something bad happened",
#     }
#     with pytest.raises(ValueError, match="something bad happened"):
#         slack.send_message({})


# def test_update_usergroup_with_valid_group_updates_list(slack, slack_client_mock):
#     slack_client_mock.usergroups_users_update.return_value = {
#         "ok": "true",
#         "usergroup": {"id": "my-group-id",},
#     }
#     result = slack.update_usergroup("my-group", "U1S2BBC0L")
#     slack_client_mock.usergroups_users_update.assert_called_with(
#         usergroup="my-groupid", users="U1S2BBC0L"
#     )
#     assert result == {"id": "my-group-id"}


# def test_update_usergroup_with_invalid_group_updates_list(slack):
#     with pytest.raises(ValueError):
#         result = slack.update_usergroup("unknown-group", "U1S2BBC0L")
#         assert result is None
