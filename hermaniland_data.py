"""
Hermaniland: Football Draft Game - Professional Real Players Database
7500 unique professional players from all eras and regions
"""

import random

COACHES = [
    {"name": "Pep Guardiola", "era": "2000s-2020s", "attack": 92, "defense": 88, "adaptability": 95, "motivation": 90},
    {"name": "Carlo Ancelotti", "era": "1990s-2020s", "attack": 85, "defense": 88, "adaptability": 90, "motivation": 88},
    {"name": "Sir Alex Ferguson", "era": "1980s-2010s", "attack": 88, "defense": 85, "adaptability": 92, "motivation": 95},
] + [
    {"name": f"Coach {i}", "era": "Various", "attack": random.randint(75, 92),
     "defense": random.randint(75, 92), "adaptability": random.randint(75, 92),
     "motivation": random.randint(75, 92)} for i in range(4, 101)
]

POSITIONS = ["GK", "CB", "LB", "RB", "CM", "CDM", "CAM", "LW", "RW", "ST", "CF"]

TEAM_COLORS = {
    "Barcelona": {"bg": "#004B87", "text": "#FFC72C"},
    "Real Madrid": {"bg": "#FFFFFF", "text": "#000000"},
    "Bayern Munich": {"bg": "#DC052D", "text": "#FFFFFF"},
    "Manchester United": {"bg": "#DA291C", "text": "#FFFFFF"},
    "Liverpool": {"bg": "#C8102E", "text": "#FFFFFF"},
    "Arsenal": {"bg": "#EF0107", "text": "#FFFFFF"},
    "Chelsea": {"bg": "#034694", "text": "#FFFFFF"},
    "AC Milan": {"bg": "#DC143C", "text": "#FFFFFF"},
    "Juventus": {"bg": "#000000", "text": "#FFFFFF"},
    "Inter Milan": {"bg": "#000000", "text": "#00A2E8"},
    "Paris SG": {"bg": "#004494", "text": "#FFFFFF"},
    "Napoli": {"bg": "#0047AB", "text": "#FFFFFF"},
}

# Real professional first and last names from football history
FIRST_NAMES = [
    "Gianluigi", "Manuel", "Iker", "Lev", "Peter", "Edwin", "Petr", "Oliver", "David", "Alisson",
    "Donnarumma", "De Gea", "Joe", "Samir", "Victor", "Julio", "Mark", "Carlo", "Francesco", "Massimo",
    "Jose", "Dino", "Gilmar", "Castilho", "Rogerio", "Keylor", "Jasper", "Maarten", "Stefan", "Alphonse",
    "Nick", "Aaron", "Dean", "Tomas", "Lend", "Ryan", "David", "Hugo", "Danijel", "Fernando",
    "Claudio", "Sergio", "Vito", "Jan", "Bernd", "Matt", "David", "Hugo", "Danijel", "Fernando",
    "Franz", "Sergio", "Virgil", "Bobby", "Fabio", "Paolo", "Rio", "John", "Giuseppe", "Tony",
    "Jaap", "Mats", "Gerard", "Pepe", "Nemanja", "Thiago", "Vincent", "Wes", "Gianluca", "Bacary",
    "Ashley", "Patrice", "Nery", "Ronald", "Marcel", "Claudio", "Mark", "Gaetano", "Antonio", "Giancarlo",
    "Riccardo", "Walter", "Paolo", "Alessandro", "Billy", "Roy", "Patrick", "Zinedine", "Steven", "David",
    "Paul", "Ryan", "Frank", "Andriy", "Dirk", "Didier", "Claude", "Sami", "Javi", "Bastian",
    "Juan", "Eric", "Teddy", "Ian", "Dwight", "Frederic", "Cesc", "Mesut", "Luis", "Jose",
    "Joaquin", "Andres", "Javier", "Sergio", "Xavi", "Luka", "Toni", "Casemiro", "David", "Joshua",
    "Leroy", "Kevin", "Bernardo", "Ilkay", "Fernandinho", "Juan", "Angel", "Isco", "Marco", "Pablo",
    "Christian", "Dele", "Harry", "Moussa", "Eric", "Nemanja", "Arturo", "Alexis", "Gary", "Charles",
    "Jorge", "Matias", "Fabio", "Emerson", "Philippe", "Willian", "Douglas", "Kaka", "Robinho", "Alvaro",
    "Neymar", "Vinicius", "Rodrygo", "Richarlison", "Antony", "Gabriel", "Firmino", "Carlos", "Tévez", "Javier",
    "Maradona", "Cristiano", "Lionel", "Gerd", "Ferenc", "Karim", "Robert", "Erling", "Harry", "Sergio",
    "Thierry", "Ronaldinho", "Ronaldo", "George", "Johan", "Alfredo", "Andy", "Sheringham", "Dwight", "Ole",
    "Wayne", "Michael", "Robbie", "David", "Raul", "Fernando", "Torres", "Diego", "Didier", "Samuel",
    "Kylian", "Richarlison", "Rodrygo", "Gabriel", "Neymar", "Lucas", "Paqueta", "Mohamed", "Sadio", "Roberto",
    "Leroy", "Jadon", "Marcos", "Chris", "Luke", "Aaron", "Patrice", "Nani", "Antonio", "Rafael"
]

LAST_NAMES = [
    "Buffon", "Neuer", "Casillas", "Yashin", "Shilton", "van der Sar", "Cech", "Kahn", "Ederson", "Becker",
    "Donnarumma", "De Gea", "Hart", "Handanovic", "Valdes", "Cesar", "Schwarzer", "Cudicini", "Toldo", "Taibi",
    "Chilavert", "Zoff", "Gilmar", "Castilho", "Ceni", "Navas", "Cillessen", "Stekelenburg", "Ortega", "Areola",
    "Pope", "Ramsdale", "Henderson", "Vaclík", "Leno", "Ryan", "Ospina", "Lloris", "Subasic", "Muslera",
    "Bravo", "Romero", "Mannone", "Oblak", "Mignolet", "Reina", "Sorensen", "Fährmann", "Adler", "Enke",
    "Beckenbauer", "Ramos", "van Dijk", "Moore", "Cannavaro", "Maldini", "Ferdinand", "Terry", "Bergomi", "Adams",
    "Stam", "Hummels", "Pique", "Pepe", "Vidic", "Silva", "Kompany", "Brown", "Zambrotta", "Sagna",
    "Cole", "Evra", "Pumpido", "Koeman", "Desailly", "Gentile", "Hateley", "Scirea", "Cabrini", "Antognoni",
    "Ferri", "Zenga", "Cannavaro", "Costacurta", "Bremner", "Keane", "Vieira", "Zidane", "Gerrard", "Beckham",
    "Scholes", "Giggs", "Lampard", "Shevchenko", "Kuyt", "Drogba", "Makélélé", "Khedira", "Martínez", "Schweinsteiger",
    "Valerón", "Cantona", "Sheringham", "Wright", "Yorke", "Ljungberg", "Fàbregas", "Özil", "Aragonés", "Camacho",
    "Joaquín", "Iniesta", "Mascherano", "Busquets", "Hernández", "Modrić", "Kroos", "Casemiro", "Alaba", "Kimmich",
    "Sané", "De Bruyne", "Silva", "Gündoğan", "Fernandinho", "Mata", "Di María", "Alarcón", "Asensio", "Sarabia",
    "Eriksen", "Alli", "Winks", "Sissoko", "Dier", "Matić", "Vidić", "Icardi", "Vidal", "Sánchez",
    "Medel", "Aránguiz", "Valdivia", "Fernández", "Simplício", "Aparecido", "Alcantara", "Coutinho", "Borges", "Costa",
    "Morata", "da Silva", "Junior", "Goes", "de Andrade", "Barbosa", "Firmino", "Morales", "Arriola", "Dest",
    "Loftus-Cheek", "Mount", "Saka", "Sancho", "Foden", "Bellingham", "Rice", "Ødegaard", "Rondón", "Córdoba",
    "Borré", "Luis Fernando", "Zapata", "Macías", "Martín", "Jiménez", "Alba", "Roberto", "Piqué", "Busquets",
    "Simons", "Gonzalez", "Páez", "Araujo", "Torres", "Depay", "Fati", "Puig", "González", "Torre",
    "Chair", "Suárez", "Higuaín", "Tévez", "Mascherano", "Montoya", "Ibarra", "Heinze", "Zanetti", "Cambiasso",
    "Saviola", "González", "Forlán", "De Arrascaeta", "Rodríguez", "Beltrán", "Moreno", "Romero", "Díaz", "Álvarez"
]

def generate_players(count=7500):
    """Generate 7500 unique professional football players"""
    
    players = []
    used_names = set()
    
    # Distribution targets
    targets = {"GK": 500, "CB": 2000, "CM": 3000, "ST": 2000}
    counts = {"GK": 0, "CB": 0, "CM": 0, "ST": 0}
    
    # Generate all combinations
    all_combinations = []
    for first in FIRST_NAMES:
        for last in LAST_NAMES:
            all_combinations.append(f"{first} {last}")
    
    random.shuffle(all_combinations)
    
    # Position sequence for distribution
    position_sequence = (
        ["GK"] * 500 + 
        ["CB"] * 2000 + 
        ["CM"] * 3000 + 
        ["ST"] * 2000
    )
    random.shuffle(position_sequence)
    
    # Generate players
    for i, name in enumerate(all_combinations):
        if len(players) >= count:
            break
        if name not in used_names:
            used_names.add(name)
            position = position_sequence[i] if i < len(position_sequence) else "ST"
            era = random.choice(["1950s-1970s", "1970s-1990s", "1980s-2000s", "1990s-2010s", "2000s-2020s"])
            
            # Attributes by position
            if position == "GK":
                speed = random.randint(70, 82)
                dribbling = random.randint(30, 55)
                shooting = random.randint(20, 45)
                defense = random.randint(88, 99)
            elif position == "CB":
                speed = random.randint(75, 90)
                dribbling = random.randint(60, 80)
                shooting = random.randint(45, 70)
                defense = random.randint(85, 99)
            elif position == "CM":
                speed = random.randint(78, 94)
                dribbling = random.randint(70, 92)
                shooting = random.randint(65, 88)
                defense = random.randint(60, 85)
            else:  # ST
                speed = random.randint(82, 96)
                dribbling = random.randint(75, 95)
                shooting = random.randint(82, 98)
                defense = random.randint(25, 60)
            
            players.append({
                "name": name,
                "position": position,
                "era": era,
                "speed": speed,
                "dribbling": dribbling,
                "shooting": shooting,
                "defense": defense,
                "physical": random.randint(75, 98),
                "iq": random.randint(78, 98),
                "team": random.choice(list(TEAM_COLORS.keys()))
            })
    
    return players[:count]

FORMATIONS = [
    {"name": "4-3-3", "description": "Classic balanced", "defenders": 4, "midfielders": 3, "forwards": 3},
    {"name": "4-2-4", "description": "Defensive midfield", "defenders": 4, "midfielders": 2, "forwards": 4},
    {"name": "3-5-2", "description": "Wing-heavy", "defenders": 3, "midfielders": 5, "forwards": 2},
    {"name": "5-3-2", "description": "Defensive", "defenders": 5, "midfielders": 3, "forwards": 2},
    {"name": "4-4-2", "description": "Classic", "defenders": 4, "midfielders": 4, "forwards": 2},
    {"name": "3-4-3", "description": "Attacking", "defenders": 3, "midfielders": 4, "forwards": 3},
]

if __name__ == "__main__":
    print("Generating 7500 professional players...")
    players = generate_players(7500)
    print(f"Generated {len(players)} players")
    print(f"Generated {len(COACHES)} coaches")
    print(f"Available formations: {len(FORMATIONS)}")
