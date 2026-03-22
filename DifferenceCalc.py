import os, json, time

#also install scipy
import pandas as pd
MATCHUPS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "weights")

if __name__ == "__main__":
    link_array = []
    point_array = []
    damage_edges = []
    TTK_edges = []
    for filename in os.listdir(MATCHUPS_DIR):
        cur_pokemon_id = filename[9:-5]
        
        with open(os.path.join(MATCHUPS_DIR, filename)) as f:
            matchup_data = json.load(f)
            total_weight_difference = 0
            num_links = 0
            for matchup in matchup_data:
                pokemon_ids = matchup.split("_vs_")
                pokemon1_id = cur_pokemon_id
                pokemon2_id = pokemon_ids[1]
                if pokemon2_id == pokemon1_id:
                    pokemon2_id = pokemon_ids[0]

                pokemon1_name = matchup_data[matchup][pokemon1_id + "_name"]
                pokemon2_name = matchup_data[matchup][pokemon2_id + "_name"]

                #remove megas and totems
                if "-mega" in pokemon1_name or "-mega" in pokemon2_name:
                    continue
                
                if "-totem" in pokemon1_name or "-totem" in pokemon2_name:
                    continue
                
                if "-gmax" in pokemon1_name or "-gmax" in pokemon2_name:
                    continue
                
                if "-eternamax" in pokemon1_name or "-eternamax" in pokemon2_name:
                    continue

                pokemon1_weight = matchup_data[matchup][pokemon1_id + "_weighted_damage"]
                if pokemon1_weight == None:
                    pokemon1_weight = 0
                pokemon2_weight = matchup_data[matchup][pokemon2_id + "_weighted_damage"]
                if pokemon2_weight == None:
                    pokemon2_weight = 0

                pokemon1_TTK = matchup_data[matchup][pokemon1_id + "_expected_TTK"]
                if pokemon1_TTK == None:
                    pokemon1_TTK = 0
                pokemon2_TTK = matchup_data[matchup][pokemon2_id + "_expected_TTK"]
                if pokemon2_TTK == None:
                    pokemon2_TTK = 0

                percent_difference = float(pokemon1_weight) - float(pokemon2_weight)
                #keep the pokemon's negative links for point sizes
                total_weight_difference += percent_difference
                num_links += 1
                #only keep pokemon's outgoing edges
                if percent_difference <= 0: 
                    continue
                TTK_difference = int(pokemon2_TTK) - int(pokemon1_TTK)

                link_array.append({"pokemon1_name": pokemon1_name, 
                                    "pokemon2_name": pokemon2_name, 
                                    "pokemon1_move": matchup_data[matchup][pokemon1_id + "_best_move"], 
                                    "pokemon2_move": matchup_data[matchup][pokemon2_id + "_best_move"],

                                    "pokemon1_move_weight": matchup_data[matchup][pokemon1_id + "_weighted_damage"],
                                    "pokemon2_move_weight": matchup_data[matchup][pokemon2_id + "_weighted_damage"],
                                    "edge_weight": percent_difference,

                                    "pokemon1_move_TTK": matchup_data[matchup][pokemon1_id + "_expected_TTK"],
                                    "pokemon2_move_TTK": matchup_data[matchup][pokemon2_id + "_expected_TTK"],
                                    "edge_TTK": TTK_difference
                                    })
            if num_links == 0:
                continue
            point_array.append({"pokemon1_name": pokemon1_name,
                                "pokemon_avg_edge_weight": (total_weight_difference/num_links)
                                })
    df = pd.DataFrame(link_array)
    df.to_csv("pokemon_link_data.csv", index_label='link_index')

    df = pd.DataFrame(point_array)
    df.to_csv("pokemon_point_data.csv", index_label='point_index')

