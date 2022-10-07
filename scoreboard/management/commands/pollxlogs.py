from django.core.management.base import BaseCommand
from scoreboard.models import Source, Game
from django.db import transaction
from scoreboard.parsers import XlogParser
from tnnt.settings import XLOG_DIR
from pathlib import Path
import requests


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
            game = Game.objects.from_xlog(local_src, xlog_entry)
            # check None because a game may not have been produced
            # (explore/wizmode game, outside tournament time, etc)
            if game is not None:
                game.save()
                num_added += 1
        if src is not None:
            src.file_pos = xlog_file.tell()
            src.save()
        print('Created', num_added, 'Games from xlog file', path)


@transaction.atomic
def import_records(src):
    xlog_path = Path(XLOG_DIR) / src.local_file
    import_from_file(xlog_path, src)


def sync_local_file(url, local_file):
    xlog_path = Path(XLOG_DIR) / local_file
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
        if 'file' in options:
            import_from_file(options['file'], None)
        else:
            for src in sources:
                sync_local_file(src.location, src.local_file)
                import_records(src)
