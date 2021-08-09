""" Slack event handers. """
import os

import slack


class SlackAPI:
    """ Handles Slack interactions. """

    def __init__(self, api_token=None, client=None):
        if not api_token:
            api_token = os.environ["SLACK_API_TOKEN"]

        if not client:
            client = slack.WebClient(token=api_token)

        self.api_token = api_token
        self.client = client

    def send_message(self, channel, **kwargs):
        """ Sends a message to Slack via API. """
        kwargs.update({"channel": channel})
        response = self.client.chat_postMessage(**kwargs)

        if not response["ok"]:
            raise ValueError(f'send_to_slack failed: {response["error"]}')

    def update_usergroup(self, usergroup, users):
        """ Updates list of users on usergroup.
        usergroup: the name of the usergroup to update
        users: list of users to update
    """

        response = self.client.usergroups_list()
        usergroup = [u for u in response["usergroups"] if u["name"] == usergroup]
        try:
            usergroup_id = usergroup[0]["id"]
        except IndexError:
            raise ValueError(f"unknown usergroup {usergroup}") from None

        response = self.client.usergroups_users_update(
            usergroup=usergroup_id, users=users
        )

        return response["usergroup"]
