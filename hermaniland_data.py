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
    """Generate unique player database with realistic attributes from historical players"""
    # Extended list of real historical football players (unique individuals)
    historical_players = [
        "Ronaldinho Gaucho", "Ronaldo Nazario", "Zinedine Zidane", "Steven Gerrard", "Frank Lampard",
        "Pavel Nedved", "Patrick Vieira", "Roy Keane", "Paul Scholes", "Ricardo Kaka", "Luka Modric",
        "Toni Kroos", "Sergio Busquets", "Andres Iniesta", "Xavi Hernandez", "Luis Suarez", "Thierry Henry",
        "Karim Benzema", "Erling Haaland", "Harry Kane", "Robert Lewandowski", "Kylian Mbappe",
        "Neymar Jr", "Vinicius Jr", "Mohamed Salah", "Raheem Sterling", "Antoine Griezmann",
        "Gareth Bale", "Arjen Robben", "Franck Ribery", "Wesley Sneijder", "Bastian Schweinsteiger",
        "Iker Casillas", "Manuel Neuer", "Lev Yashin", "Roy Makaay", "Edin Dzeko", "Fabio Quagliarella",
        "Zlatan Ibrahimovic", "Edinson Cavani", "Fernando Torres", "David Villa", "Raul Gonzalez",
        "Morientes", "Hernan Crespo", "Didier Drogba", "Samuel Eto'o", "Sergio Aguero", "Jamie Vardy",
        "Riyad Mahrez", "David Beckham", "Ryan Giggs", "Carlos Tevez", "Javier Mascherano",
        "Sergio Ramos", "Gerard Pique", "Thiago Silva", "Vincent Kompany", "Rio Ferdinand",
        "Ashley Cole", "Patrice Evra", "Nery Pumpido", "Peter Shilton", "Dino Zoff",
        "Antonio Cabrini", "Gaetano Scirea", "Claudio Gentile", "Mark Hateley", "Tony Adams",
        "Desailly", "Maldini", "Costacurta", "Cannavaro", "Fabio Cannavaro", "Pablo Zabaleta",
        "Jaap Stam", "John Terry", "Nemanja Vidic", "Wes Brown", "Mikael Silvestre",
        "Juan Pablo Sorin", "Gianluca Zambrotta", "Sagna", "Sokratis", "Pepe",
        "Thiago Alcantara", "Javi Martinez", "Sami Khedira", "Darren Fletcher", "Michael Carrick",
        "Davor Suker", "Henrik Larsson", "Jimmy Floyd Hasselbaink", "Niall Quinn", "Peter Crouch",
        "Didier Drogba", "Florian Thauvin", "Kingsley Coman", "Alphonso Davies", "Joshua Kimmich",
        "Serge Gnabry", "Leroy Sane", "Marco Asensio", "Isco Alarcon", "Pablo Sarabia",
        "Jordi Alba", "Alvaro Morata", "Diego Costa", "David Silva", "Juan Mata",
        "Angel Di Maria", "Gonzalo Higuain", "Paulo Dybala", "Douglas Costa", "Medhi Benatia",
        "Juan Cuadrado", "Sandro", "Mandzukic", "Perisic", "Rakitic", "Modric",
        "Vidal", "Alexis Sanchez", "Danilo", "Marcelo", "Carvajal", "Varane",
        "Nacho Fernandez", "Casemiro", "Toni Kroos", "Luka Modric", "Isco",
        "Cristiano Ronaldo", "Benzema", "Di Maria", "Higuain", "Ozil",
        "Khedira", "Pepe", "Ramos", "Pique", "Mascherano", "Busquets",
        "Iniesta", "Xavi", "Messi", "Robben", "Ribery", "Muller",
        "Mandzukic", "Gomez", "Klose", "Ballack", "Podolski", "Lahm",
        "Boateng", "Badstuber", "Tasci", "Howedes", "Metzelder", "Dida",
        "Dudek", "Valdez", "Lehmann", "Fabianski", "Szczesny", "Sorensen",
        "Canizares", "Kalou", "Anelka", "Ballotelli", "Balzaretti", "Paletta",
        "Emanuelson", "Nocerino", "Montolivo", "Constant", "Zambrotta", "Thiago Motta",
        "Gattuso", "Pirlo", "Seedorf", "Ambrosini", "Nesta", "Stam",
        "Maldini", "Costacurta", "Baresi", "Riccardo Ferri", "Walter Zenga",
        "Abbiati", "Maignan", "Donnarumma", "Handanovic", "Samir Handanovic",
        "De Sanctis", "Buffon", "Marchetti", "Storari", "Sorrentino",
        "Chiellini", "Bonucci", "Barzagli", "Vidal", "Marchisio",
        "Pogba", "Juve", "Bayern", "Real", "Barcelona", "Arsenal",
        "Liverpool", "Manchester", "Chelsea", "Milan", "Inter",
        "Roma", "Napoli", "Juventus", "Lazio", "Fiorentina"
    ]

    # Add unique names by combining first and last names
    first_names = [
        "Alessandro", "Antonio", "Carlo", "Diego", "Enrique", "Fernando", "Giancarlo", "Gustavo",
        "Hernan", "Ignacio", "Javier", "Julio", "Klaus", "Leonardo", "Marcelo", "Nicolas",
        "Olivier", "Paulo", "Quentin", "Raul", "Santiago", "Tiago", "Ubaldo", "Vicente",
        "Waldemar", "Xavier", "Yuri", "Zeljko", "Alberto", "Bruno", "Cristian", "Diego",
        "Emilio", "Federico", "Gustavo", "Hugo", "Ivan", "Jesus", "Klaus", "Luis",
        "Manuel", "Nestor", "Oscar", "Pablo", "Quirino", "Roberto", "Sergio", "Tomas"
    ]

    last_names = [
        "Alvarez", "Benites", "Carrillo", "Delgado", "Espinoza", "Fernandez", "Gonzalez", "Hernandez",
        "Iglesias", "Jimenez", "Kovalenko", "Lopez", "Martinez", "Nunez", "Ortiz", "Pacheco",
        "Quinones", "Ramirez", "Sanchez", "Torres", "Urbano", "Vargas", "Wagner", "Yanez",
        "Zamora", "Acosta", "Bernal", "Castro", "Duarte", "Esparza", "Flores", "Garza",
        "Herrera", "Ibarra", "Jimenez", "Kimura", "Luna", "Molina", "Nava", "Ocampo",
        "Peña", "Quintanilla", "Reyes", "Silva", "Trevino", "Uribe", "Valencia", "Vega"
    ]

    players = TOP_PLAYERS_SAMPLE.copy()
    used_names = {p["name"] for p in players}

    # Generate unique players
    extra_needed = count - len(players)

    # Use historical players first
    for player_name in historical_players:
        if len(players) >= count:
            break
        if player_name not in used_names:
            used_names.add(player_name)
            position = random.choice(POSITIONS)
            era = random.choice(["1950s-1970s", "1970s-1990s", "1980s-2000s", "1990s-2010s", "2000s-2020s"])

            players.append({
                "name": player_name,
                "position": position,
                "era": era,
                "speed": random.randint(70, 96) if position not in ["GK"] else random.randint(70, 82),
                "dribbling": random.randint(30, 98) if position != "GK" else random.randint(30, 50),
                "shooting": random.randint(20, 98) if position != "GK" else random.randint(20, 40),
                "defense": random.randint(25, 99),
                "physical": random.randint(70, 98),
                "iq": random.randint(75, 98),
                "team": random.choice(list(TEAM_COLORS.keys()))
            })

    # Generate remaining with unique combinations (pre-generate to avoid collisions)
    candidates = []
    for f in first_names:
        for l in last_names:
            candidates.append(f"{f} {l}")

    random.shuffle(candidates)

    for name in candidates:
        if len(players) >= count:
            break
        if name not in used_names:
            used_names.add(name)
            position = random.choice(POSITIONS)
            era = random.choice(["1950s-1970s", "1970s-1990s", "1980s-2000s", "1990s-2010s", "2000s-2020s"])

            # Adjust attributes based on position
            if position == "GK":
                speed = random.randint(70, 82)
                dribbling = random.randint(30, 50)
                shooting = random.randint(20, 40)
                defense = random.randint(85, 99)
            elif position in ["CB", "LB", "RB"]:
                speed = random.randint(75, 92)
                dribbling = random.randint(60, 85)
                shooting = random.randint(40, 70)
                defense = random.randint(85, 99)
            elif position in ["CM", "CDM", "CAM"]:
                speed = random.randint(75, 92)
                dribbling = random.randint(70, 95)
                shooting = random.randint(65, 90)
                defense = random.randint(55, 85)
            else:  # LW, RW, ST, CF
                speed = random.randint(80, 96)
                dribbling = random.randint(75, 98)
                shooting = random.randint(80, 98)
                defense = random.randint(25, 60)

            physical = random.randint(70, 98)
            iq = random.randint(75, 98)
            team = random.choice(list(TEAM_COLORS.keys()))

            players.append({
                "name": name,
                "position": position,
                "era": era,
                "speed": speed,
                "dribbling": dribbling,
                "shooting": shooting,
                "defense": defense,
                "physical": physical,
                "iq": iq,
                "team": team
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
