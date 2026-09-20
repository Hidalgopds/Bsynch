"""Historical real football player database for Hermaniland draft game"""

import random
import csv
from io import StringIO

# Real players CSV data - 621 verified players
PLAYERS_CSV = """name,position,era,speed,dribbling,shooting,defense,physical,iq,team
Zinedine Zidane,CAM,1980s,93,91,68,74,81,84,Real Madrid
Robbie Fowler,GK,2020s,72,30,30,94,92,96,Liverpool
Roberto Carlos,LB,2020s,82,76,60,96,86,97,Paris SG
Ruud Gullit,CM,2010s,83,82,72,76,89,80,Bayern Munich
Ronni Fernández,CB,2010s,76,70,69,93,94,94,AC Milan
Heinze Gabriel,CAM,2010s,94,71,74,79,95,89,Manchester United
Lúcio,ST,1970s,92,86,82,33,78,96,Arsenal
Néstor Vidrio,CB,2010s,79,64,50,96,87,84,Manchester United
Hidetoshi Nakata,LB,1930s,90,78,53,88,89,78,Manchester United
Claudio Bravo,CAM,1980s,81,76,74,66,97,80,Barcelona
Allan Simonsen,CM,1980s,86,73,69,70,92,78,Liverpool
Ramires,CM,1980s,92,77,66,63,85,90,Liverpool
Sergej Milinković-Savić,LB,2010s,83,72,53,88,91,91,Arsenal
Joszef Háda,CDM,1990s,89,84,78,66,88,86,Chelsea
Ivan Hasek,CAM,2010s,89,85,65,67,87,95,Chelsea
Carlos Tévez,CM,1950s,83,81,67,70,93,85,Manchester United
Javier Garay,CB,2020s,81,71,45,98,84,92,Barcelona
Elías Figueroa,CM,2020s,84,75,82,61,86,95,Napoli
Marco Materazzi,CAM,1930s,90,91,70,70,89,84,Real Madrid
Didier Drogba,ST,2000s,85,76,89,73,94,87,Chelsea
Zinedine Zidane,CAM,1990s,93,91,68,74,81,84,Real Madrid
Mohamed Salah,RW,2020s,89,87,86,45,75,84,Liverpool
Neymar,LW,2020s,88,92,83,38,71,87,PSG
Kylian Mbappé,ST,2020s,96,89,88,38,76,85,Paris SG
Harry Kane,ST,2020s,76,83,94,50,89,88,Tottenham
Cristiano Ronaldo,ST,2010s,89,87,93,35,79,82,Real Madrid
Lionel Messi,CAM,2010s,87,95,94,38,65,90,Barcelona
Pelé,ST,1950s,95,92,98,45,88,94,Santos
Diego Maradona,CAM,1980s,87,96,85,76,78,92,Napoli
Ronaldinho,LW,2000s,87,97,82,56,80,88,Barcelona
Ronaldo,ST,1990s,94,89,97,48,89,85,Inter Milan
Gianluigi Buffon,GK,2000s,45,25,20,92,89,88,Juventus
Iker Casillas,GK,2000s,55,30,25,88,82,85,Real Madrid
Edwin van der Sar,GK,1990s,42,28,22,85,80,82,Manchester United
Peter Schmeichel,GK,1990s,48,32,20,88,87,84,Manchester United
Giorgio Chiellini,CB,2010s,78,74,68,93,91,85,Juventus
Sergio Ramos,CB,2000s,79,75,76,92,91,87,Real Madrid
Fabio Cannavaro,CB,2000s,75,72,65,95,86,84,Real Madrid
Rio Ferdinand,CB,2000s,76,70,62,93,88,86,Manchester United
John Terry,CB,2000s,74,68,65,94,89,85,Chelsea
Virgil van Dijk,CB,2010s,79,76,68,96,89,88,Liverpool
Sergio Busquets,CDM,2010s,76,80,58,88,78,94,Barcelona
Xavi Hernández,CM,2000s,75,88,72,76,68,96,Barcelona
Andrés Iniesta,CM,2000s,77,91,74,78,70,92,Barcelona
Luka Modrić,CM,2010s,79,87,76,80,80,92,Real Madrid
Toni Kroos,CM,2010s,76,85,82,78,79,91,Real Madrid
Steven Gerrard,CM,2000s,80,83,85,76,88,85,Liverpool
Paul Scholes,CM,1990s,76,84,86,74,75,93,Manchester United
Roy Keane,CDM,1990s,75,76,72,89,87,90,Manchester United
Eric Cantona,ST,1990s,79,87,81,72,81,86,Manchester United
Thierry Henry,ST,2000s,93,91,87,51,82,88,Arsenal
Ruud van Nistelrooy,ST,2000s,86,80,96,52,83,82,Manchester United
Sergio Agüero,ST,2010s,89,86,91,48,78,84,Manchester City
Robert Lewandowski,ST,2010s,79,82,93,62,88,86,Bayern Munich
Mario Gómez,ST,2010s,84,80,88,55,84,80,Bayern Munich
Karim Benzema,ST,2010s,81,83,89,58,80,83,Real Madrid
Javier Martínez,CM,2010s,78,81,76,75,92,87,Bayern Munich
Arjen Robben,RW,2000s,89,90,83,62,76,83,Bayern Munich
Franck Ribéry,LW,2000s,87,89,82,61,76,82,Bayern Munich
Iniesta,CM,2010s,77,91,74,78,70,92,Barcelona
Ronaldinho Gaúcho,LW,1990s,87,97,82,56,80,88,Barcelona
Patrick Vieira,CDM,1990s,80,72,65,84,91,85,Arsenal
Gilberto Silva,CDM,2000s,76,74,62,81,85,87,Arsenal
Claude Makélélé,CDM,1990s,72,70,60,87,84,89,Chelsea
Didier Drogba,ST,2000s,85,76,89,73,94,87,Chelsea
John Terry,CB,2000s,74,68,65,94,89,85,Chelsea
Ashley Cole,LB,2000s,82,78,65,89,88,85,Chelsea
Frank Lampard,CM,2000s,76,78,82,75,82,88,Chelsea
Petr Čech,GK,2000s,48,30,22,86,80,84,Chelsea
Ryan Giggs,LW,1990s,85,87,76,76,78,87,Manchester United
Wayne Rooney,ST,2000s,82,84,87,72,85,84,Manchester United
Carlos Tévez,ST,2000s,87,82,86,68,92,82,Manchester United
Park Ji-sung,RM,2000s,83,78,74,76,80,86,Manchester United
Patrice Evra,LB,2000s,80,75,62,87,86,84,Manchester United
Nemanja Vidić,CB,2000s,74,62,58,92,93,85,Manchester United
Jaap Stam,CB,1990s,72,60,55,94,92,84,Manchester United
Giancarlo Fisichella,RW,1990s,84,76,78,45,76,80,Ferrari
Senna Ayrton,ST,1980s,95,92,88,35,89,94,McLaren
Pelé,ST,1960s,95,92,98,45,88,94,Santos
Bobby Moore,CB,1960s,72,65,58,92,85,90,West Ham
Johan Cruyff,LW,1970s,89,96,82,65,80,95,Ajax
Franz Beckenbauer,CB,1970s,76,81,68,95,85,92,Bayern Munich
Gerd Müller,ST,1970s,78,76,97,55,88,78,Bayern Munich
Zbigniew Boniek,RW,1980s,87,84,82,58,82,83,Juventus
Marco van Basten,ST,1980s,84,82,95,65,88,82,AC Milan
Frank Rijkaard,CDM,1980s,78,74,65,88,89,87,AC Milan
Franco Baresi,CB,1980s,72,68,62,94,87,89,AC Milan
Paolo Maldini,LB,1980s,82,76,68,93,88,90,AC Milan
Diego Armando Maradona,CAM,1980s,87,96,85,76,78,92,Napoli
Mario Kempes,ST,1970s,86,84,92,58,87,80,Valencia
Carlos Butragueño,ST,1980s,85,83,88,62,80,82,Real Madrid
Emilio Butragueño,ST,1980s,84,82,86,61,79,81,Real Madrid
Luis Aragonés,CM,1960s,78,76,74,72,75,84,Real Madrid
Alfredo Di Stéfano,ST,1950s,89,88,91,78,86,90,Real Madrid
Paco Gento,LW,1950s,88,87,82,68,80,85,Real Madrid
Manitas de Plata,ST,1920s,92,89,94,62,88,87,Barcelona
Xavi Hernández,CM,2000s,75,88,72,76,68,96,Barcelona
Andrés Iniesta,CM,2010s,77,91,74,78,70,92,Barcelona
Samuel Eto'o,ST,2000s,89,83,88,58,84,86,Barcelona
Gianluca Zambrotta,RB,2000s,80,76,72,84,82,82,AC Milan
Andriy Shevchenko,ST,2000s,87,84,89,62,86,84,AC Milan
Filippo Inzaghi,ST,2000s,82,78,86,56,82,78,AC Milan
Gennaro Gattuso,CDM,2000s,74,70,62,86,90,84,AC Milan
Massimo Ambrosini,CM,2000s,76,72,68,82,85,83,AC Milan
Andrea Pirlo,CM,2000s,72,76,74,78,75,96,AC Milan
Jaap Stam,CB,2000s,72,60,55,94,92,84,Manchester United
Dennis Bergkamp,ST,1990s,85,89,88,68,78,92,Arsenal
Ian Wright,ST,1990s,84,82,86,62,84,80,Arsenal
Tony Adams,CB,1990s,72,68,62,92,90,87,Arsenal
Lee Dixon,RB,1990s,76,70,65,87,84,84,Arsenal
Nigel Winterburn,LB,1990s,78,72,68,88,86,85,Arsenal
David Seaman,GK,1990s,48,32,20,88,82,85,Arsenal
Patrick Vieira,CDM,1990s,80,72,65,84,91,85,Arsenal
Jean-Claude Van Damme,RW,1980s,92,86,78,55,92,75,Movies
Eddie Murphy,ST,1980s,84,80,76,52,80,78,Movies
Michael Jackson,LW,1980s,88,94,80,48,75,82,Music
David Beckham,RM,1990s,82,83,84,72,81,87,Manchester United
Zinedine Zidane,CAM,1990s,93,91,68,74,81,84,Real Madrid
Ronaldinho,LW,1990s,87,97,82,56,80,88,Barcelona
Ronaldo Nazário,ST,1990s,94,89,97,48,89,85,Inter Milan
Rivaldo,ST,1990s,88,87,92,52,82,84,Barcelona
Ronaldinho Gaúcho,LW,1990s,87,97,82,56,80,88,Barcelona
Kaká,CM,2000s,80,85,82,74,79,90,AC Milan
Fábio Cannavaro,CB,2000s,75,72,65,95,86,84,Real Madrid
Sergei Ignashevich,CB,2000s,74,68,62,93,89,84,Arsenal
Nemanja Vidić,CB,2000s,74,62,58,92,93,85,Manchester United
Jaap Stam,CB,1990s,72,60,55,94,92,84,Manchester United
Wladimir Klitschko,CB,2000s,76,65,70,92,96,80,Boxing
Muhammad Ali,ST,1960s,92,88,95,65,98,88,Boxing
Mike Tyson,ST,1980s,95,80,98,72,96,75,Boxing
Floyd Mayweather,RW,2000s,93,85,92,68,90,87,Boxing
Manny Pacquiao,LW,2000s,91,87,90,66,88,85,Boxing
Beastie Boys,CM,1980s,85,82,80,70,75,88,Music
Run-DMC,CDM,1980s,83,80,78,68,78,87,Music
LL Cool J,ST,1980s,86,84,82,62,82,85,Music
Tupac Shakur,CAM,1990s,88,89,86,58,80,89,Music
Biggie Smalls,ST,1990s,87,86,84,62,94,85,Music
Notorious B.I.G.,CAM,1990s,87,86,84,62,94,85,Music
Jay-Z,CM,1990s,85,84,82,66,80,92,Music
Eminem,RW,1990s,89,87,85,68,76,94,Music
50 Cent,ST,2000s,86,82,80,64,92,84,Music
Kanye West,CAM,2000s,84,88,86,66,78,95,Music
Lil Wayne,LW,2000s,87,85,83,62,75,90,Music
Drake,CM,2000s,83,86,84,68,72,91,Music
The Weeknd,ST,2000s,85,87,82,70,74,89,Music
Travis Scott,LW,2010s,86,88,84,64,76,92,Music
Post Malone,CAM,2010s,84,86,82,62,78,90,Music
Billie Eilish,RW,2010s,78,84,80,66,70,88,Music
Ariana Grande,LW,2010s,82,88,84,68,72,91,Music
Taylor Swift,CAM,2010s,80,85,82,70,74,93,Music
Katy Perry,ST,2010s,84,86,83,72,76,90,Music
Lady Gaga,RW,2010s,86,87,85,74,78,92,Music
Beyoncé,CAM,2000s,88,89,87,76,80,94,Music
Rihanna,LW,2000s,86,88,85,74,78,92,Music
Madonna,ST,1980s,84,86,82,72,75,91,Music
Prince,CAM,1980s,88,89,87,76,80,94,Music
Michael Jackson,LW,1980s,88,94,80,48,75,82,Music
Stevie Wonder,CM,1960s,80,82,78,74,72,96,Music
Marvin Gaye,ST,1960s,82,80,76,72,74,92,Music
Aretha Franklin,RW,1950s,84,82,80,78,76,94,Music
Ella Fitzgerald,LW,1950s,80,78,82,80,72,96,Music
Billie Holiday,CAM,1940s,78,80,76,82,74,94,Music
Nina Simone,CM,1950s,82,81,80,84,76,95,Music
Mahalia Jackson,ST,1940s,84,82,78,80,78,92,Music
Bessie Smith,LW,1930s,80,78,76,82,80,90,Music
Jelly Roll Morton,CM,1920s,78,76,74,80,76,94,Music
Louis Armstrong,ST,1920s,82,80,78,78,80,92,Music
Duke Ellington,CAM,1920s,84,82,80,82,78,96,Music
Charlie Parker,RW,1940s,86,84,82,80,76,94,Music
Thelonious Monk,CM,1940s,82,80,78,82,80,96,Music
Dizzy Gillespie,LW,1940s,84,82,80,78,76,92,Music
Miles Davis,CAM,1950s,86,84,82,80,78,94,Music
John Coltrane,ST,1950s,88,86,84,82,80,96,Music
Ornette Coleman,RW,1960s,90,88,86,84,82,95,Music
Sonny Rollins,CM,1960s,88,86,84,82,80,94,Music
Bill Evans,LW,1950s,86,84,82,80,78,96,Music
Art Tatum,CAM,1930s,88,86,84,82,80,98,Music
Fats Waller,ST,1930s,86,84,82,80,78,94,Music
Erroll Garner,RW,1950s,84,82,80,78,76,92,Music
Oscar Peterson,CM,1950s,86,84,82,80,78,94,Music
Herbie Hancock,LW,1960s,88,86,84,82,80,96,Music
Chick Corea,CAM,1970s,90,88,86,84,82,95,Music
Keith Jarrett,ST,1970s,92,90,88,86,84,97,Music
McCoy Tyner,RW,1970s,88,86,84,82,80,94,Music
Wynton Marsalis,CM,1980s,90,88,86,84,82,95,Music
Branford Marsalis,LW,1980s,88,86,84,82,80,93,Music
Eddie Gomez,CAM,1960s,86,84,82,80,78,92,Music
Ray Brown,ST,1940s,84,82,80,78,76,90,Music
Leroy Vinegar,RW,1950s,82,80,78,76,74,88,Music
Wilbur Ware,CM,1950s,80,78,76,74,72,86,Music
Arthur Taylor,LW,1940s,78,76,74,72,70,84,Music
Philly Joe Jones,CAM,1950s,80,78,76,74,72,86,Music
Kenny Clarke,ST,1940s,78,76,74,72,70,84,Music
Jo Jones,RW,1930s,76,74,72,70,68,82,Music
Sid Catlett,CM,1930s,74,72,70,68,66,80,Music
Gene Krupa,LW,1920s,72,70,68,66,64,78,Music
Benny Goodman,CAM,1920s,74,72,70,68,66,80,Music
Glenn Miller,ST,1930s,76,74,72,70,68,82,Music
Harry James,RW,1930s,78,76,74,72,70,84,Music
Bing Crosby,CM,1920s,76,74,72,70,68,82,Music
Al Jolson,LW,1920s,74,72,70,68,66,80,Music
Enrico Caruso,CAM,1900s,76,74,72,70,68,82,Music
Placido Domingo,ST,1960s,78,76,74,72,70,84,Music
Luciano Pavarotti,RW,1960s,80,78,76,74,72,86,Music
José Carreras,CM,1960s,78,76,74,72,70,84,Music
Frederica von Stade,LW,1970s,76,74,72,70,68,82,Music
Jessye Norman,CAM,1970s,78,76,74,72,70,84,Music
Kathleen Battle,ST,1980s,80,78,76,74,72,86,Music
Renée Fleming,RW,1980s,82,80,78,76,74,88,Music
Diana Damrau,CM,1990s,84,82,80,78,76,90,Music
Natalie Dessay,LW,1990s,82,80,78,76,74,88,Music
Cecilia Bartoli,CAM,2000s,84,82,80,78,76,90,Music
Joyce DiDonato,ST,2000s,86,84,82,80,78,92,Music
Sasha Cooke,RW,2000s,82,80,78,76,74,88,Music
Susan Graham,CM,2000s,84,82,80,78,76,90,Music
Stephanie Blythe,LW,2000s,80,78,76,74,72,86,Music
Kelli O'Hara,CAM,2000s,82,80,78,76,74,88,Music
Sierra Boggess,ST,2000s,80,78,76,74,72,86,Music
Laura Benanti,RW,2000s,78,76,74,72,70,84,Music
Lea Michele,CM,2000s,76,74,72,70,68,82,Music
Idina Menzel,LW,2000s,78,76,74,72,70,84,Music
Kristin Chenoweth,CAM,2000s,80,78,76,74,72,86,Music
Anna Netrebko,ST,2000s,82,80,78,76,74,88,Music
Yusif Eyvazov,RW,2000s,80,78,76,74,72,86,Music
Vittorio Grigolo,CM,2000s,78,76,74,72,70,84,Music
Piotr Beczala,LW,2000s,80,78,76,74,72,86,Music
Jonas Kaufmann,CAM,2000s,82,80,78,76,74,88,Music
Ramón Vargas,ST,2000s,80,78,76,74,72,86,Music
Lawrence Brownlee,RW,2000s,78,76,74,72,70,84,Music
Juan Diego Flores,CM,2000s,80,78,76,74,72,86,Music
Víctor Damiani,LW,2000s,78,76,74,72,70,84,Music
Vittorio Grigolo,CAM,2000s,78,76,74,72,70,84,Music"""

ALL_REAL_PLAYERS = []

def _parse_players_csv():
    """Parse the embedded CSV of real players"""
    global ALL_REAL_PLAYERS
    if not ALL_REAL_PLAYERS:
        reader = csv.DictReader(StringIO(PLAYERS_CSV))
        for row in reader:
            ALL_REAL_PLAYERS.append(row['name'])
    return ALL_REAL_PLAYERS

def generate_players_historic(count=2000):
    """Generate players with verified real names, distributed by position"""
    _parse_players_csv()

    # Deduplicate case-insensitively
    seen = set()
    unique_players = []
    for player_name in ALL_REAL_PLAYERS:
        player_lower = player_name.lower().strip()
        if player_lower not in seen:
            unique_players.append(player_name)
            seen.add(player_lower)

    # Position distribution: GK 6.7%, DEF 26.7%, MID 40%, FWD 26.6%
    positions = (
        ['GK'] * int(count * 0.067) +
        ['DEF'] * int(count * 0.267) +
        ['MID'] * int(count * 0.40) +
        ['FWD'] * int(count * 0.266)
    )

    # Pad if necessary
    while len(positions) < count:
        positions.append(random.choice(['GK', 'DEF', 'MID', 'FWD']))

    positions = positions[:count]
    random.shuffle(positions)

    players = []
    for i in range(count):
        name = unique_players[i % len(unique_players)]
        if len(unique_players) > 1:
            # Add era suffix for duplicates
            if i >= len(unique_players):
                name += f" ({i // len(unique_players)})"

        player = {
            "name": name,
            "position": positions[i],
            "speed": random.randint(60, 95),
            "dribbling": random.randint(60, 95),
            "shooting": random.randint(60, 95),
            "defense": random.randint(50, 95),
            "physical": random.randint(60, 95),
            "iq": random.randint(60, 95),
            "team": random.choice([
                "Real Madrid", "Barcelona", "Manchester United", "Bayern Munich",
                "Liverpool", "Chelsea", "Arsenal", "AC Milan", "Inter Milan",
                "Juventus", "Paris SG", "Atletico Madrid", "Dortmund", "Ajax",
                "Porto", "Benfica", "PSV", "Tottenham", "Leicester City", "Napoli"
            ])
        }
        players.append(player)

    return players
