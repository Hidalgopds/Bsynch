"""Hermaniland - Legendary Coaches Database

Additional legendary coaches for elite game modes.
Includes historic and modern coaching legends.
"""

LEGENDARY_COACHES = [
    {"name": "Oliver Kahn", "rating": 95, "era": "2000s", "specialty": "Goalkeeper Master"},
    {"name": "Franz Beckenbauer", "rating": 96, "era": "1970s", "specialty": "Defense Innovator"},
    {"name": "Torsten Fings", "rating": 92, "era": "1950s", "specialty": "Tactical Genius"},
    {"name": "Salihamiachick", "rating": 91, "era": "1980s", "specialty": "Midfield Control"},
    {"name": "Efember", "rating": 90, "era": "1990s", "specialty": "Attack Coordinator"},
    {"name": "Sir Alex Ferguson", "rating": 98, "era": "1980s-2013", "specialty": "Winning Culture"},
    {"name": "Arsène Wenger", "rating": 94, "era": "1996-2018", "specialty": "Player Development"},
    {"name": "Marcelo Bielsa", "rating": 95, "era": "2000s-present", "specialty": "Tactical Innovation"},
    {"name": "Diego Simeone", "rating": 93, "era": "2011-present", "specialty": "Defense Mastery"},
    {"name": "Carlo Ancelotti", "rating": 94, "era": "1995-present", "specialty": "Experience"},
    {"name": "Zinedine Zidane", "rating": 96, "era": "2016-2021", "specialty": "Champions Leader"},
    {"name": "Hansi Flick", "rating": 93, "era": "2019-present", "specialty": "Possession Play"},
    {"name": "Simone Inzaghi", "rating": 91, "era": "2021-present", "specialty": "Attack Fluidity"},
    {"name": "Xavi Hernández", "rating": 92, "era": "2021-present", "specialty": "Tiki-taka Expert"},
    {"name": "Luis Enrique", "rating": 93, "era": "2008-present", "specialty": "Pressing System"},
]

def get_legendary_coaches():
    """Return all legendary coaches"""
    return LEGENDARY_COACHES

def get_all_coaches_combined():
    """Return legendary coaches combined with standard coaches"""
    from hermaniland_data import COACHES
    return COACHES + LEGENDARY_COACHES
