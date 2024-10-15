# Given a dumplog format, player name, and datetime object representing the
# start time of one of that player's games, return a valid dumplog URL.
#
# Ideally this would live in hardfought_utils.py but circular import errors with
# models.py prevent that. If dumplogs are ever stored as part of Games, this
# will no longer be called from models.py and it can be moved to
# hardfought_utils.
def format_dumplog(fmt, playername, starttime):
    return fmt.replace('%n1', playername[0]) \
              .replace('%n', playername) \
              .replace('%st', str(int(starttime.timestamp())))
