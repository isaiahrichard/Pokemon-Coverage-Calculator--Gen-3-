import pypokedex
import os
import sys
from info import leader_pokemon, leaders, type_effectiveness


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def reset_terminal():
    os.system("cls" if os.name == "nt" else "clear")
    print(
        f""" {bcolors.OKCYAN}
  _____      _                                _______                     ____        _ _     _           
 |  __ \    | |                              |__   __|                   |  _ \      (_) |   | |          
 | |__) |__ | | _____ _ __ ___   ___  _ __      | | ___  __ _ _ __ ___   | |_) |_   _ _| | __| | ___ _ __ 
 |  ___/ _ \| |/ / _ \ '_ ` _ \ / _ \| '_ \     | |/ _ \/ _` | '_ ` _ \  |  _ <| | | | | |/ _` |/ _ \ '__|
 | |  | (_) |   <  __/ | | | | | (_) | | | |    | |  __/ (_| | | | | | | | |_) | |_| | | | (_| |  __/ |   
 |_|   \___/|_|\_\___|_| |_| |_|\___/|_| |_|    |_|\___|\__,_|_| |_| |_| |____/ \__,_|_|_|\__,_|\___|_|  
 {bcolors.ENDC}
"""
    )


def split_dict(input_dict):
    dictA = {}
    dictB = {}

    for key, value in input_dict.items():
        if value > 0:
            dictA[key] = value
        if value < 0:
            dictB[key] = value

    return dictA, dictB


def get_pokemon_team(pokemon_names):
    poke_list = []

    for pokemon_name in pokemon_names:
        pokemon = pypokedex.get(name=pokemon_name)
        poke_list.append(pokemon)

    return poke_list


def reset_leader_stats():
    for leader, pokemon_list in leaders.items():
        pokemon_list["defense_score"] = 0
        pokemon_list["attack_score"] = 0
        for pokemon, type_values in pokemon_list["pokemon"].items():
            type_values.clear()


def analyze_team_resistance(pokemon_team):
    type_effectiveness_dict = {
        "normal": 0,
        "fire": 0,
        "water": 0,
        "electric": 0,
        "grass": 0,
        "ice": 0,
        "fighting": 0,
        "poison": 0,
        "ground": 0,
        "flying": 0,
        "psychic": 0,
        "bug": 0,
        "rock": 0,
        "ghost": 0,
        "dragon": 0,
        "dark": 0,
        "steel": 0,
        "fairy": 0,
    }

    for pokemon in pokemon_team:
        for type in pokemon.types:
            weaknesses = type_effectiveness[type]["weak_incoming"]
            for weakness in weaknesses:
                type_effectiveness_dict[weakness] += 1

            strenghts = type_effectiveness[type]["strong_incoming"]
            for strenght in strenghts:
                type_effectiveness_dict[strenght] -= 1

    return split_dict(type_effectiveness_dict)


def analyze_type_interaction(pokemon_types, attacking_types):
    weak_to = []
    resists = []

    for type in pokemon_types:
        weak_to += type_effectiveness[type]["weak_incoming"]
        resists += type_effectiveness[type]["strong_incoming"]

    weak_to_set = set(weak_to)
    resists_set = set(resists)

    intersection = weak_to_set & resists_set

    weak_to = set([type for type in weak_to if type not in intersection])
    resists = set([type for type in resists if type not in intersection])

    interaction_index = 0

    if set(attacking_types) & weak_to:
        interaction_index = -1
    elif set(attacking_types) & resists:
        interaction_index = 1

    return interaction_index


def analyze_team_coverage(pokemon_team):
    for leader, pokemon_list in leaders.items():
        for curr_leader_pokemon in pokemon_list["pokemon"]:
            pokemon_types = leader_pokemon[curr_leader_pokemon]["types"]
            for pokemon in pokemon_team:
                interaction_index_outgoing = analyze_type_interaction(
                    pokemon_types, pokemon.types
                )
                interaction_index_incoming = analyze_type_interaction(
                    pokemon.types, pokemon_types
                )
                leaders[leader]["pokemon"][curr_leader_pokemon].append(
                    interaction_index_outgoing
                )
                leaders[leader]["defense_score"] += interaction_index_outgoing
                leaders[leader]["attack_score"] += interaction_index_incoming
                leaders[leader]["pokemon"][curr_leader_pokemon].append(
                    interaction_index_incoming
                )


def main():
    while True:
        reset_terminal()

        selection = 0
        pokemon_team_input = ""

        with open("previous_teams.txt", "r") as f:
            prev_pokemon_team = f.read()
            pokemon_list = prev_pokemon_team.split(",")
            print(
                f"1. Load previous team: {' | '.join([pokemon.capitalize() for pokemon in pokemon_list])}"
            )
            print(f"2. Enter new team")
            print(f"3. Exit")
            selection = int(input(""))
            if selection == 1:
                pokemon_team_input = prev_pokemon_team.split(",")

        reset_terminal()

        if selection == 2:
            print(
                "Input pokemon name(s) to see its effectiveness against pokemon fire red and leaf green"
            )
            pokemon_team_input = input("").replace(" ", "").split(",")
        elif selection == 3:
            sys.exit()

        with open("previous_teams.txt", "w") as f:
            f.write(",".join(pokemon_team_input))

        while True:
            reset_terminal()

            print("1. Sort leaders by damage effectiveness of your team")
            print("2. Sort leaders by damage effectiveness against your team")
            print("3. Enter new team")
            print("4. Exit")
            sort_selection = int(input(""))

            pokemon_team = get_pokemon_team(pokemon_team_input)
            reset_leader_stats()
            analyze_team_coverage(pokemon_team)

            sorted_leaders = []

            if sort_selection == 1:
                sorted_leaders = dict(
                    sorted(
                        leaders.items(),
                        key=lambda item: item[1]["defense_score"],
                        reverse=True,
                    )
                )
            elif sort_selection == 2:
                sorted_leaders = dict(
                    sorted(leaders.items(), key=lambda item: item[1]["attack_score"])
                )
            elif sort_selection == 3:
                break
            else:
                sys.exit()

            reset_terminal()
            print(
                f"{bcolors.OKGREEN}----------------------------------------------------------"
            )
            print("         Your Effectiveness / Their Effectiveness")
            print(
                f"----------------------------------------------------------{bcolors.ENDC}\n"
            )

            for leader, pokemon_list in sorted_leaders.items():
                print(f"Leader: {leader.capitalize()}")
                print(f"-----------------------------")
                header = ["Pokémon"] + [
                    pokemon.name.capitalize() for pokemon in pokemon_team
                ]
                print(" ".join([f"{col:<10}" for col in header]))
                trouble_pokemon = []
                for pokemon, type_values in pokemon_list["pokemon"].items():
                    type_interaction_values = [
                        "2x" if value < 0 else ".5x" if value > 0 else "1x"
                        for value in type_values
                    ]
                    double_type_values = [
                        f"{type_interaction_values[i]}/{type_interaction_values[i+1]}"
                        for i in range(0, len(type_interaction_values), 2)
                    ]
                    row = [pokemon.capitalize()] + double_type_values
                    print(" ".join([f"{item:<10}" for item in row]))
                    if all(
                        value > 0
                        for index, value in enumerate(type_values)
                        if index % 2 == 0
                    ):
                        enemy_pokemon = pypokedex.get(name=pokemon)
                        trouble_pokemon.append(enemy_pokemon)
                if len(trouble_pokemon):
                    team_weaknesses, _ = analyze_team_resistance(trouble_pokemon)
                    print(
                        f"{bcolors.FAIL}No pokemon in your team is strong against {', '.join([pokemon.name.capitalize() for pokemon in trouble_pokemon])}"
                    )
                    print(
                        f"Consider adding a pokemon with a {', '.join(team_weaknesses.keys())} move{bcolors.ENDC}"
                    )
                print("\n")

            resort_selection = 0
            print("1. Re-sort leaders")
            print("2. Exit")
            resort_selection = int(input(""))
            if resort_selection == 1:
                continue
            if resort_selection == 2:
                sys.exit()


if __name__ == "__main__":
    os.system("color")
    main()
