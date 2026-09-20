"""
Hermaniland: Football Draft Game - Players and Coaches Data Generator
"""

import random

# Top 100 football coaches of all time with attributes (1-100)
COACHES = [
    {"name": "Pep Guardiola", "era": "2000s-2020s", "attack": 92, "defense": 88, "adaptability": 95, "motivation": 90},
    {"name": "Carlo Ancelotti", "era": "1990s-2020s", "attack": 85, "defense": 88, "adaptability": 90, "motivation": 88},
    {"name": "Sir Alex Ferguson", "era": "1980s-2010s", "attack": 88, "defense": 85, "adaptability": 92, "motivation": 95},
    {"name": "Johan Cruyff", "era": "1980s-1990s", "attack": 95, "defense": 82, "adaptability": 88, "motivation": 85},
    {"name": "Arrigo Sacchi", "era": "1980s-1990s", "attack": 88, "defense": 92, "adaptability": 85, "motivation": 87},
    {"name": "Ernst Happel", "era": "1970s-1980s", "attack": 82, "defense": 90, "adaptability": 88, "motivation": 85},
    {"name": "Valeriy Lobanovskyi", "era": "1970s-1990s", "attack": 85, "defense": 92, "adaptability": 88, "motivation": 87},
    {"name": "Rinus Michels", "era": "1960s-1980s", "attack": 92, "defense": 85, "adaptability": 87, "motivation": 88},
    {"name": "Vicente del Bosque", "era": "1990s-2010s", "attack": 82, "defense": 87, "adaptability": 88, "motivation": 85},
    {"name": "Zinedine Zidane", "era": "2010s-2020s", "attack": 85, "defense": 82, "adaptability": 87, "motivation": 92},
    {"name": "Luis Enrique", "era": "2010s-2020s", "attack": 90, "defense": 85, "adaptability": 88, "motivation": 90},
    {"name": "Frank Rijkaard", "era": "1990s-2000s", "attack": 87, "defense": 90, "adaptability": 86, "motivation": 85},
    {"name": "Bobby Robson", "era": "1980s-2000s", "attack": 84, "defense": 86, "adaptability": 85, "motivation": 88},
    {"name": "Clive Woodward", "era": "1990s-2000s", "attack": 85, "defense": 87, "adaptability": 84, "motivation": 86},
    {"name": "Roy Hodgson", "era": "1990s-2010s", "attack": 80, "defense": 85, "adaptability": 85, "motivation": 83},
    {"name": "Fabio Capello", "era": "1990s-2010s", "attack": 82, "defense": 88, "adaptability": 83, "motivation": 87},
    {"name": "Guus Hiddink", "era": "1990s-2010s", "attack": 83, "defense": 86, "adaptability": 88, "motivation": 87},
    {"name": "Sven-Göran Eriksson", "era": "1990s-2010s", "attack": 81, "defense": 84, "adaptability": 85, "motivation": 84},
    {"name": "Nico Laporte", "era": "1950s-1960s", "attack": 85, "defense": 85, "adaptability": 82, "motivation": 84},
    {"name": "Helenio Herrera", "era": "1950s-1970s", "attack": 80, "defense": 90, "adaptability": 84, "motivation": 86},
] + [
    {"name": f"Coach {i}", "era": "Various", "attack": random.randint(75, 92),
     "defense": random.randint(75, 92), "adaptability": random.randint(75, 92),
     "motivation": random.randint(75, 92)} for i in range(21, 101)
]

# Sample of best players with positions and attributes (need 3000, using templates)
POSITIONS = ["GK", "CB", "LB", "RB", "CM", "CDM", "CAM", "LW", "RW", "ST", "CF"]

# Team colors (primary, secondary) for visualization
TEAM_COLORS = {
    "Santos": {"bg": "#FFD700", "text": "#000000"},
    "Argentina": {"bg": "#87CEEB", "text": "#000000"},
    "Napoli": {"bg": "#0047AB", "text": "#FFFFFF"},
    "Barcelona": {"bg": "#004B87", "text": "#FFC72C"},
    "Manchester United": {"bg": "#DA291C", "text": "#FFFFFF"},
    "Germany": {"bg": "#000000", "text": "#FFFFFF"},
    "Bayern Munich": {"bg": "#DC052D", "text": "#FFFFFF"},
    "Real Madrid": {"bg": "#FFFFFF", "text": "#000000"},
    "Ajax": {"bg": "#DC143C", "text": "#FFFFFF"},
    "France": {"bg": "#002395", "text": "#FFFFFF"},
    "Juventus": {"bg": "#000000", "text": "#FFFFFF"},
    "Liverpool": {"bg": "#C8102E", "text": "#FFFFFF"},
    "England": {"bg": "#0A3161", "text": "#FFFFFF"},
}

TOP_PLAYERS_SAMPLE = [
    # Legendary strikers
    {"name": "Pelé", "position": "ST", "era": "1950s-1970s", "speed": 90, "dribbling": 92, "shooting": 96, "defense": 45, "physical": 85, "iq": 88, "team": "Santos"},
    {"name": "Diego Maradona", "position": "LW", "era": "1980s-2000s", "speed": 92, "dribbling": 99, "shooting": 93, "defense": 50, "physical": 82, "iq": 96, "team": "Napoli"},
    {"name": "Cristiano Ronaldo", "position": "ST", "era": "2000s-2020s", "speed": 89, "dribbling": 87, "shooting": 93, "defense": 35, "physical": 92, "iq": 85, "team": "Manchester United"},
    {"name": "Lionel Messi", "position": "LW", "era": "2000s-2020s", "speed": 86, "dribbling": 96, "shooting": 94, "defense": 38, "physical": 73, "iq": 95, "team": "Barcelona"},
    {"name": "Johan Cruyff", "position": "CF", "era": "1960s-1980s", "speed": 88, "dribbling": 94, "shooting": 90, "defense": 40, "physical": 84, "iq": 97, "team": "Barcelona"},
    {"name": "Gerd Müller", "position": "ST", "era": "1960s-1970s", "speed": 82, "dribbling": 80, "shooting": 97, "defense": 30, "physical": 88, "iq": 85, "team": "Bayern Munich"},
    {"name": "Ferenc Puskás", "position": "CF", "era": "1940s-1960s", "speed": 85, "dribbling": 88, "shooting": 95, "defense": 35, "physical": 82, "iq": 88, "team": "Real Madrid"},
    {"name": "Zinedine Zidane", "position": "CAM", "era": "1990s-2000s", "speed": 85, "dribbling": 92, "shooting": 89, "defense": 60, "physical": 87, "iq": 94, "team": "Real Madrid"},

    # Legendary midfielders
    {"name": "Michel Platini", "position": "CM", "era": "1970s-1980s", "speed": 82, "dribbling": 85, "shooting": 88, "defense": 65, "physical": 84, "iq": 90, "team": "Juventus"},

    # Defenders
    {"name": "Franz Beckenbauer", "position": "CB", "era": "1960s-1980s", "speed": 85, "dribbling": 88, "shooting": 70, "defense": 95, "physical": 86, "iq": 96, "team": "Bayern Munich"},
    {"name": "Bobby Moore", "position": "CB", "era": "1960s-1970s", "speed": 80, "dribbling": 75, "shooting": 65, "defense": 94, "physical": 85, "iq": 95, "team": "England"},
    {"name": "Sergio Ramos", "position": "CB", "era": "2000s-2020s", "speed": 82, "dribbling": 75, "shooting": 75, "defense": 92, "physical": 89, "iq": 88, "team": "Real Madrid"},
    {"name": "Virgil van Dijk", "position": "CB", "era": "2010s-2020s", "speed": 88, "dribbling": 70, "shooting": 68, "defense": 94, "physical": 95, "iq": 90, "team": "Liverpool"},

    # Goalkeepers
    {"name": "Gianluigi Buffon", "position": "GK", "era": "1990s-2010s", "speed": 75, "dribbling": 40, "shooting": 30, "defense": 96, "physical": 88, "iq": 92, "team": "Juventus"},
]

def generate_players(count=3000):
    """Generate unique player database with realistic attributes by position"""
    # Best players unique for each position
    best_by_position = {
        "GK": [
            {"name": "Gianluigi Buffon", "speed": 75, "dribbling": 40, "shooting": 30, "defense": 96, "physical": 88, "iq": 92, "team": "Juventus"},
            {"name": "Manuel Neuer", "speed": 80, "dribbling": 60, "shooting": 35, "defense": 95, "physical": 92, "iq": 93, "team": "Bayern Munich"},
            {"name": "Iker Casillas", "speed": 77, "dribbling": 38, "shooting": 28, "defense": 94, "physical": 86, "iq": 90, "team": "Real Madrid"},
            {"name": "Lev Yashin", "speed": 76, "dribbling": 35, "shooting": 25, "defense": 97, "physical": 89, "iq": 91, "team": "Dynamo Moscow"},
            {"name": "Peter Shilton", "speed": 74, "dribbling": 32, "shooting": 20, "defense": 96, "physical": 88, "iq": 90, "team": "Nottingham Forest"},
            {"name": "Donnarumma", "speed": 78, "dribbling": 50, "shooting": 32, "defense": 93, "physical": 90, "iq": 88, "team": "AC Milan"},
            {"name": "De Gea", "speed": 76, "dribbling": 45, "shooting": 30, "defense": 92, "physical": 87, "iq": 87, "team": "Manchester United"},
            {"name": "Ederson", "speed": 82, "dribbling": 65, "shooting": 40, "defense": 91, "physical": 88, "iq": 89, "team": "Manchester City"},
        ],
        "CB": [
            {"name": "Franz Beckenbauer", "speed": 85, "dribbling": 88, "shooting": 70, "defense": 95, "physical": 86, "iq": 96, "team": "Bayern Munich"},
            {"name": "Sergio Ramos", "speed": 82, "dribbling": 75, "shooting": 75, "defense": 92, "physical": 89, "iq": 88, "team": "Real Madrid"},
            {"name": "Virgil van Dijk", "speed": 88, "dribbling": 70, "shooting": 68, "defense": 94, "physical": 95, "iq": 90, "team": "Liverpool"},
            {"name": "Bobby Moore", "speed": 80, "dribbling": 75, "shooting": 65, "defense": 94, "physical": 85, "iq": 95, "team": "England"},
            {"name": "Fabio Cannavaro", "speed": 80, "dribbling": 68, "shooting": 60, "defense": 96, "physical": 88, "iq": 91, "team": "Juventus"},
            {"name": "Maldini", "speed": 85, "dribbling": 80, "shooting": 65, "defense": 94, "physical": 89, "iq": 94, "team": "AC Milan"},
            {"name": "Rio Ferdinand", "speed": 82, "dribbling": 72, "shooting": 62, "defense": 93, "physical": 87, "iq": 92, "team": "Manchester United"},
            {"name": "John Terry", "speed": 81, "dribbling": 70, "shooting": 60, "defense": 93, "physical": 88, "iq": 91, "team": "Chelsea"},
        ],
        "LW": [
            {"name": "Diego Maradona", "speed": 92, "dribbling": 99, "shooting": 93, "defense": 50, "physical": 82, "iq": 96, "team": "Napoli"},
            {"name": "Lionel Messi", "speed": 86, "dribbling": 96, "shooting": 94, "defense": 38, "physical": 73, "iq": 95, "team": "Barcelona"},
            {"name": "Ronaldinho", "speed": 90, "dribbling": 97, "shooting": 92, "defense": 45, "physical": 85, "iq": 94, "team": "Barcelona"},
            {"name": "Arjen Robben", "speed": 92, "dribbling": 95, "shooting": 90, "defense": 42, "physical": 83, "iq": 90, "team": "Bayern Munich"},
            {"name": "Cristiano Ronaldo", "speed": 89, "dribbling": 87, "shooting": 93, "defense": 35, "physical": 92, "iq": 85, "team": "Manchester United"},
            {"name": "Franck Ribery", "speed": 88, "dribbling": 93, "shooting": 88, "defense": 40, "physical": 84, "iq": 89, "team": "Bayern Munich"},
            {"name": "Gareth Bale", "speed": 94, "dribbling": 88, "shooting": 89, "defense": 38, "physical": 90, "iq": 85, "team": "Real Madrid"},
            {"name": "Neymar Jr", "speed": 91, "dribbling": 94, "shooting": 87, "defense": 42, "physical": 80, "iq": 88, "team": "Barcelona"},
        ],
        "RW": [
            {"name": "Pelé", "speed": 90, "dribbling": 92, "shooting": 96, "defense": 45, "physical": 85, "iq": 88, "team": "Santos"},
            {"name": "George Best", "speed": 88, "dribbling": 94, "shooting": 91, "defense": 48, "physical": 84, "iq": 87, "team": "Manchester United"},
            {"name": "Stanley Matthews", "speed": 89, "dribbling": 96, "shooting": 88, "defense": 44, "physical": 82, "iq": 90, "team": "Blackpool"},
            {"name": "Vinicius Jr", "speed": 95, "dribbling": 91, "shooting": 86, "defense": 40, "physical": 88, "iq": 81, "team": "Real Madrid"},
            {"name": "Mohamed Salah", "speed": 89, "dribbling": 89, "shooting": 91, "defense": 35, "physical": 86, "iq": 87, "team": "Liverpool"},
            {"name": "Kingsley Coman", "speed": 91, "dribbling": 87, "shooting": 85, "defense": 42, "physical": 82, "iq": 86, "team": "Bayern Munich"},
            {"name": "Jadon Sancho", "speed": 90, "dribbling": 89, "shooting": 84, "defense": 41, "physical": 81, "iq": 85, "team": "Borussia Dortmund"},
            {"name": "Rafael Leao", "speed": 94, "dribbling": 90, "shooting": 85, "defense": 39, "physical": 87, "iq": 82, "team": "AC Milan"},
        ],
        "ST": [
            {"name": "Gerd Müller", "speed": 82, "dribbling": 80, "shooting": 97, "defense": 30, "physical": 88, "iq": 85, "team": "Bayern Munich"},
            {"name": "Ferenc Puskás", "speed": 85, "dribbling": 88, "shooting": 95, "defense": 35, "physical": 82, "iq": 88, "team": "Real Madrid"},
            {"name": "Karim Benzema", "speed": 84, "dribbling": 85, "shooting": 92, "defense": 32, "physical": 86, "iq": 89, "team": "Real Madrid"},
            {"name": "Robert Lewandowski", "speed": 83, "dribbling": 82, "shooting": 96, "defense": 33, "physical": 92, "iq": 88, "team": "Bayern Munich"},
            {"name": "Harry Kane", "speed": 81, "dribbling": 80, "shooting": 94, "defense": 35, "physical": 89, "iq": 90, "team": "Tottenham"},
            {"name": "Erling Haaland", "speed": 96, "dribbling": 84, "shooting": 95, "defense": 32, "physical": 94, "iq": 81, "team": "Manchester City"},
            {"name": "Sergio Aguero", "speed": 88, "dribbling": 85, "shooting": 93, "defense": 31, "physical": 84, "iq": 86, "team": "Manchester City"},
            {"name": "Thierry Henry", "speed": 92, "dribbling": 90, "shooting": 91, "defense": 33, "physical": 87, "iq": 88, "team": "Arsenal"},
        ],
    }

    first_names = [
        "Alessandro", "Antonio", "Carlo", "Diego", "Enrique", "Fernando", "Giancarlo", "Gustavo",
        "Hernan", "Ignacio", "Javier", "Julio", "Klaus", "Leonardo", "Marcelo", "Nicolas",
        "Olivier", "Paulo", "Quentin", "Raul", "Santiago", "Tiago", "Ubaldo", "Vicente",
        "Waldemar", "Xavier", "Yuri", "Zeljko", "Alberto", "Bruno", "Cristian", "Damian",
        "Emilio", "Federico", "Gustavo", "Hugo", "Ivan", "Jesus", "Klaus", "Luis",
        "Manuel", "Nestor", "Oscar", "Pablo", "Quirino", "Roberto", "Sergio", "Tomas",
    ]

    last_names = [
        "Alvarez", "Benites", "Carrillo", "Delgado", "Espinoza", "Fernandez", "Gonzalez", "Hernandez",
        "Iglesias", "Jimenez", "Kovalenko", "Lopez", "Martinez", "Nunez", "Ortiz", "Pacheco",
        "Quinones", "Ramirez", "Sanchez", "Torres", "Urbano", "Vargas", "Wagner", "Yanez",
        "Zamora", "Acosta", "Bernal", "Castro", "Duarte", "Esparza", "Flores", "Garza",
    ]

    players = []
    used_names = set()

    # Add best players first (unique, no duplicates)
    for position, best_players in best_by_position.items():
        for player in best_players:
            used_names.add(player["name"])
            players.append({**player, "position": position, "era": "Various"})

    # Generate candidates
    candidates = []
    for f in first_names:
        for l in last_names:
            candidates.append(f"{f} {l}")
    random.shuffle(candidates)

    # Distribution: GK=1000, CB=6000, LW=3000, RW=3000, ST=3000 (total 16000, but we take `count`)
    # For 3000 total, we scale proportionally
    distribution = {"GK": 0.063, "CB": 0.375, "LW": 0.188, "RW": 0.188, "ST": 0.188}
    targets = {pos: int(count * pct) for pos, pct in distribution.items()}

    position_counts = {pos: len(best_by_position[pos]) for pos in best_by_position}

    # Generate remaining players by position
    for name in candidates:
        if len(players) >= count:
            break
        if name not in used_names:
            used_names.add(name)

            # Pick position with fewest generated yet
            pos = min(distribution.keys(), key=lambda p: position_counts[p] - targets[p])

            if position_counts[pos] < targets[pos]:
                position_counts[pos] += 1
                era = random.choice(["1950s-1970s", "1970s-1990s", "1980s-2000s", "1990s-2010s", "2000s-2020s"])

                # Attributes by position
                if pos == "GK":
                    speed, dribbling, shooting, defense = random.randint(70, 82), random.randint(30, 50), random.randint(20, 40), random.randint(85, 99)
                elif pos == "CB":
                    speed, dribbling, shooting, defense = random.randint(75, 92), random.randint(60, 85), random.randint(40, 70), random.randint(85, 99)
                else:  # LW, RW, ST
                    speed, dribbling, shooting, defense = random.randint(80, 96), random.randint(75, 98), random.randint(80, 98), random.randint(25, 60)

                players.append({
                    "name": name,
                    "position": pos,
                    "era": era,
                    "speed": speed,
                    "dribbling": dribbling,
                    "shooting": shooting,
                    "defense": defense,
                    "physical": random.randint(70, 98),
                    "iq": random.randint(75, 98),
                    "team": random.choice(list(TEAM_COLORS.keys()))
                })

    return players[:count]

# Formations: (name, description, defender_count, midfielder_count, forward_count)
FORMATIONS = [
    {"name": "4-3-3", "description": "Classic balanced", "defenders": 4, "midfielders": 3, "forwards": 3},
    {"name": "4-2-4", "description": "Defensive midfield", "defenders": 4, "midfielders": 2, "forwards": 4},
    {"name": "3-5-2", "description": "Wing-heavy", "defenders": 3, "midfielders": 5, "forwards": 2},
    {"name": "5-3-2", "description": "Defensive", "defenders": 5, "midfielders": 3, "forwards": 2},
    {"name": "4-4-2", "description": "Classic", "defenders": 4, "midfielders": 4, "forwards": 2},
    {"name": "3-4-3", "description": "Attacking", "defenders": 3, "midfielders": 4, "forwards": 3},
]

if __name__ == "__main__":
    print("Generating 3000 players...")
    players = generate_players(3000)
    print(f"Generated {len(players)} players")
    print(f"Generated {len(COACHES)} coaches")
    print(f"Available formations: {len(FORMATIONS)}")
    print("\nSample players:")
    for p in players[:5]:
        print(f"  {p['name']} ({p['position']}) - Shooting: {p['shooting']}, Defense: {p['defense']}")
