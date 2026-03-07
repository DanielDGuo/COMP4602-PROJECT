import requests as re
import json, os
import math

base_url = "https://pokeapi.co/api/v2"
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")

type_effectiveness = {
    "normal":{
        "rock": 0.5,
        "ghost": 0,
        "steel": 0.5,
    },
    "fire":{
        "fire": 0.5,
        "water": 0.5,
        "grass": 2,
        "ice": 2,
        "bug": 2,
        "rock": 0.5,
        "dragon": 0.5,
        "steel": 2,
    },
    "water":{
        "fire": 2,
        "water": 0.5,
        "grass": 0.5,
        "ground": 2,
        "rock": 2,
        "dragon": 0.5,
    },
    "grass":{
        "fire": 0.5,
        "water": 2,
        "grass": 0.5,
        "poison": 0.5,
        "ground": 2,
        "flying": 0.5,
        "bug": 0.5,
        "rock": 2,
        "dragon": 0.5,
        "steel": 0.5,
    },
    "electric":{
        "water": 2,
        "grass": 0.5,
        "electric": 0.5,
        "ground": 0,
        "flying": 2,
        "dragon": 0.5,
    },
    "ice":{
        "fire": 0.5,
        "water": 0.5,
        "grass": 2,
        "ice": 0.5,
        "ground": 2,
        "flying": 2,
        "dragon": 2,
        "steel": 0.5,
    },
    "fighting":{
        "normal": 2,
        "ice": 2,
        "poison": 0.5,
        "flying": 0.5,
        "psychic": 0.5,
        "bug": 0.5,
        "rock": 2,
        "ghost": 0,
        "dark": 2,
        "steel": 2,
        "fairy": 0.5,
    },
    "poison":{
        "grass": 2,
        "poison": 0.5,
        "ground": 0.5,
        "rock": 0.5,
        "ghost": 0.5,
        "steel": 0,
        "fairy": 2,
    },
    "ground":{
        "fire": 2,
        "grass": 0.5,
        "electric": 2,
        "poison": 2,
        "flying": 0,
        "bug": 0.5,
        "rock": 2,
        "steel": 2,
    },
    "flying":{
        "grass": 2,
        "electric": 0.5,
        "fighting": 2,
        "bug": 2,
        "rock": 0.5,
        "steel": 0.5,
    },
    "psychic":{
        "fighting": 2,
        "poison": 2,
        "psychic": 0.5,
        "dark": 0,
        "steel": 0.5,
    },
    "bug":{
        "fire": 0.5,
        "grass": 2,
        "fighting": 0.5,
        "poison": 0.5,
        "flying": 0.5,
        "psychic": 2,
        "ghost": 0.5,
        "dark": 2,
        "steel": 0.5,
        "fairy": 0.5,
    },
    "rock":{
        "fire": 2,
        "ice": 2,
        "fighting": 0.5,
        "ground": 0.5,
        "flying": 2,
        "bug": 2,
        "steel": 0.5,
    },
    "ghost":{
        "normal": 0,
        "psychic": 2,
        "ghost": 2,
        "dark": 0.5,
    },
    "dragon":{
        "dragon": 2,
        "steel": 0.5,
        "fairy": 0,
    },
    "dark":{
        "fighting": 0.5,
        "psychic": 2,
        "ghost": 2,
        "dark": 0.5,
        "fairy": 0.5,
    },
    "steel":{
        "fire": 0.5,
        "water": 0.5,
        "electric": 0.5,
        "ice": 2,
        "rock": 2,
        "steel": 0.5,
        "fairy": 2,
    },
    "fairy":{
        "fire": 0.5,
        "fighting": 2,
        "poison": 0.5,
        "dragon": 2,
        "dark": 2,
        "steel": 0.5,
    }
}


#taken from the damage_calculator github. Function not exposed in libary
#uses int division like in the game.
def calculate_move_damage(level, attack, defense, power, type_effectiveness, stab):
    level_factor = (2 * level) // 5 + 2
    damage = int((((level_factor * attack * power // defense) // 50) + 2) * stab * type_effectiveness)
    return damage

#fetches pokemon by id
def fetch_pokemon(pokemon_id):
    if int(pokemon_id) < 1 or int(pokemon_id) > 1025:
        raise ValueError("Pokemon ID must be between 1 and 1025.")
    #fetch URL
    url = f"{base_url}/pokemon/{pokemon_id}"
    #create the cache directory for pokemon
    os.makedirs(os.path.join(CACHE_DIR, "pokemon_by_id"), exist_ok=True)

    #set the path for the json file
    path = os.path.join(CACHE_DIR, "pokemon_by_id", "pokemon_" + pokemon_id + ".json")

    #if it exists, it's been fetched before. Get the file from the cache instead of making an API request
    if os.path.exists(path):
        with open(path) as f:
            print("file for pokemon " + str(pokemon_id) + " found in cache")
            return json.load(f)

    #make an API request for the pokemon
    print("file fetched")
    response = re.get(url)

    if response.status_code == 200:
        #format the data before dumping it into the file
        data = response.json()
        remove_keys = ["base_experience", "cries", "forms", "game_indices", "height", "held_items", "is_default", "location_area_encounters", "order", "past_abilities", "past_stats", "past_types", "sprites"]
        for key in remove_keys:
            data.pop(key, None)

        for move in data["moves"]:
            move.pop("version_group_details")


        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        return data
    else:
        #pokemon doesn't exist, return an error message
        raise re.exceptions.HTTPError("PokemonAPI endpoint not found. Name error. Error " + str(response.status_code))

#completely overwrites existing json data.
def replace_data(path, json_data):
    if os.path.exists(path):
        with open(path, "w") as f:
            json.dump(json_data, f, indent=4)

#fetches pokemon by id. Alt forms need to inherit some values from their base form.
#need to be inherited: moves, abilities, 
def fetch_alt_form_pokemon(pokemon_id):
    if int(pokemon_id) < 10001 or int(pokemon_id) > 10325:
        raise ValueError("Pokemon alternate form ID must be between 10001 and 10325.")
    #fetch URL
    url = f"{base_url}/pokemon/{pokemon_id}"
    #create the cache directory for pokemon
    os.makedirs(os.path.join(CACHE_DIR, "pokemon_by_id"), exist_ok=True)

    #set the path for the json file
    path = os.path.join(CACHE_DIR, "pokemon_by_id", "pokemon_" + pokemon_id + ".json")

    #if it exists, it's been fetched before. Get the file from the cache instead of making an API request
    if os.path.exists(path):
        with open(path) as f:
            print("file found in cache")
            return json.load(f)

    #make an API request for the pokemon
    print("file fetched")
    response = re.get(url)

    if response.status_code == 200:
        #format the data before dumping it into the file
        data = response.json()
        remove_keys = ["base_experience", "cries", "forms", "game_indices", "height", "held_items", "is_default", "location_area_encounters", "order", "past_abilities", "past_stats", "past_types", "sprites"]
        for key in remove_keys:
            data.pop(key, None)

        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        return data
    else:
        #pokemon doesn't exist, return an error message
        raise re.exceptions.HTTPError("PokemonAPI endpoint not found. Name error. Error " + str(response.status_code))

#fetches moves by ID. Ignores moves with no power
#fetch all valid moves first -> if a pokemon uses a move not in the list of fetched moves, the move must be invalid.
#ignore healing effects
#list of moves that should exist are here: https://bulbapedia.bulbagarden.net/wiki/List_of_moves_that_do_damage
def fetch_move(move_id):
    if int(move_id) < 1 or int(move_id) > 919:
        raise ValueError("Move ID must be between 1 and 919(Move 920 - 'Nihil Light' is not in PokeAPI.).")
    #fetch URL
    url = f"{base_url}/move/{move_id}"
    #create the cache directory for pokemon
    os.makedirs(os.path.join(CACHE_DIR, "move_by_id"), exist_ok=True)

    #set the path for the json file
    path = os.path.join(CACHE_DIR, "move_by_id", "move_" + move_id + ".json")

    #if it exists, it's been fetched before. Get the file from the cache instead of making an API request
    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
            print("file for move " + str(move_id) + " found in cache")
            if "is_status" in data.keys():
                print("move " + str(move_id) + " is a status move. Ignored.")
                return -1
            if "is_weird_move" in data.keys():
                print("move " + str(move_id) + " has None power and has a move that scales weirdly. Ignored.")
                return -1
            return data

    #make an API request for the pokemon
    print("file fetched")
    response = re.get(url)

    if response.status_code == 200:
        #format the data before dumping it into the file
        data = response.json()
        if data["power"] == None:
            #ignore status moves
            if data["damage_class"]["name"] == "status":
                print("Move " + move_id + " is a status move.")
                data = {}
                data["is_status"] = True        
                with open(path, "w") as f:
                    json.dump(data, f, indent=4)
                return -1
            # some moves that do deal damage have weird damage calculations. They do NOT appear in the list.
            valid_null_power_moves = ["electro-ball", "frustration", "grass-knot", "gyro-ball", "heat-crash", "heavy-slam", "low-kick", "return"]
            if data["name"] not in valid_null_power_moves:
                print("Move " + move_id + " has no power and does not have a scaling power.")
                data = {}
                data["is_weird_move"] = True        
                with open(path, "w") as f:
                    json.dump(data, f, indent=4)
                return -1
            else:
                if data["name"] == "frustration" or data["name"] == "return":
                    data["power"] = 102

        if data["accuracy"] == None:
            data["accuracy"] = 100
        
        #multihit move modifiers
        multihit_bonus = 1
        #moves that always hit twice
        if data["name"] in ["bonemerang", "double-hit", "double-iron-bash", "double-kick", "dragon-darts", "dual-chop", "dual-wingbeat", "gear-grind", "tachyon-cutter", "twin-beam", "twineedle"]:
            multihit_bonus = 2
        #moves that always hit thrice
        if data["name"] in ["surging-strikes", "triple-dive"]:
            multihit_bonus = 3
        #moves that on average hit 3.1 times
        if data["name"] in ["arm-thrust", "barrage", "bone-rush", "bullet-seed", "comet-punch", "double-slap", "fury-attack", "fury-swipes", "icicle-spear", "pin-missile", "rock-blast", "scale-shot", "spike-cannon", "tail-slap", "water-shuriken"]:
            multihit_bonus = 3.1
        #population bomb
        if data["name"] in ["population-bomb"]:
            multihit_bonus = 5.8618940391
        data["multihit_modifier"] = multihit_bonus

        #penalize the accuracy 2x
        accuracy_modifier = 100 - 2*(100 - data["accuracy"])
        data["accuracy_modifier"] = accuracy_modifier / 100.0

        remove_keys = ["contest_combos", "contest_type", "contest_effect", "effect_changes", "generation", "learned_by_pokemon", "flavor_text_entries", "machines", "names", "past_values", "super_contest_effect"]
        for key in remove_keys:
            data.pop(key, None)

        for entry in data["effect_entries"]:
            if entry["language"]["name"] != "en":
                data["effect_entries"].remove(entry)

        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        return data
    else:
        #move id doesn't exist, return an error message
        raise re.exceptions.HTTPError("PokemonAPI endpoint not found. Name error. Error " + str(response.status_code))


#get stats at lv100
#returns a dict
def calculate_stats(pokemon_id):
    max_stats = {}
    pokemon_data = fetch_pokemon(pokemon_id)
    if "max_stats" in pokemon_data.keys():
        return pokemon_data["max_stats"]
    base_stats = pokemon_data["stats"]

    for stat in base_stats:
        match stat["stat"]["name"]:
            case "hp":
                max_stats["hp"] = 110 + (2*stat["base_stat"] + 31)
            case "attack":
                max_stats["atk"] = 5 + (2*stat["base_stat"] + 31)
            case "defense":
                max_stats["def"] = 5 + (2*stat["base_stat"] + 31)
            case "special-attack":
                max_stats["spa"] = 5 + (2*stat["base_stat"] + 31)
            case "special-defense":
                max_stats["spd"] = 5 + (2*stat["base_stat"] + 31)
            case "speed":
                max_stats["spe"] = 5 + (2*stat["base_stat"] + 31)
    if len(max_stats) < 6:
        raise ValueError("Some stats not found for pokemon with id " + str(pokemon_id) + ". Stats received: " + str(max_stats.keys()))
    pokemon_data["max_stats"] = max_stats
    path = os.path.join(CACHE_DIR, "pokemon_by_id", "pokemon_" + pokemon_id + ".json")
    replace_data(path, pokemon_data)
    return max_stats

def calculate_type_effectiveness(atk_type, def_type1, def_type2):
    type1_effectiveness = 1
    type2_effectiveness = 1
    if def_type1 in type_effectiveness[atk_type]:
        type1_effectiveness = type_effectiveness[atk_type][def_type1]
    if def_type2 in type_effectiveness[atk_type] and def_type2 != None:
        type2_effectiveness = type_effectiveness[atk_type][def_type2]

    return 1 * type1_effectiveness * type2_effectiveness

def calculate_damage(pokemon1_id, pokemon2_id):
    #general data
    pokemon1_data = fetch_pokemon(pokemon1_id)
    pokemon2_data = fetch_pokemon(pokemon2_id)

    #stats
    pokemon1_stats = calculate_stats(pokemon1_id)
    pokemon2_stats = calculate_stats(pokemon2_id)
    #calculate the best move for pokemon 1 to use
    #damage calculator needs power
    max_damage = 0
    actual_max_damage = 0
    max_move = ""
    max_move_accuracy = 0
    for move in pokemon1_data["moves"]:
        move_id = move["move"]["url"].rstrip("/").split("/")[-1]
        move_data = fetch_move(move_id)
        #status move or move that doesnt do damage
        if move_data == -1:
            continue

        damage_class = move_data["damage_class"]["name"]
        attacker_stat = 0
        defender_stat = 0
        if damage_class == "physical":
            attacker_stat = pokemon1_stats["atk"]
            defender_stat = pokemon2_stats["def"]
        elif damage_class == "special":
            attacker_stat = pokemon1_stats["spa"]
            defender_stat = pokemon2_stats["spd"]
        else:
            raise ValueError("Expected physical or special move. Recieved " + damage_class)
    
        is_triple_axel = False
        is_triple_kick = False
        
        #two moves that ramp up in power with each subsequent hit
        if move["move"]["name"] == "triple-axel":
            is_triple_axel = True
        if move["move"]["name"] == "triple-kick":
            is_triple_kick = True

        type_effectiveness = 1
        if len(pokemon2_data["types"]) == 2:
            type_effectiveness = calculate_type_effectiveness(move_data["type"]["name"], pokemon2_data["types"][0]["type"]["name"], pokemon2_data["types"][1]["type"]["name"])
        else:
            type_effectiveness = calculate_type_effectiveness(move_data["type"]["name"], pokemon2_data["types"][0]["type"]["name"], None)

        stab = 1
        for type in pokemon1_data["types"]:
            if type["type"]["name"] == move_data["type"]["name"]:
                stab = 1.5
                break

        power = move_data["power"]
        if power == None:
            match move["move"]["name"]:
                case "grass-knot":
                    if pokemon2_data["weight"] < 100:
                        power = 20
                    elif pokemon2_data["weight"] < 250:
                        power = 40
                    elif pokemon2_data["weight"] < 500:
                        power = 60
                    elif pokemon2_data["weight"] < 1000:
                        power = 80
                    elif pokemon2_data["weight"] < 2000:
                        power = 100
                    else:
                        power = 120

                    damage = (move_data["multihit_modifier"] * move_data["accuracy_modifier"] * calculate_move_damage(100, attacker_stat, defender_stat, power, type_effectiveness, stab)) / pokemon2_stats["hp"]
                    if max_damage < damage:
                        max_damage = damage
                        move = move["move"]["name"]
                case "heavy-slam":
                    weight_ratio = pokemon2_data["weight"] / pokemon1_data["weight"]
                    if weight_ratio > 0.5:
                        power = 40
                    elif weight_ratio > 0.3334:
                        power = 60
                    elif weight_ratio > 0.25:
                        power = 80
                    elif weight_ratio > 20:
                        power = 100
                    else:
                        power = 120

                    damage = (move_data["multihit_modifier"] * move_data["accuracy_modifier"] * calculate_move_damage(100, attacker_stat, defender_stat, power, type_effectiveness, stab)) / pokemon2_stats["hp"]
                    if max_damage < damage:
                        max_damage = damage
                        move = move["move"]["name"]
                case "gyro-ball":
                    power = min(150, (25*(pokemon2_stats["spd"])/(pokemon1_stats["spe"])) + 1)

                    damage = (move_data["multihit_modifier"] * move_data["accuracy_modifier"] * calculate_move_damage(100, attacker_stat, defender_stat, power, type_effectiveness, stab)) / pokemon2_stats["hp"]
                    if max_damage < damage:
                        max_damage = damage
                        move = move["move"]["name"]
                case _:
                    print(move["move"]["name"] + " has None power. Create an edge case to manually set.")
        #WIP - ignored for now
        elif is_triple_axel:
            print("Triple Axel")
        elif is_triple_kick:
            print("Triple Kick")
        else:
            damage = (move_data["multihit_modifier"] * move_data["accuracy_modifier"] * calculate_move_damage(100, attacker_stat, defender_stat, power, type_effectiveness, stab)) / pokemon2_stats["hp"]
            if max_damage < damage:
                max_damage = damage
                actual_max_damage = (move_data["multihit_modifier"] * calculate_move_damage(100, attacker_stat, defender_stat, power, type_effectiveness, stab)) / pokemon2_stats["hp"]
                max_move = move["move"]["name"]
                max_move_accuracy = move_data["accuracy"]
                
    path = os.path.join(CACHE_DIR, "matchups.json")
    #create a base json file if needed
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({}, f)  
    with open(path, "r") as f:
        data = json.load(f)
        matchup_index = ""
        ordered_pokeid1 = "-1"
        ordered_pokeid2 = "-1"

        if int(pokemon1_id) < int(pokemon2_id):
            ordered_pokeid1 = pokemon1_id
            ordered_pokeid2 = pokemon2_id
        else:
            ordered_pokeid1 = pokemon2_id
            ordered_pokeid2 = pokemon1_id
        matchup_index = str(ordered_pokeid1) + "_vs_" + str(ordered_pokeid2)

        if not matchup_index in data.keys():
            data[matchup_index] = {}
        data[matchup_index]["pokemon_1_id"] = ordered_pokeid1
        data[matchup_index]["pokemon_2_id"] = ordered_pokeid2
        data[matchup_index][str(pokemon1_id)+"_best_move"] = max_move
        data[matchup_index][str(pokemon1_id)+"_weighted_damage"] = max_damage
        data[matchup_index][str(pokemon1_id)+"_expected_TTK"] = math.ceil(1 / max_damage)
        data[matchup_index][str(pokemon1_id)+"_move_actual_damage"] = actual_max_damage
        data[matchup_index][str(pokemon1_id)+"_move_accuracy"] = max_move_accuracy
        replace_data(path, data)

    print("move " + max_move + " has most weight, with a weighted damage of " + str(max_damage * 100) + "%.")
    print("move actual damage: " + str(actual_max_damage * 100) + "%, accuracy: " + str(max_move_accuracy))

if __name__ == "__main__":
    #fetch all 1025 pokemon with ids 1 to 1025
    calculate_damage("389", "9")
    calculate_damage("9", "389")
    #diancie
    # fetch_pokemon("719")
    #fetch alternate forms with ids 10001 to 10325
    #mega-diancie
    # fetch_alt_form_pokemon("10075")
    #need to store abilities, forms, id, moves, name, stats, type, weight