# --- Configuration Settings ---

# SETTING 1: Player Name Format
# Set to True to use the full name extracted from the URL (e.g., "Rafael Nadal")
# Set to False to use the abbreviated name from the link text (e.g., "R. Nadal")
USE_FULL_NAME = True

# SETTING 2: Tournament Size (16, 24, 28, 32, 64, 96 or 128)
PLAYER_COUNT = 32

# SETTING 3: Best-of Format
# Determines the maximum number of sets in a match (e.g., 5 for Grand Slam men's, 3 other events)
BEST_OF_SETS = 3

# SETTING 4: Date
# Determines the date format for matches (e.g., "YYYY-MM-DD")
DATE_FORMAT = "YYYY-MM-DD"


# --- Helper Function ---
def format_player_name(url):
    """Extracts player name from URL and formats it to Title Case (e.g., 'rafael-nadal' -> 'Rafael Nadal')."""
    if not url or "/en/players/" not in url:
        return ""

    # Get the part between '/en/players/' and the player ID '/n409/overview'
    try:
        name_part = url.split("/en/players/")[1].split("/")[0]
        # Replace hyphens with spaces and capitalize the first letter of each word
        formatted_name = " ".join(word.capitalize() for word in name_part.split("-"))
        return formatted_name
    except IndexError:
        return ""


# --- Round Setups ---
# Define matches per round and round labels dynamically based on PLAYER_COUNT
if PLAYER_COUNT == 128:
    wiki_template = "Bracket/128"
    matches_per_round = {
        1: 64,  # Round 1
        2: 32,  # Round 2
        3: 16,  # Round 3
        4: 8,  # Round 4
        5: 4,  # Quarterfinals
        6: 2,  # Semifinals
        7: 1,  # Grand Final
    }
    round_labels = {
        1: "Round 1",
        2: "Round 2",
        3: "Round 3",
        4: "Round 4",
        5: "Quarterfinals",
        6: "Semifinals",
        7: "Grand Final",
    }
elif PLAYER_COUNT == 96:
    wiki_template = "Bracket/64L32DSSSSS"
    matches_per_round = {
        1: 32,  # Round 1
        2: 32,  # Round 1
        3: 16,  # Round 2
        4: 8,  # Round 3
        5: 4,  # Quarterfinals
        6: 2,  # Semifinals
        7: 1,  # Grand Final
    }
    round_labels = {
        1: "Round 1",
        2: "Round 2",
        3: "Round 3",
        4: "Round 4",
        5: "Quarterfinals",
        6: "Semifinals",
        7: "Grand Final",
    }
elif PLAYER_COUNT == 64:
    wiki_template = "Bracket/64"
    matches_per_round = {
        1: 32,  # Round 1
        2: 16,  # Round 2
        3: 8,  # Round 3
        4: 4,  # Quarterfinals
        5: 2,  # Semifinals
        6: 1,  # Grand Final
    }
    round_labels = {
        1: "Round 1",
        2: "Round 2",
        3: "Round 3",
        4: "Round 4",
        5: "Quarterfinals",
        6: "Grand Final",
    }
elif PLAYER_COUNT == 32:
    wiki_template = "Bracket/32"
    matches_per_round = {
        1: 16,  # Round of 32
        2: 8,  # Round of 16
        3: 4,  # Quarterfinals
        4: 2,  # Semifinals
        5: 1,  # Grand Final
    }
    round_labels = {
        1: "Round of 32",
        2: "Round of 16",
        3: "Quarterfinals",
        4: "Semifinals",
        5: "Grand Final",
    }
elif PLAYER_COUNT == 28:
    wiki_template = "Bracket/4L2DH8LSH8H4L2DLSL"
    matches_per_round = {
        1: 12,  # Round of 28
        2: 8,  # Round of 16
        3: 4,  # Quarterfinals
        4: 2,  # Semifinals
        5: 1,  # Grand Final
    }
    round_labels = {
        1: "Round of 28",
        2: "Round of 16",
        3: "Quarterfinals",
        4: "Semifinals",
        5: "Grand Final",
    }
elif PLAYER_COUNT == 24:
    wiki_template = "Bracket/16L8DSSS"
    matches_per_round = {
        1: 8,  # Round of 24
        2: 8,  # Round of 16
        3: 4,  # Quarterfinals
        4: 2,  # Semifinals
        5: 1,  # Grand Final
    }
    round_labels = {
        1: "Round of 24",
        2: "Round of 16",
        3: "Quarterfinals",
        4: "Semifinals",
        5: "Grand Final",
    }
elif PLAYER_COUNT == 16:
    wiki_template = "Bracket/16"
    matches_per_round = {
        1: 8,  # Round of 16
        2: 4,  # Quarterfinals
        3: 2,  # Semifinals
        4: 1,  # Grand Final
    }
    round_labels = {
        1: "Round of 16",
        2: "Quarterfinals",
        3: "Semifinals",
        4: "Grand Final",
    }
else:
    # This ValueError is necessary for the settings to function correctly if PLAYER_COUNT is invalid.
    raise ValueError(
        f"Unsupported PLAYER_COUNT: {PLAYER_COUNT}. Please set to 16, 24, 28, 32, 64, 96, or 128."
    )
