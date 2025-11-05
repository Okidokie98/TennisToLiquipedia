# main.py

# --- Imports (Required for the provided snippet) ---
from Settings import settings
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

# The wiki_template variable needs to be determined based on PLAYER_COUNT,
# which was done in settings.py's conditional logic. We redefine it here
# to ensure it's in scope for the provided snippet.
if PLAYER_COUNT == 128:
    wiki_template = "Bracket/128"
elif PLAYER_COUNT == 96:
    wiki_template = "Bracket/64L32DSSSSS"
elif PLAYER_COUNT == 64:
    wiki_template = "Bracket/64"
elif PLAYER_COUNT == 32:
    wiki_template = "Bracket/32"
elif PLAYER_COUNT == 28:
    wiki_template = "Bracket/4L2DH8LSH8H4L2DLSL"
elif PLAYER_COUNT == 24:
    wiki_template = "Bracket/16L8DSSS"
elif PLAYER_COUNT == 16:
    wiki_template = "Bracket/16"
else:
    # This should be caught in settings.py, but kept for robustness
    raise ValueError(f"Unsupported PLAYER_COUNT: {PLAYER_COUNT}.")


# --- START OF HTML TRANSFORMATION TO WIKICODE ---

soup = BeautifulSoup(html, "html.parser")


# Detect round (if present)
round_name = soup.select_one(".draw-header")
round_label = round_name.text.strip() if round_name else "Round"

# Find all matches
matches = soup.select(".draw-item")

# Initialize bracket with proper format
wiki_output = [f"{{{{Bracket|{wiki_template}|id=XXXXXXXXXX"]

# Convert matches into a list of processed matches (if any)
processed_matches = []

for match_index, match in enumerate(matches, start=1):
    player_links = match.select(".name a")

    bye_player = match.find("div", class_="name", string="Bye")
    if bye_player:
        continue  # Skip the rest of the loop for this match
    players = []

    # 🔴 LOGIC BASED ON USE_FULL_NAME SETTING
    if USE_FULL_NAME:
        # Extract full name from the link's href and format it
        for link in player_links:
            href = link.get("href", "")
            full_name = format_player_name(href)
            players.append(full_name)
    else:
        # Extract abbreviated name from the link's text
        for link in player_links:
            # Original logic: 'R. Nadal <span>(1)</span>' -> 'R. Nadal'
            abbr_name = link.text.strip().split("(")[0].strip()
            players.append(abbr_name)

    # 🏳️ Extract flag codes (if present)
    flag_elements = match.select(".country use")
    flags = []
    for f in flag_elements:
        href = f.get("href", "")
        flag_code = ""
        if "#flag-" in href:
            flag_code = href.split("#flag-")[1].lower()
            # Use the .get() method for a cleaner, safer lookup
            flag_code = FLAG_REPLACEMENTS.get(flag_code, flag_code)
            flags.append(flag_code)

    # Note: ATPTour website structure often repeats score blocks for P1 and P2
    score_blocks = match.select(".scores")

    # Check for the winner of the match, default is "draw"
    winner = 0

    stats_items = match.select(".stats-item")

    if len(stats_items) >= 2:
        # Check P1 (.stats-item[0]) for the winner checkmark
        if stats_items[0].select_one(".winner .icon-checkmark"):
            winner = 1
        # Check P2 (.stats-item[1]) for the winner checkmark
        elif stats_items[1].select_one(".winner .icon-checkmark"):
            winner = 2

    match_data = {"players": players, "flags": flags, "scores": [], "winner": winner}

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

        match_data["scores"] = list(zip(scores_p1, scores_p2))

    processed_matches.append(match_data)

# Generate bracket output round by round
match_counter = 0
for round_num, num_matches in matches_per_round.items():
    wiki_output.append(f"\n")
    for match_in_round in range(1, num_matches + 1):
        round_match_id = f"R{round_num}M{match_in_round}"

        if match_counter < len(processed_matches):
            m = processed_matches[match_counter]
            match_counter += 1

            p1 = m["players"][0] if len(m["players"]) > 0 else ""
            p2 = m["players"][1] if len(m["players"]) > 1 else ""

            # 🏁 Get flags (default empty if missing)
            flag1 = m["flags"][0] if len(m["flags"]) > 0 else ""
            flag2 = m["flags"][1] if len(m["flags"]) > 1 else ""

            winner_param = ""

            # 🔴 TARGETED SWAP FOR R2 MATCHES (adjusting the order for the template)
            if PLAYER_COUNT == 28:
                if round_num == 2 and match_in_round in [6, 8]:
                    # Swap players if the template requires the 2nd player in the raw data to be opponent1
                    p1, p2 = p2, p1
                    flag1, flag2 = flag2, flag1

                    swapped_scores = []
                    for score_p1_orig, score_p2_orig in m["scores"]:
                        swapped_scores.append(
                            (score_p2_orig, score_p1_orig)
                        )  # Swap them here
                    m["scores"] = swapped_scores

            if PLAYER_COUNT == 96:
                if round_num == 2 and match_in_round in [
                    2,
                    4,
                    6,
                    8,
                    10,
                    12,
                    14,
                    16,
                    18,
                    20,
                    22,
                    24,
                    26,
                    28,
                    30,
                    32,
                ]:
                    # Swap players if the template requires the 2nd player in the raw data to be opponent1
                    p1, p2 = p2, p1
                    flag1, flag2 = flag2, flag1

                    swapped_scores = []
                    for score_p1_orig, score_p2_orig in m["scores"]:
                        swapped_scores.append(
                            (score_p2_orig, score_p1_orig)
                        )  # Swap them here
                    m["scores"] = swapped_scores

            final_winner = m["winner"]  # Start with the winner from the HTML order

            # Check if the players were swapped by the custom logic
            # (This is a complex check, let's assume the players were swapped if either of your PLAYER_COUNT blocks executed)

            # A simple way to check if a swap happened:
            # Compare final p1 to original player 1 (m["players"][0])
            original_p1_name = m["players"][0] if len(m["players"]) > 0 else ""

            if p1 == original_p1_name:
                # No swap occurred relative to the original processed_match order
                final_winner = m["winner"]
            else:
                # Swap occurred (p1 is now original p2)
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
    |opponent1={{{{SoloOpponent|{p1}|flag={flag1}}}}}
    |opponent2={{{{SoloOpponent|{p2}|flag={flag2}}}}}"""

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

# --- END OF USER-PROVIDED CODE SNIPPET ---


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
