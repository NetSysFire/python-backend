from tnnt.settings import UNIQUE_DEATH_REJECTIONS, UNIQUE_DEATH_NORMALIZATIONS
from django.db.models import Count, Min, Subquery, OuterRef
from scoreboard.models import Game
import re

def normalize(death):
    # Given a death string, apply normalizations from settings.
    for regtuple in UNIQUE_DEATH_NORMALIZATIONS:
        death = re.sub(regtuple[0], regtuple[1], death)
    return death

def reject(death):
    # Given a death string, return True if it should be excluded as a
    # unique death and False if not.
    for regex in UNIQUE_DEATH_REJECTIONS:
        if re.search(regex, death) is not None:
            return True
    return False

def compile_unique_deaths(gameQS):
    # Given a QuerySet of Game objects, return a set containing strings of all
    # the unique deaths from those games after rejections and normalizations are
    # applied.
    # This is primarily for aggregation (but is currently also used to show the
    # unique deaths on a player/clan page) and runs faster than
    # get_unique_death_details() that returns the players who first got a death
    # and when.

    # First, get all unique, un-normalized deaths.
    raw_uniq_deaths = \
        gameQS.values_list('death', flat=True).distinct()
    # Then apply normalizations and rejections, and turn it into a set
    # to automatically remove any duplicates produced by normalization.
    return set(normalize(d) for d in raw_uniq_deaths if not reject(d))

def get_unique_death_details():
    # For the Unique Deaths page. Goes more in-depth than just a list of unique
    # deaths for a player or clan.
    # Returns a list of dictionaries containing the death reason, name of the
    # earliest player who got that death, datetime they got that death, and the
    # total number of clans and players who have that death. The list is sorted
    # by death reason.

    # Subquery to find the earliest game associated with a given death. This is
    # not complete (because it lacks a .values() on the end) and that needs to
    # be added where it is used below.
    subq = Game.objects.values('death') \
                       .annotate(earliest=Min('endtime')) \
                       .filter(death=OuterRef('death'))

    # Then put it all together to obtain the fields we want to show.
    deathdetails = Game.objects.values('death').annotate(
        time=Subquery(subq.values('earliest')),
        earliest_plr=Subquery(subq.order_by('earliest').values('player__name')[:1]),
        nclans = Count('player__clan__name'),
        nplayers = Count('player__name')
    ).order_by('death', 'time')

    # Have to iterate over it here, because different raw deaths might normalize
    # to the same string and we don't want duplicates.
    output = {}

    for d in deathdetails:
        if reject(d['death']):
            continue

        normd = normalize(d['death'])
        if normd in output:
            # since we ordered by earliest, this must be a later death with a
            # different string that got normalized to the same thing; we don't
            # care about the player details, but do want to add the clan and
            # player count
            output[normd]['nclans'] += d['nclans']
            output[normd]['nplayers'] += d['nplayers']
            continue
        else:
            output[normd] = d
            # d[death] is still un-normalized, fix that
            output[normd]['death'] = normd

    return sorted([ value for key,value in output.items() ],
                  key=lambda deathdict: deathdict['death'])
