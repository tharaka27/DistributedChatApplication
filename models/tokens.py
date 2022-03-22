import enum
# Using enum class create enumerations
class Consensus(enum.Enum):
   Yes = 1
   No = 2

class Gossip(enum.Enum):
    SUSPECTED = 1
    NOT_SUSPECTED = 2