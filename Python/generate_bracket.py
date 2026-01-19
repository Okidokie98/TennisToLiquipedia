# main.py

# --- Imports (Required for the provided snippet) ---
import Settings.settings as settings
# Assuming 'Settings/flag_codes.py' exists and defines FLAG_REPLACEMENTS
from Settings.flag_codes import FLAG_REPLACEMENTS

import pyperclip
from bs4 import BeautifulSoup

try:
    with open("html_content.txt", "r", encoding="utf-8") as f:
        html = f.read()
except FileNotFoundError:
    print(
        "Error: 'html_content.txt' not found. Please ensure the HTML file is in the same directory."
    )
    exit()


# --- Variable and Function Dependencies (Imported from settings.py) ---
USE_FULL_NAME = settings.USE_FULL_NAME
PLAYER_COUNT = settings.PLAYER_COUNT
BEST_OF_SETS = settings.BEST_OF_SETS
DATE_FORMAT = settings.DATE_FORMAT
matches_per_round = settings.matches_per_round
format_player_name = (
    settings.format_player_name
)  # The helper function to clean up player names

# --- REDUNDANCY FIX: Import wiki_template directly from settings.py ---
wiki_template = settings.wiki_template


# --- Check for Doubles Format based on HTML structure ---
# We'll use a new setting/variable to determine if it's doubles.
# The presence of the 'atp-draw-container--doubles' class is a good indicator.
IS_DOUBLES = "atp-draw-container--doubles" in html


# --- START OF HTML TRANSFORMATION TO WIKICODE ---

soup = BeautifulSoup(html, "html.parser")


# Detect round (if present)
round_name = soup.select_one(".draw-header")
round_label = round_name.text.strip() if round_name else "Round"

# Find all matches
matches = soup.select(".draw-item")

# Initialize bracket with proper format
wiki_output = [f"{{{{Bracket|{wiki_template}|id=XXXXXXXXXX"]

# The flag_replacements dictionary is now imported as FLAG_REPLACEMENTS


# Convert matches into a list of processed matches (if any)
processed_matches = []

for match_index, match in enumerate(matches, start=1):
    bye_player = match.find("div", class_="name", string="Bye")
    if bye_player:
        continue  # Skip the rest of the loop for this match

    stats_items = match.select(".stats-item")
    if len(stats_items) < 2:
        continue # Skip if we don't have two opponents

    match_players = [] # List of lists: [[P1_T1, P2_T1], [P1_T2, P2_T2]]
    match_flags = []   # List of lists: [[F1_T1, F2_T1], [F1_T2, F2_T2]]

    # Process each team (stats_items[0] is Team 1, stats_items[1] is Team 2)
    for team_index, team_stats in enumerate(stats_items):
        
        # 🔴 FIX: Corrected CSS selectors based on the provided HTML structure
        # The parent divs '.names' and '.countries' do not exist in the source HTML.
        player_links = team_stats.select(".player-info .name a")
        flag_elements = team_stats.select(".player-info .country use")

        team_players = []
        team_flags = []

        # 🔴 LOGIC FOR PLAYER NAMES (WORKS FOR SOLO AND DUO)
        if IS_DOUBLES and len(player_links) >= 2:
            # Doubles: Each team has two players (DuoOpponent)
            for link in player_links:
                if USE_FULL_NAME:
                    href = link.get("href", "")
                    name = format_player_name(href)
                    team_players.append(name)
                else:
                    # Original logic: 'R. Nadal <span>(1)</span>' -> 'R. Nadal'
                    abbr_name = link.text.strip().split("(")[0].strip()
                    team_players.append(abbr_name)

            # 🏳️ LOGIC FOR FLAGS (DOUBLES)
            if len(flag_elements) >= 2:
                for f in flag_elements:
                    href = f.get("href", "")
                    flag_code = ""
                    if "#flag-" in href:
                        flag_code = href.split("#flag-")[1].lower()
                        # Using the imported FLAG_REPLACEMENTS
                        flag_code = FLAG_REPLACEMENTS.get(flag_code, flag_code)
                        team_flags.append(flag_code)
        
        elif not IS_DOUBLES and len(player_links) >= 1:
            # Singles: Each team is one player (SoloOpponent)
            link = player_links[0]
            if USE_FULL_NAME:
                href = link.get("href", "")
                name = format_player_name(href)
                team_players.append(name)
            else:
                abbr_name = link.text.strip().split("(")[0].strip()
                team_players.append(abbr_name)
                
            # 🏳️ LOGIC FOR FLAGS (SINGLES)
            if len(flag_elements) >= 1:
                f = flag_elements[0]
                href = f.get("href", "")
                flag_code = ""
                if "#flag-" in href:
                    flag_code = href.split("#flag-")[1].lower()
                    # Using the imported FLAG_REPLACEMENTS
                    flag_code = FLAG_REPLACEMENTS.get(flag_code, flag_code)
                    team_flags.append(flag_code)

        # Ensure we capture either [P1] for solo or [P1, P2] for duo
        match_players.append(team_players)
        match_flags.append(team_flags)


    # Check for the winner of the match, default is "draw"
    winner = 0

    if len(stats_items) >= 2:
        # Check P1 (.stats-item[0]) for the winner checkmark
        if stats_items[0].select_one(".winner .icon-checkmark"):
            winner = 1
        # Check P2 (.stats-item[1]) for the winner checkmark
        elif stats_items[1].select_one(".winner .icon-checkmark"):
            winner = 2

    # Note: ATPTour website structure often repeats score blocks for P1 and P2
    score_blocks = match.select(".scores")
    match_scores = []
    
    # Assuming the first half of .scores belongs to P1 and the second half to P2
    if len(score_blocks) >= 2:
        # P1 scores are typically in the first score block, P2 in the second
        # Extract only the main score from the span:first-child
        scores_p1 = [
            s.text.strip()
            for s in score_blocks[0].select(".score-item span:first-child")
            if s.text.strip()
        ]
        scores_p2 = [
            s.text.strip()
            for s in score_blocks[1].select(".score-item span:first-child")
            if s.text.strip()
        ]

        match_scores = list(zip(scores_p1, scores_p2))

    
    # Store data using a clear Team 1 / Team 2 structure
    # Duo format: players=[[p1_t1, p2_t1], [p1_t2, p2_t2]], flags=[[f1_t1, f2_t1], [f1_t2, f2_t2]]
    # Solo format: players=[[p1_t1], [p1_t2]], flags=[[f1_t1], [f1_t2]]
    processed_matches.append({
        "players": match_players, 
        "flags": match_flags, 
        "scores": match_scores, 
        "winner": winner
    })

# Generate bracket output round by round
match_counter = 0
for round_num, num_matches in matches_per_round.items():
    wiki_output.append(f"\n")
    for match_in_round in range(1, num_matches + 1):
        round_match_id = f"R{round_num}M{match_in_round}"

        if match_counter < len(processed_matches):
            m = processed_matches[match_counter]
            match_counter += 1

            # Team 1 Data
            team1_players = m["players"][0] if len(m["players"]) > 0 else []
            team2_players = m["players"][1] if len(m["players"]) > 1 else []
            team1_flags = m["flags"][0] if len(m["flags"]) > 0 else []
            team2_flags = m["flags"][1] if len(m["flags"]) > 1 else []

            # Determine player name strings and the Opponent Template
            if IS_DOUBLES:
                # DuoOpponent with named parameters: |p1=|p1flag=|p2=|p2flag=
                p1_str = team1_players[0] if len(team1_players) > 0 else ""
                p2_str = team1_players[1] if len(team1_players) > 1 else ""
                f1_str = team1_flags[0] if len(team1_flags) > 0 else ""
                f2_str = team1_flags[1] if len(team1_flags) > 1 else ""
                
                # Constructing the DuoOpponent template with named parameters
                team1_template = f"{{{{DuoOpponent|p1={p1_str}|p1flag={f1_str}|p2={p2_str}|p2flag={f2_str}}}}}"

                p3_str = team2_players[0] if len(team2_players) > 0 else ""
                p4_str = team2_players[1] if len(team2_players) > 1 else ""
                f3_str = team2_flags[0] if len(team2_flags) > 0 else ""
                f4_str = team2_flags[1] if len(team2_flags) > 1 else ""

                team2_template = f"{{{{DuoOpponent|p1={p3_str}|p1flag={f3_str}|p2={p4_str}|p2flag={f4_str}}}}}"
            else:
                # SoloOpponent with positional/named parameters (original logic)
                p1_str = team1_players[0] if len(team1_players) > 0 else ""
                f1_str = team1_flags[0] if len(team1_flags) > 0 else ""
                
                team1_template = f"{{{{SoloOpponent|{p1_str}|flag={f1_str}}}}}"

                p2_str = team2_players[0] if len(team2_players) > 0 else ""
                f2_str = team2_flags[0] if len(team2_flags) > 0 else ""

                team2_template = f"{{{{SoloOpponent|{p2_str}|flag={f2_str}}}}}"


            final_winner = m["winner"]  # Winner is 1 or 2 based on HTML order
            winner_param = ""
            
            # 🔴 TARGETED SWAP LOGIC (added missing logic for PLAYER_COUNT=24)
            swapped = False
            
            if PLAYER_COUNT == 28:
                if round_num == 2 and match_in_round in [6, 8]:
                    swapped = True
            
            if PLAYER_COUNT == 24: # Added missing swap logic for round 2 matches 2, 4, 6, 8
                if round_num == 2 and match_in_round in [2, 4, 6, 8]:
                    swapped = True

            if PLAYER_COUNT == 56: # Added missing swap logic for round 2 matches 2, 4, 6, 8
                if round_num == 2 and match_in_round in [4, 8, 12, 16]:
                    swapped = True
                    
            if PLAYER_COUNT == 96:
                if round_num == 2 and match_in_round in [
                    2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32,
                ]:
                    swapped = True
            
            # Apply swap logic for template parameters (opponents and scores)
            if swapped:
                team1_template, team2_template = team2_template, team1_template

                swapped_scores = []
                for score_p1_orig, score_p2_orig in m["scores"]:
                    swapped_scores.append((score_p2_orig, score_p1_orig))
                m["scores"] = swapped_scores
                
                # Also swap the winner if a swap occurred
                if m["winner"] == 1:
                    final_winner = 2
                elif m["winner"] == 2:
                    final_winner = 1


            if final_winner in [1, 2]:
                winner_param = f"|winner={final_winner}\n\t"

            # 🟢 Use BEST_OF_SETS setting
            match_entry = f"""|{round_match_id}={{{{Match
    {winner_param}|bestof={BEST_OF_SETS}
    |date={DATE_FORMAT}
    |opponent1={team1_template}
    |opponent2={team2_template}"""

            # Add map data - iterate up to BEST_OF_SETS
            for i in range(BEST_OF_SETS):
                if i < len(m["scores"]):
                    score1, score2 = m["scores"][i]
                    # Determine 'finished' state
                    finished = "true" if score1 and score2 else "skip"
                else:
                    score1 = score2 = ""
                    finished = "skip"

                match_entry += f"""
    |map{i+1}={{{{Map|map=Set {i+1}|score1={score1}|score2={score2}|finished={finished}}}}}"""

            match_entry += """
    }}"""
            wiki_output.append(match_entry)
        else:
            # Empty slot (no match data found)
            wiki_output.append(f"|{round_match_id}=")

wiki_output.append("}}")  # Close the bracket


# --- Output and Clipboard Logic (replacing Jupyter display) ---

print("\n--- GENERATED WIKI CODE ---\n")
final_output = "\n".join(wiki_output)

# 1. Print the output to the console
print(final_output)

# 2. Copy the final output to the clipboard
try:
    pyperclip.copy(final_output)
    print("\n✅ Successfully copied the Wiki Code to your clipboard!")
except pyperclip.PyperclipException as e:
    print(f"\n⚠️ Could not copy to clipboard. Ensure pyperclip is configured: {e}")