from django.core.management.base import BaseCommand
from scoreboard.models import Source, Game, Player, Conduct, Achievement
from django.db import transaction
from scoreboard.parsers import XlogParser
from tnnt import settings
from pathlib import Path
import requests
import sys
from datetime import datetime, timedelta, timezone

# xlogfile fields that have the same name in the Game model.
SIMPLE_XLOG_FIELDS = ['version', 'role', 'race', 'gender', 'align', 'points',
                      'turns', 'maxlvl', 'death', 'align0', 'gender0',
                      'deathlev']

class xlog_flags:
    WIZARD  = 0x1
    EXPLORE = 0x2
    NOBONES = 0x4

def game_from_xlog(source, xlog_dict):
    '''
    Create and save a Game from a dictionary of fields that comes from the xlog.
    This function contains the custom "business logic" of converting fields that
    are stored differently in Game than in the xlogfile, and also mapping to
    Player.

    Return 0 if no game was created, 1 if it was.

    `source` is a Source object that the resulting Game will be associated with.

    SIDE EFFECT: This searches for a player of the given name, and if they
    cannot be found, it will create that Player. (This is one of the two ways
    Players are naturally created.)
    '''

    kwargs = {'source': source}

    # filter explore/wizmode games
    if xlog_dict['flags'] & xlog_flags.WIZARD:
        print('Game not parsed because it was in wizard mode', file=sys.stderr)
        return 0
    if xlog_dict['flags'] & xlog_flags.EXPLORE:
        print('Game not parsed because it was in explore mode', file=sys.stderr)
        return 0

    # time/duration information
    # while doing this, also filter games that partially or completely fall
    # outside the time window of the tournament
    kwargs['starttime'] = datetime.fromtimestamp(xlog_dict['starttime'], timezone.utc)
    kwargs['endtime'] = datetime.fromtimestamp(xlog_dict['endtime'], timezone.utc)
    if kwargs['starttime'] < settings.TOURNAMENT_START:
        print('Game not parsed because it started before tournament start:',
              kwargs['starttime'], file=sys.stderr)
        return 0
    if kwargs['endtime'] > settings.TOURNAMENT_END:
        print('Game not parsed because it ended after tournament end:',
              kwargs['endtime'], file=sys.stderr)
        return 0
    kwargs['realtime'] = timedelta(seconds=xlog_dict['realtime'])
    kwargs['wallclock'] = kwargs['endtime'] - kwargs['starttime']

    # TODO: validate xlog_dict contains some set of 'required_fields'
    # simple fields get keyed directly to keyword args to Game.objects.create()
    for key in SIMPLE_XLOG_FIELDS:
        kwargs[key] = xlog_dict[key]

    # assign 'won' boolean
    if xlog_dict['achieve'] & 0x100:
        kwargs['won'] = True
    else:
        # a non-winning game is a splat if they had the amulet at some point
        # (we count escapes in celestial disgrace and any other
        # non-ascension end to the game as a splat)
        if xlog_dict['achieve'] & 0x20:
            kwargs['splatted'] = True

    # ditto for mines/soko
    if xlog_dict['achieve'] & 0x600:
        kwargs['mines_soko'] = True

    # find/create player
    try:
        player = Player.objects.get(name=xlog_dict['name'])
    except Player.DoesNotExist:
        player = Player(name=xlog_dict['name'], clan=None, clan_admin=False)
        player.save()
    kwargs['player'] = player

    game = Game.objects.create(**kwargs)
    for conduct in Conduct.objects.all():
        if conduct.xlogfield in xlog_dict and xlog_dict[conduct.xlogfield] & (1 << conduct.bit):
            game.conducts.add(conduct)
    for achieve in Achievement.objects.all():
        if achieve.xlogfield in xlog_dict and xlog_dict[achieve.xlogfield] & (1 << achieve.bit):
            game.achievements.add(achieve)

    game.save()
    return 1

def import_from_file(path, src):
    '''
    Turn all xlog records from the xlogfile at `path` into Game objects.
    If `src` isn't None, use its internal tracking of file positions and update
    it at the end. If it's None, ignore this.
    '''
    if src is None:
        # we still need SOMETHING to pass to from_xlog
        local_src = Source.objects.all()[0]
    else:
        local_src = src
    with Path(path).open("r") as xlog_file:
        if src is not None:
            xlog_file.seek(src.file_pos)
        num_added = 0
        for xlog_entry in XlogParser().parse(xlog_file):
            num_added += game_from_xlog(local_src, xlog_entry)
        print('Created', num_added, 'Games from xlog file', path)
        if src is not None:
            src.file_pos = xlog_file.tell()
            src.save()


@transaction.atomic
def import_records(src):
    xlog_path = Path(settings.XLOG_DIR) / src.local_file
    import_from_file(xlog_path, src)


def sync_local_file(url, local_file):
    xlog_path = Path(settings.XLOG_DIR) / local_file
    with xlog_path.open("ab") as xlog_file:
        r = requests.get(url, headers={"Range": f"bytes={xlog_file.tell()}-"})
        # 206 means they are honouring our Range request c:
        if r.status_code != 206:
            return
        for chunk in r.iter_content(chunk_size=128):
            xlog_file.write(chunk)


class Command(BaseCommand):
    help = "Poll Sources (xlogfiles) for new game data"

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            help='Load games from this xlog file instead of using sources in the database'
        )

    def handle(self, *args, **options):
        sources = Source.objects.all()
        if len(sources) == 0:
            raise RuntimeError('There are no sources in the database to poll!')
        if options.get('file') is not None:
            import_from_file(options['file'], None)
        else:
            for src in sources:
                sync_local_file(src.location, src.local_file)
                import_records(src)
