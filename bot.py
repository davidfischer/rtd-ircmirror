'''
This bot mirrors Read the Docs' IRC channel to slack

- This bot takes any message posted in #readthedocs on freenode
  and posts it into #ircbridge in Read the Docs' slack
- It is a one way integration - posting to slack does nothing
'''

import logging
import os

import irc.bot
import irc.strings
from slackclient import SlackClient


logger = logging.getLogger('RTDPythonBot')
IRC_PASSWORD = os.environ['IRC_PASSWORD']
SLACK_TOKEN = os.environ['SLACK_TOKEN']


class ReadTheDocsPythonBot(irc.bot.SingleServerIRCBot):
    def __init__(self, server='irc.freenode.net', port=6667):
        self.nick = 'RTDPythonBot'
        self.channel = '#readthedocs'

        self.slack_client = SlackClient(SLACK_TOKEN)

        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, IRC_PASSWORD)], self.nick, self.nick)

    def on_welcome(self, connection, event):
        logger.info(u'Joining channel %s', self.channel)
        connection.join(self.channel)

    def on_pubmsg(self, connection, event):
        message = event.arguments[0]
        source_nick = event.source.nick
        logger.info(u'Received message %s from %s', message, source_nick)

        self.slack_client.api_call(
            'chat.postMessage',
            channel='#ircbridge',
            text=message,
            as_user=False,
            username='{} (IRC)'.format(source_nick),
        )


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Read the Docs IRC Bot')
    parser.add_argument(
        '--server',
        dest='server',
        default='irc.freenode.net',
        help='Hostname for the IRC server [irc.freenode.net]',
    )
    parser.add_argument(
        '--port',
        dest='port',
        type=int,
        default=6667,
        help='Port for the IRC server [6667]',
    )

    args = parser.parse_args()

    logging.basicConfig(format='[%(asctime)s]: %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    bot = ReadTheDocsPythonBot(server=args.server, port=args.port)
    bot.start()

if __name__ == '__main__':
    main()
