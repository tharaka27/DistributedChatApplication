from models import serverstate
from models.userSession import UserSession
from controllers.JSONMessageBuilder import MessageBuilder
from algorithms.consensus import *
from flask import jsonify
from algorithms.fastbully import Bully
import json
import time

class consensusHandler:
    def __init__(self, LOCAL_SERVER_CONFIGURATION):
        self._protocol = "start_vote"
        self._suspectServerId = json_data["suspectServerId"]
        self_.serverId = json_data["id"]
        self._bully_instance = Bully._instance
        myServerId = LOCAL_SERVER_CONFIGURATION.getId()

    def handle(self):

        if self._suspectServerId in d:
            if (serverstate.SUSPECT_SERVERS[serverId] == Gossip.SUSPECTED):
                  String suspectServerId = (String) jsonMessage.get(Protocol.suspectserverid.toString());
                    String votedBy = (String) jsonMessage.get(Protocol.votedby.toString());
                    String vote = (String) jsonMessage.get(Protocol.vote.toString());

                    voteCount = serverstate.VOTE_SET[Consensus.Yes]

                    if (voteCount == None) {
                        serverstate.VOTE_SET[Consensus.Yes] = 1
                    } else {
                        serverstate.VOTE_SET[Consensus.Yes] = voteCount + 1
                    }
