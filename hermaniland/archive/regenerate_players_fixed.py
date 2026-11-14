#!/usr/bin/env python3
"""Regenerate hermaniland_players_*.py with CORRECT positions for famous players."""

import csv
import json

POSITION_GROUPS = {
    'GK': ['GK'],
    'DEF': ['CB', 'LB', 'RB'],
    'MID': ['CM', 'CDM', 'CAM'],
    'FWD': ['ST', 'CF', 'LW', 'RW']
}

# Manual corrections for famous players (base name -> correct position)
PLAYER_CORRECTIONS = {
    'Cristiano Ronaldo': 'ST',
    'Gianluigi Buffon': 'GK',
    'Lionel Messi': 'LW',
}

def score_player(row):
    """Score a player based on their stats."""
    stats = [
        float(row.get('speed', 0)),
        float(row.get('dribbling', 0)),
        float(row.get('shooting', 0)),
        float(row.get('defense', 0)),
        float(row.get('physical', 0)),
        float(row.get('iq', 0))
    ]
    return sum(stats) / len(stats) if stats else 0

def read_and_organize_players():
    """Read CSV and organize players by position group."""
    organized = {
        'GK': [],
        'DEF': [],
        'MID': [],
        'FWD': []
    }

    with open('/home/user/Bsynch/hermaniland_players_7500.csv', 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # First pass: find best variants of famous players and add them
    for base_name in PLAYER_CORRECTIONS:
        best_score = -1
        best_player = None
        best_group = None

        for row in rows:
            name = row['name'].strip()
            row_base_name = name.split(' #')[0].strip()

            if row_base_name == base_name:
                pos = PLAYER_CORRECTIONS[base_name]
                score = score_player(row)

                if score > best_score:
                    best_score = score

                    # Find which group this position belongs to
                    group = None
                    for g, positions in POSITION_GROUPS.items():
                        if pos in positions:
                            group = g
                            break

                    if group:
                        best_player = {
                            'name': base_name,
                            'position': pos,
                            'speed': int(float(row.get('speed', 0))),
                            'dribbling': int(float(row.get('dribbling', 0))),
                            'shooting': int(float(row.get('shooting', 0))),
                            'defense': int(float(row.get('defense', 0))),
                            'physical': int(float(row.get('physical', 0))),
                            'iq': int(float(row.get('iq', 0))),
                            'team': row.get('team', 'Unknown'),
                            'era': row.get('era', '2020'),
                            'rating': score
                        }
                        best_group = group

        if best_player and best_group:
            organized[best_group].append((best_score, best_player))

    # Second pass: add all other players
    skip_bases = set(PLAYER_CORRECTIONS.keys())

    for row in rows:
        name = row['name'].strip()
        base_name = name.split(' #')[0].strip()

        # Skip famous players (already added)
        if base_name in skip_bases:
            continue

        pos = row.get('position', '').upper()
        score = score_player(row)

        # Find which group this position belongs to
        group = None
        for g, positions in POSITION_GROUPS.items():
            if pos in positions:
                group = g
                break

        if not group:
            continue

        player = {
            'name': name,  # Keep variant names (with #)
            'position': pos,
            'speed': int(float(row.get('speed', 0))),
            'dribbling': int(float(row.get('dribbling', 0))),
            'shooting': int(float(row.get('shooting', 0))),
            'defense': int(float(row.get('defense', 0))),
            'physical': int(float(row.get('physical', 0))),
            'iq': int(float(row.get('iq', 0))),
            'team': row.get('team', 'Unknown'),
            'era': row.get('era', '2020'),
            'rating': score
        }
        organized[group].append((score, player))

    # Sort by score and keep top N per group
    TARGET_COUNTS = {'GK': 50, 'DEF': 165, 'MID': 248, 'FWD': 167}
    for group in organized:
        organized[group].sort(reverse=True, key=lambda x: x[0])
        organized[group] = [p for _, p in organized[group][:TARGET_COUNTS[group]]]

    return organized

def generate_gk_file(players):
    """Generate hermaniland_players_gk.py"""
    code = '''"""Hermaniland - GK Players Database"""

def get_goalkeepers():
    return [
'''
    for p in players:
        code += f"        {{'name': {json.dumps(p['name'])}, 'position': {json.dumps(p['position'])}, 'speed': {p['speed']}, 'dribbling': {p['dribbling']}, 'shooting': {p['shooting']}, 'defense': {p['defense']}, 'physical': {p['physical']}, 'iq': {p['iq']}, 'team': {json.dumps(p['team'])}, 'era': {json.dumps(p['era'])}, 'rating': {p['rating']}}},\n"
    code += '''    ]
'''
    return code

def generate_def_file(players):
    """Generate hermaniland_players_def.py"""
    code = '''"""Hermaniland - DEF Players Database"""

def get_defenders():
    return [
'''
    for p in players:
        code += f"        {{'name': {json.dumps(p['name'])}, 'position': {json.dumps(p['position'])}, 'speed': {p['speed']}, 'dribbling': {p['dribbling']}, 'shooting': {p['shooting']}, 'defense': {p['defense']}, 'physical': {p['physical']}, 'iq': {p['iq']}, 'team': {json.dumps(p['team'])}, 'era': {json.dumps(p['era'])}, 'rating': {p['rating']}}},\n"
    code += '''    ]
'''
    return code

def generate_mid_file(players):
    """Generate hermaniland_players_mid.py"""
    code = '''"""Hermaniland - MID Players Database"""

def get_midfielders():
    return [
'''
    for p in players:
        code += f"        {{'name': {json.dumps(p['name'])}, 'position': {json.dumps(p['position'])}, 'speed': {p['speed']}, 'dribbling': {p['dribbling']}, 'shooting': {p['shooting']}, 'defense': {p['defense']}, 'physical': {p['physical']}, 'iq': {p['iq']}, 'team': {json.dumps(p['team'])}, 'era': {json.dumps(p['era'])}, 'rating': {p['rating']}}},\n"
    code += '''    ]
'''
    return code

def generate_fwd_file(players):
    """Generate hermaniland_players_fwd.py"""
    code = '''"""Hermaniland - FWD Players Database"""

def get_forwards():
    return [
'''
    for p in players:
        code += f"        {{'name': {json.dumps(p['name'])}, 'position': {json.dumps(p['position'])}, 'speed': {p['speed']}, 'dribbling': {p['dribbling']}, 'shooting': {p['shooting']}, 'defense': {p['defense']}, 'physical': {p['physical']}, 'iq': {p['iq']}, 'team': {json.dumps(p['team'])}, 'era': {json.dumps(p['era'])}, 'rating': {p['rating']}}},\n"
    code += '''    ]
'''
    return code

if __name__ == '__main__':
    print("Regenerating player files with CORRECT positions...")
    organized = read_and_organize_players()

    # Verify famous players
    print("\nVerifying famous players:")
    all_players = organized['GK'] + organized['DEF'] + organized['MID'] + organized['FWD']
    for test_name in ['Cristiano Ronaldo', 'Gianluigi Buffon', 'Lionel Messi']:
        found = [p for p in all_players if p['name'] == test_name]
        if found:
            print(f"  ✓ {test_name}: {found[0]['position']}")
        else:
            print(f"  ✗ {test_name}: NOT FOUND")

    # Write each file
    with open('/home/user/Bsynch/hermaniland_players_gk.py', 'w') as f:
        f.write(generate_gk_file(organized['GK']))
    print(f"\n✓ Generated hermaniland_players_gk.py ({len(organized['GK'])} goalkeepers)")

    with open('/home/user/Bsynch/hermaniland_players_def.py', 'w') as f:
        f.write(generate_def_file(organized['DEF']))
    print(f"✓ Generated hermaniland_players_def.py ({len(organized['DEF'])} defenders)")

    with open('/home/user/Bsynch/hermaniland_players_mid.py', 'w') as f:
        f.write(generate_mid_file(organized['MID']))
    print(f"✓ Generated hermaniland_players_mid.py ({len(organized['MID'])} midfielders)")

    with open('/home/user/Bsynch/hermaniland_players_fwd.py', 'w') as f:
        f.write(generate_fwd_file(organized['FWD']))
    print(f"✓ Generated hermaniland_players_fwd.py ({len(organized['FWD'])} forwards)")

    total = sum(len(organized[g]) for g in organized)
    print(f"\n✓ Total players: {total}")
