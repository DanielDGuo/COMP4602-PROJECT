import requests as re
import json, os
import math, time

base_url = "https://pokeapi.co/api/v2"
matchup_dict = {}
pokemon_dict = {}
moves_dict = {}
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

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

    if pokemon_id in pokemon_dict.keys():
        return pokemon_dict[pokemon_id]
    
    #create the cache directory for pokemon
    os.makedirs(os.path.join(CACHE_DIR, "pokemon_by_id"), exist_ok=True)

    #set the path for the json file
    path = os.path.join(CACHE_DIR, "pokemon_by_id", "pokemon_" + pokemon_id + ".json")

    #if it exists, it's been fetched before. Get the file from the cache instead of making an API request
    if os.path.exists(path):
        with open(path) as f:
            # print("file for pokemon " + str(pokemon_id) + " found in cache")
            pokemon_dict[pokemon_id] = json.load(f)
            return pokemon_dict[pokemon_id]

    #make an API request for the pokemon
    print("file fetched for pokemon " + str(pokemon_id))
    #fetch URL
    url = f"{base_url}/pokemon/{pokemon_id}"
    response = re.get(url)

    if response.status_code == 200:
        #format the data before dumping it into the file
        data = response.json()
        for key in ["base_experience", "cries", "forms", "game_indices", "height", "held_items", "is_default", "location_area_encounters", "order", "past_abilities", "past_stats", "past_types", "sprites"]:
            data.pop(key, None)

        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        pokemon_dict[pokemon_id] = data
        return pokemon_dict[pokemon_id]
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
    
    if pokemon_id in pokemon_dict.keys():
        return pokemon_dict[pokemon_id]
    
    #create the cache directory for pokemon
    os.makedirs(os.path.join(CACHE_DIR, "pokemon_by_id"), exist_ok=True)

    #set the path for the json file
    path = os.path.join(CACHE_DIR, "pokemon_by_id", "pokemon_" + pokemon_id + ".json")

    #if it exists, it's been fetched before. Get the file from the cache instead of making an API request
    if os.path.exists(path):
        with open(path) as f:
            # print("file found in cache")
            pokemon_dict[pokemon_id] = json.load(f)
            return pokemon_dict[pokemon_id]

    #make an API request for the pokemon
    print("file fetched for pokemon " + str(pokemon_id))
    #fetch URL
    url = f"{base_url}/pokemon/{pokemon_id}"
    response = re.get(url)

    if response.status_code == 200:
        #format the data before dumping it into the file
        data = response.json()
        for key in ["base_experience", "cries", "forms", "game_indices", "height", "held_items", "is_default", "location_area_encounters", "order", "past_abilities", "past_stats", "past_types", "sprites"]:
            data.pop(key, None)

        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        pokemon_dict[pokemon_id] = data
        return pokemon_dict[pokemon_id]
    else:
        #pokemon doesn't exist, return an error message
        raise re.exceptions.HTTPError("PokemonAPI endpoint not found. Name error. Error " + str(response.status_code))

#fetches moves by ID. Ignores moves with no power
#fetch all valid moves first -> if a pokemon uses a move not in the list of fetched moves, the move must be invalid.
#ignore healing effects
#list of moves that should exist are here: https://bulbapedia.bulbagarden.net/wiki/List_of_moves_that_do_damage
def fetch_move(move_id):
    if int(move_id) < 1 or int(move_id) > 919:
        raise ValueError("Move ID must be between 1 and 919(Move 920 - 'Nihil Light' is not in PokeAPI).")
    
    if move_id in moves_dict.keys():
        return moves_dict[move_id]
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
            # print("file for move " + str(move_id) + " found in cache")
            if "is_status" in data.keys():
                # print("move " + str(move_id) + " is a status move. Ignored.")
                return -1
            if "is_weird_move" in data.keys():
                # print("move " + str(move_id) + " has None power and has a move that scales weirdly. Ignored.")
                return -1
            moves_dict[move_id] = data
            return moves_dict[move_id]

    #make an API request for the pokemon
    print("file fetched for move " + str(move_id))
    response = re.get(url)

    if response.status_code == 200:
        #format the data before dumping it into the file
        data = response.json()
        #ignore status moves
        if data["damage_class"]["name"] == "status":
            # print("Move " + move_id + " is a status move.")
            data = {}
            data["is_status"] = True        
            with open(path, "w") as f:
                json.dump(data, f, indent=4)
            return -1
        #handle moves with power that depend on other factors
        if data["power"] == None:
            # some moves that do deal damage have weird damage calculations. They do NOT appear in the list.
            valid_null_power_moves = ["electro-ball", "frustration", "grass-knot", "gyro-ball", "heat-crash", "heavy-slam", "low-kick", "return", "fissure", "guillotine", "horn-drill", "sheer-cold"]
            if data["name"] not in valid_null_power_moves:
                print("Move " + move_id + " has no power and does not have a scaling power.")
                data = {}
                data["is_weird_move"] = True        
                with open(path, "w") as f:
                    json.dump(data, f, indent=4)
                return -1
            #catch friendship-based moves
            elif data["name"] == "frustration" or data["name"] == "return":
                    data["power"] = 102
        #handle moves that cause the user to faint(lose)
        if data["name"] in ["explosion", "misty-explosion", "self-destruct"]:
                print("Move " + move_id + " causes the user to faint, and as such is ignored.")
                data = {}
                data["is_weird_move"] = True        
                with open(path, "w") as f:
                    json.dump(data, f, indent=4)
                return -1
        #handle moves that can only be used as the first move
        if data["name"] in ["fake-out", "first-impression"]:
                print("Move " + move_id + " can only be used as the first move. Ignored for simplicity.")
                data = {}
                data["is_weird_move"] = True        
                with open(path, "w") as f:
                    json.dump(data, f, indent=4)
                return -1
        
        #handle moves that cause the user to faint(lose)
        if data["name"] in ["hidden-power", "ivy-cudgel", "aura-wheel", "judgement", "multi-attack", "raging-bull", "revelation-dance", "techno-blast", ""]:
                print("Move " + move_id + " can be change type. Type effectiveness ignored.")
                data["type"]["name"] = None
        
        #moves that always hit have what basically is 100 accuracy
        if data["accuracy"] == None:
            data["accuracy"] = 100





        ### CALCULATE WEIGHT BONUSES AND PENALTIES ###
        data["bonuses"] = {}

        charge_bonus = 1
        #handle moves that require a vulnerable charging turn
        if data["name"] in ["electro-shot", "freeze-shock", "ice-burn", "meteor-beam", "razor-wind", "skull-bash", "sky-attack", "solar-beam", "solar-blade"]:
            #opponent has a free move and can expect it coming
            charge_bonus = 0.35
        #handle moves that require a semi-invulnerable charging turn
        if data["name"] in ["bounce", "dig", "dive", "fly", "phantom-force", "shadow-force"]:
            #opponent can expect it coming
            charge_bonus = 0.45
        #sky drop is ignored; under thought-out circumstances, both sides lose a turn
        data["bonuses"]["charge_bonus"] = charge_bonus

        recharge_bonus = 1
        #handle moves that require a recharge
        if data["name"] in ["blast-burn", "eternabeam", "frenzy-plant", "giga-impact", "hydro-cannon", "hyper-beam", "meteor-assault", "prismatic-laser", "roar-of-time", "rock-wrecker"]:
            #opponent has a free move after the move is used. Can't see it coming.
            recharge_bonus = 0.55
        data["bonuses"]["recharge_bonus"] = recharge_bonus

        always_crit_bonus = 1
        #handle moves that always crit
        if data["name"] in ["flower-trick", "frost-breath", "storm-throw", "surging-strikes", "wicked-blow"]:
            #crits do 1.5x damage
            always_crit_bonus = 1.5
        data["bonuses"]["always_crit_bonus"] = always_crit_bonus

        drain_bonus = 1
        #handle moves that drain hp or have recoil damage
        if data["meta"] != None and data["meta"]["drain"] != 0:
            #half the penalty if it's recoil; controlled recoil
            if data["meta"]["drain"] < 0:
                drain_bonus = 1 + ((data["meta"]["drain"]/100.0)/2.0)
            #healing is always good
            else:
                drain_bonus = 1 + (data["meta"]["drain"]/100.0)
        elif data["name"] == "chloroblast" or data["name"] == "steel-beam":
            #catch chloroblast; always takes 50% recoil based on user max hp
            #half the damage like other recoil moves even if its a constant
            drain_bonus = 0.75
        data["bonuses"]["drain_bonus"] = drain_bonus

        crash_bonus = 1
        #handle moves that crash on a miss
        if data["name"] in ["axe-kick", "high-jump", "jump-kick", "supercell-slam"]:
            #on miss, always take damage equal to half the user hp
            crash_bonus = 1 - (0.5 * (100-data["accuracy"])/100.0)
        data["bonuses"]["crash_bonus"] = crash_bonus

        target_asleep_bonus = 1
        #handle dream eater
        if data["name"] == "dream-eater":
            #REQUIRES the target to be asleep. Needs at a decent amount of work to prepare
            target_asleep_bonus = 0.25
        data["bonuses"]["target_asleep_bonus"] = target_asleep_bonus
            
        consecutive_move_bonus = 1
        #handle moves that lock you into using that move for a few turns
        if data["name"] in ["ice-ball", "outrage", "petal-dance", "raging-fury", "rollout", "thrash", "uproar"]:
            #negative as they're predictable and removes you ability to adapt
            consecutive_move_bonus = 0.8
            #decrease the bonus farther if it confuses the user at the end
            if data["name"] in ["outrage", "petal-dance", "raging-fury", "thrash"]:
                consecutive_move_bonus = 0.7
            #increase the effective weight of moves that increase in power each turn theyre used. Still not good moves.
            if data["name"] in ["ice-ball", "rollout"]:
                consecutive_move_bonus = 1.5
        data["bonuses"]["consecutive_move_bonus"] = consecutive_move_bonus

        delayed_bonus = 1
        #handle moves that occur in 2 turns
        if data["name"] in ["future-sight", "doom-desire"]:
            #negative as they're predictable
            delayed_bonus = 0.8
        data["bonuses"]["delayed_bonus"] = delayed_bonus

        priority_bonus = 1
        #handle moves that have modified priority
        #positive priority moves strike first
        #first impression, fake out was handled earlier
        if data["name"] in ["water-shuriken", "wacuum-wave", "thunderclap", "sucker-punch", "feint", "upper-hand"]:
            priority_bonus = 1.25
            #thunderclap, sucker punch requires the enemy to be using an attack
            if data["name"] in ["thunderclap", "sucker-punch"]:
                priority_bonus = 1
            #feint requires the opponent to have used protect or detect
            if data["name"] in ["feint"]:
                priority_bonus = 0.1
            #feint requires the opponent to be using an increased priority move
            if data["name"] in ["upper-hand"]:
                priority_bonus = 0.2

        #negative priority moves strike last
        elif data["name"] in ["dragon-tail", "circle-throw", "avalanche", "shell-trap", "focus-punch", "beak-blast"]:
            priority_bonus = 0.75
            #avalanche double in power if the user was damaged(e.g if the opponent used an attack)
            if data["name"] in ["avalanche"]:
                priority_bonus = 1.4
            #shell trap requries the user to be hit like avalanche
            if data["name"] in ["avalanche"]:
                priority_bonus = 0.7
            #focus punch requires the user to NOT be hit
            if data["name"] in ["focus-punch"]:
                priority_bonus = 0.2

        data["bonuses"]["priority_bonus"] = priority_bonus
        
        #multihit move bonus
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
        data["bonuses"]["multihit_bonus"] = multihit_bonus

        #penalize the accuracy 2x
        accuracy_bonus = 100 - 2*(100 - data["accuracy"])
        data["bonuses"]["accuracy_bonus"] = accuracy_bonus / 100.0

        ### END OF WEIGHT BONUSES AND PENALTIES ###




        for key in ["contest_combos", "contest_type", "contest_effect", "effect_changes", "generation", "learned_by_pokemon", "flavor_text_entries", "machines", "names", "past_values", "super_contest_effect"]:
            data.pop(key, None)

        for entry in data["effect_entries"]:
            if entry["language"]["name"] != "en":
                data["effect_entries"].remove(entry)

        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        moves_dict[move_id] = data
        return moves_dict[move_id]
    else:
        #move id doesn't exist, return an error message
        raise re.exceptions.HTTPError("PokemonAPI endpoint not found. Name error. Error " + str(response.status_code))


#get stats at lv100
#returns a dict
def calculate_stats(pokemon_id):
    max_stats = {}
    pokemon_data = None
    if int(pokemon_id) < 1026:
        pokemon_data = fetch_pokemon(pokemon_id)
    else:
        pokemon_data = fetch_alt_form_pokemon(pokemon_id)
    if "max_stats" in pokemon_data.keys():
        return pokemon_data["max_stats"]
    base_stats = pokemon_data["stats"]

    for stat in base_stats:
        match stat["stat"]["name"]:
            case "hp":
                #shedninja is the exception
                if pokemon_id == "292":
                    max_stats["hp"] = 1
                else:
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
    if atk_type == None:
        return 1
    type1_effectiveness = 1
    type2_effectiveness = 1
    if def_type1 in type_effectiveness[atk_type]:
        type1_effectiveness = type_effectiveness[atk_type][def_type1]
    if def_type2 in type_effectiveness[atk_type] and def_type2 != None:
        type2_effectiveness = type_effectiveness[atk_type][def_type2]

    return 1 * type1_effectiveness * type2_effectiveness

def calculate_damage(pokemon1_id, pokemon2_id):
    #general data
    pokemon1_data = None
    pokemon2_data = None
    if int(pokemon1_id) < 1026:
        pokemon1_data = fetch_pokemon(pokemon1_id)
    else:
        pokemon1_data = fetch_alt_form_pokemon(pokemon1_id)

    if int(pokemon2_id) < 1026:
        pokemon2_data = fetch_pokemon(pokemon2_id)
    else:
        pokemon2_data = fetch_alt_form_pokemon(pokemon2_id)

    #stats
    pokemon1_stats = calculate_stats(pokemon1_id)
    pokemon2_stats = calculate_stats(pokemon2_id)
    #calculate the best move for pokemon 1 to use
    #damage calculator needs power
    max_damage = -1
    actual_max_damage = -1
    max_move = "None"
    max_move_accuracy = -1
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
            raise ValueError("Expected physical or special move. Recieved " + damage_class + " for move with move_id " + str(move_id))
    
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
            damage = 0
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

                    bonus = 1
                    for b in move_data["bonuses"]:
                        bonus *= float(move_data["bonuses"][b])
                    damage = (bonus * calculate_move_damage(100, attacker_stat, defender_stat, power, type_effectiveness, stab)) / pokemon2_stats["hp"]
                case "low-kick":
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

                    bonus = 1
                    for b in move_data["bonuses"]:
                        bonus *= float(move_data["bonuses"][b])
                    damage = (bonus * calculate_move_damage(100, attacker_stat, defender_stat, power, type_effectiveness, stab)) / pokemon2_stats["hp"]
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

                    bonus = 1
                    for b in move_data["bonuses"]:
                        bonus *= float(move_data["bonuses"][b])
                    damage = (bonus * calculate_move_damage(100, attacker_stat, defender_stat, power, type_effectiveness, stab)) / pokemon2_stats["hp"]
                case "heat-crash":
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

                    bonus = 1
                    for b in move_data["bonuses"]:
                        bonus *= float(move_data["bonuses"][b])
                    damage = (bonus * calculate_move_damage(100, attacker_stat, defender_stat, power, type_effectiveness, stab)) / pokemon2_stats["hp"]
                case "gyro-ball":
                    power = min(150, (25*(pokemon2_stats["spe"])/(pokemon1_stats["spe"])) + 1)

                    bonus = 1
                    for b in move_data["bonuses"]:
                        bonus *= float(move_data["bonuses"][b])
                    damage = (bonus * calculate_move_damage(100, attacker_stat, defender_stat, power, type_effectiveness, stab)) / pokemon2_stats["hp"]
                case "electro-ball":
                    spe_ratio = pokemon2_stats["spe"]/pokemon1_stats["spe"]
                    if spe_ratio > 1:
                        power = 40
                    elif spe_ratio > .5:
                        power = 60
                    elif spe_ratio > .3333:
                        power = 80
                    elif spe_ratio > .25:
                        power = 120
                    else:
                        power = 150
                    
                    bonus = 1
                    for b in move_data["bonuses"]:
                        bonus *= float(move_data["bonuses"][b])
                    damage = (bonus * calculate_move_damage(100, attacker_stat, defender_stat, power, type_effectiveness, stab)) / pokemon2_stats["hp"]
                #OHKO moves hit 30% of the time -> penalize them heavily for being very inconsistent
                case "fissure":
                    damage = (0.15 * pokemon2_stats["hp"])/pokemon2_stats["hp"]
                    if max_damage < damage:
                        max_damage = damage
                        actual_max_damage = 1.0
                        max_move = move["move"]["name"]
                        max_move_accuracy = move_data["accuracy"]
                case "guillotine":
                    damage = (0.15 * pokemon2_stats["hp"])/pokemon2_stats["hp"]
                    if max_damage < damage:
                        max_damage = damage
                        actual_max_damage = 1.0
                        max_move = move["move"]["name"]
                        max_move_accuracy = move_data["accuracy"]
                case "horn-drill":
                    damage = (0.15 * pokemon2_stats["hp"])/pokemon2_stats["hp"]
                    if max_damage < damage:
                        max_damage = damage
                        actual_max_damage = 1.0
                        max_move = move["move"]["name"]
                        max_move_accuracy = move_data["accuracy"]
                case "sheer-cold":
                    damage = (0.15 * pokemon2_stats["hp"])/pokemon2_stats["hp"]
                    if max_damage < damage:
                        max_damage = damage
                        actual_max_damage = 1.0
                        max_move = move["move"]["name"]
                        max_move_accuracy = move_data["accuracy"]
                case _:
                    print(move["move"]["name"] + " has None power. Create an edge case to manually set.")
            if max_damage < damage:
                max_damage = damage
                actual_max_damage = (move_data["bonuses"]["multihit_bonus"] * calculate_move_damage(100, attacker_stat, defender_stat, power, type_effectiveness, stab)) / pokemon2_stats["hp"]
                max_move = move["move"]["name"]
                max_move_accuracy = move_data["accuracy"]

        #expected damages for triple axel and kick
        elif is_triple_axel:
            damage = (move_data["bonuses"]["accuracy_bonus"] * calculate_move_damage(100, attacker_stat, defender_stat, 20, type_effectiveness, stab)) / pokemon2_stats["hp"] +\
                        (move_data["bonuses"]["accuracy_bonus"] * move_data["bonuses"]["accuracy_bonus"] * calculate_move_damage(100, attacker_stat, defender_stat, 40, type_effectiveness, stab)) / pokemon2_stats["hp"] +\
                        (move_data["bonuses"]["accuracy_bonus"] * move_data["bonuses"]["accuracy_bonus"] * move_data["bonuses"]["accuracy_bonus"] * calculate_move_damage(100, attacker_stat, defender_stat, 60, type_effectiveness, stab)) / pokemon2_stats["hp"]
            if max_damage < damage:
                max_damage = damage
                actual_max_damage = (calculate_move_damage(100, attacker_stat, defender_stat, 20, type_effectiveness, stab)) / pokemon2_stats["hp"] +\
                                    (calculate_move_damage(100, attacker_stat, defender_stat, 40, type_effectiveness, stab)) / pokemon2_stats["hp"] +\
                                    (calculate_move_damage(100, attacker_stat, defender_stat, 60, type_effectiveness, stab)) / pokemon2_stats["hp"]
                max_move = move["move"]["name"]
                max_move_accuracy = move_data["accuracy"]
        elif is_triple_kick:
            damage = (move_data["bonuses"]["accuracy_bonus"] * calculate_move_damage(100, attacker_stat, defender_stat, 10, type_effectiveness, stab)) / pokemon2_stats["hp"] +\
                        (move_data["bonuses"]["accuracy_bonus"] * move_data["bonuses"]["accuracy_bonus"] * calculate_move_damage(100, attacker_stat, defender_stat, 20, type_effectiveness, stab)) / pokemon2_stats["hp"] +\
                        (move_data["bonuses"]["accuracy_bonus"] * move_data["bonuses"]["accuracy_bonus"] * move_data["bonuses"]["accuracy_bonus"] * calculate_move_damage(100, attacker_stat, defender_stat, 30, type_effectiveness, stab)) / pokemon2_stats["hp"]
            if max_damage < damage:
                max_damage = damage
                actual_max_damage = (calculate_move_damage(100, attacker_stat, defender_stat, 10, type_effectiveness, stab)) / pokemon2_stats["hp"] +\
                                    (calculate_move_damage(100, attacker_stat, defender_stat, 20, type_effectiveness, stab)) / pokemon2_stats["hp"] +\
                                    (calculate_move_damage(100, attacker_stat, defender_stat, 30, type_effectiveness, stab)) / pokemon2_stats["hp"]
                max_move = move["move"]["name"]
                max_move_accuracy = move_data["accuracy"]
        
        #all normal moves
        else:
            #check if the move can cause the target to flinch
            flinch_bonus = 1
            #can only flinch if you attack first; simplified to a speed check.
            if pokemon1_stats["spe"] > pokemon2_stats["spe"]:
                if move_data["meta"] != None and "flinch_chance" in move_data["meta"].keys() and int(move_data["meta"]["flinch_chance"]) > 0 and move_data["name"] != "double-iron-bash":
                    flinch_bonus = 1 + int(move_data["meta"]["flinch_chance"])/100.0
                #handle triple arrows
                elif move_data["name"] == "triple-arrows":
                    flinch_bonus = 1.3
                #handle double-iron-bash; has 2 hits, so it has a 51% chance to flinch.
                elif move_data["name"] == "triple-arrows":
                    flinch_bonus = 1.51


            bonus = flinch_bonus
            for b in move_data["bonuses"]:
                bonus *= float(move_data["bonuses"][b])
            damage = (bonus * calculate_move_damage(100, attacker_stat, defender_stat, power, type_effectiveness, stab)) / pokemon2_stats["hp"]
            if max_damage < damage:
                max_damage = damage
                #multihit bonus is the only one to inccrease the maximum damage; others only effect the weight
                actual_max_damage = (move_data["bonuses"]["multihit_bonus"] * calculate_move_damage(100, attacker_stat, defender_stat, power, type_effectiveness, stab)) / pokemon2_stats["hp"]
                max_move = move["move"]["name"]
                max_move_accuracy = move_data["accuracy"]

    ordered_pokeid1 = "-1"
    ordered_pokeid2 = "-1"

    if int(pokemon1_id) < int(pokemon2_id):
        ordered_pokeid1 = pokemon1_id
        ordered_pokeid2 = pokemon2_id
    else:
        ordered_pokeid1 = pokemon2_id
        ordered_pokeid2 = pokemon1_id
    
    matchup_index = str(ordered_pokeid1) + "_vs_" + str(ordered_pokeid2)

    if not matchup_index in matchup_dict.keys():
        matchup_dict[matchup_index] = {}
    matchup_dict[matchup_index]["pokemon_1_id"] = ordered_pokeid1
    matchup_dict[matchup_index]["pokemon_2_id"] = ordered_pokeid2
    if max_damage > 0:
        matchup_dict[matchup_index][str(pokemon1_id)+"_name"] = pokemon1_data["name"]
        matchup_dict[matchup_index][str(pokemon1_id)+"_best_move"] = max_move
        matchup_dict[matchup_index][str(pokemon1_id)+"_weighted_damage"] = max_damage
        matchup_dict[matchup_index][str(pokemon1_id)+"_expected_TTK"] = math.ceil(1 / max_damage)
        matchup_dict[matchup_index][str(pokemon1_id)+"_move_actual_damage"] = actual_max_damage
        matchup_dict[matchup_index][str(pokemon1_id)+"_move_accuracy"] = max_move_accuracy
    elif max_damage == 0:
        # pokemon have no damaging moves(e.g a pokemon that only knows normal moves against a ghost type)
        matchup_dict[matchup_index][str(pokemon1_id)+"_name"] = pokemon1_data["name"]
        matchup_dict[matchup_index][str(pokemon1_id)+"_best_move"] = max_move
        matchup_dict[matchup_index][str(pokemon1_id)+"_weighted_damage"] = max_damage
        matchup_dict[matchup_index][str(pokemon1_id)+"_expected_TTK"] = None
        matchup_dict[matchup_index][str(pokemon1_id)+"_move_actual_damage"] = actual_max_damage
        matchup_dict[matchup_index][str(pokemon1_id)+"_move_accuracy"] = max_move_accuracy
    else:
        # ditto, wynaut, waubuffet, smeargle, pyukumuku, cosmog, cosmoem (132 202 235 360 771 789 790)
        # also includes some alt form pokemon who do not have move entries (e.g gmax, some megas)
        matchup_dict[matchup_index][str(pokemon1_id)+"_name"] = pokemon1_data["name"]
        matchup_dict[matchup_index][str(pokemon1_id)+"_best_move"] = None
        matchup_dict[matchup_index][str(pokemon1_id)+"_weighted_damage"] = None
        matchup_dict[matchup_index][str(pokemon1_id)+"_expected_TTK"] = None
        matchup_dict[matchup_index][str(pokemon1_id)+"_move_actual_damage"] = None
        matchup_dict[matchup_index][str(pokemon1_id)+"_move_accuracy"] = None
    # print("move " + max_move + " has most weight, with a weighted damage of " + str(max_damage * 100) + "%.")
    # print("move actual damage: " + str(actual_max_damage * 100) + "%, accuracy: " + str(max_move_accuracy))

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    start_time = time.perf_counter()

    #get each matchup by getting all outgoing edges of all pokemon Takes ~30 seconds each pokemon
    print("calculating normal pokemon moves")
    for id1 in range(1, 1026):
        matchup_dict = {}
        path = os.path.join(OUTPUT_DIR, "matchups_" + str(id1) + ".json")
        pokemon_start_time = time.perf_counter()
        #normal pokemon
        for id2 in range(1, 1026):
            calculate_damage(str(id1), str(id2))
            calculate_damage(str(id2), str(id1))
        #alt form pokemon
        for id2 in range(10001, 10326):
            calculate_damage(str(id1), str(id2))
            calculate_damage(str(id2), str(id1))
        pokemon_end_time = time.perf_counter()
        execution_time = pokemon_end_time - pokemon_start_time
        total_execution_time = pokemon_end_time - start_time
        print(str(id1) + f" normal pokemon calculated out of 1025. Took {execution_time:.2f} seconds ({total_execution_time:.2f} total seconds elapsed).")
        
        with open(path, "w") as f:
            json.dump(matchup_dict, f, indent=4)  
        
    print("calculating alt form pokemon moves")
    for id1 in range(10001, 10325):
        matchup_dict = {}
        path = os.path.join(OUTPUT_DIR, "matchups_" + str(id1) + ".json")
        pokemon_start_time = time.perf_counter()
        #normal pokemon
        for id2 in range(1, 1026):
            calculate_damage(str(id1), str(id2))
            calculate_damage(str(id2), str(id1))
        #alt form pokemon
        for id2 in range(10001, 10326):
            calculate_damage(str(id1), str(id2))
            calculate_damage(str(id2), str(id1))
        pokemon_end_time = time.perf_counter()
        execution_time = pokemon_end_time - pokemon_start_time
        total_execution_time = pokemon_end_time - start_time
        print(str(id1 - 10000) + f" alt form pokemon calculated out of 325. Took {execution_time:.2f} seconds ({total_execution_time:.2f} total seconds elapsed).")
        
        with open(path, "w") as f:
            json.dump(matchup_dict, f, indent=4)  

    #dump the complete matchup dict to a file
    with open(path, "w") as f:
        json.dump(matchup_dict, f, indent=4)  

    end_time = time.perf_counter()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time:.2f} seconds")