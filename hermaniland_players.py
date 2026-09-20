"""Hermaniland - Unified Players Database by Position

Combined database with 621 real verified football players across 4 categories:
- Goalkeepers (GK): 41 players
- Defenders (DEF): 165 players
- Midfielders (MID): 248 players
- Forwards (FWD): 167 players
"""

from hermaniland_players_gk import get_goalkeepers
from hermaniland_players_def import get_defenders
from hermaniland_players_mid import get_midfielders
from hermaniland_players_fwd import get_forwards

# Cache for all players by position
_CACHE = {
    'GK': None,
    'DEF': None,
    'MID': None,
    'FWD': None,
    'ALL': None
}

def _build_cache():
    """Build cache of all players by position"""
    if _CACHE['ALL'] is None:
        _CACHE['GK'] = get_goalkeepers()
        _CACHE['DEF'] = get_defenders()
        _CACHE['MID'] = get_midfielders()
        _CACHE['FWD'] = get_forwards()
        _CACHE['ALL'] = _CACHE['GK'] + _CACHE['DEF'] + _CACHE['MID'] + _CACHE['FWD']
    return _CACHE

def get_players_by_position(position='ALL'):
    """
    Get players filtered by position.

    Args:
        position: 'GK', 'DEF', 'MID', 'FWD', or 'ALL' (default)

    Returns:
        List of player dictionaries
    """
    cache = _build_cache()
    position = position.upper()

    if position in cache:
        return cache[position]
    return cache['ALL']

def get_all_players():
    """Get all players across all positions"""
    cache = _build_cache()
    return cache['ALL']

def search_players(query, position='ALL'):
    """
    Search players by name and optionally filter by position.

    Args:
        query: Search string (case-insensitive, partial match)
        position: 'GK', 'DEF', 'MID', 'FWD', or 'ALL' (default)

    Returns:
        List of matching player dictionaries
    """
    players = get_players_by_position(position)
    query_lower = query.lower().strip()

    if not query_lower:
        return players

    # Search by name (partial match, case-insensitive)
    results = [p for p in players if query_lower in p['name'].lower()]
    return results

def get_stats():
    """Get database statistics"""
    cache = _build_cache()
    return {
        'total': len(cache['ALL']),
        'gk': len(cache['GK']),
        'def': len(cache['DEF']),
        'mid': len(cache['MID']),
        'fwd': len(cache['FWD'])
    }
