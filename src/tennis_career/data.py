import json
import re
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
import pandas as pd

url = "https://www.tennisabstract.com"

def _validate_name(player_name):
    if not isinstance(player_name, str) or not player_name.strip():
        raise ValueError("Provide a nonempty player name such as 'Serena Williams'.")
    name = player_name.strip()
    if not re.fullmatch(r"[A-Za-z\s.'-]+", name) or not re.search(r"[A-Za-z]", name):
        raise ValueError("Use letters, spaces, periods, apostrophes, or hyphens in player names.")
    return name

def _format_player_name(player_name):
    words = _validate_name(player_name).split()
    if len(words) == 1 and words[0].islower():
        raise ValueError("Use spaces ('serena williams') or a capitalized joined name ('SerenaWilliams').")
    name = words[0]
    if len(words) > 1:
        name = ""
        for word in words:
            name += word.title()
    return re.sub(r"[^A-Za-z]", "", name)

def _fetch_text(path):
    request = Request(url + path, headers={"User-Agent": "tennis-career/0.1"})
    try:
        with urlopen(request, timeout=30) as response:
            return response.read().decode("utf-8-sig")
    except HTTPError as error:
        if error.code == 404:
            raise ValueError("Player data not found please check the Tennis Abstract spelling.") from error
        raise ConnectionError(f"Tennis Abstract returned HTTP {error.code}.") from error
    except (URLError, TimeoutError) as error:
        raise ConnectionError("Unable to reach Tennis Abstract please try again later.") from error

def _read_metadata(text, name):
    match = re.search(r"\bvar\s+" + name + r"\s*=\s*([^;]+);", text)
    if match is None:
        raise ValueError(f"Tennis Abstract data is missing {name!r}.")
    return match.group(1).strip().strip("\"'")

def _validate_matches(rows):
    if not isinstance(rows, list):
        raise ValueError("The match array must be a list.")
    for row in rows:
        if not isinstance(row, list) or len(row) < 17:
            raise ValueError("Each match must be an array with at least 17 fields.")

def _parse_matches(text, variable="morematchmx"):
    match = re.search(r"\bvar\s+" + variable + r"\s*=\s*", text)
    if match is None:
        raise ValueError(f"Tennis Abstract data is missing the {variable!r} match array.")
    try:
        rows, _ = json.JSONDecoder().raw_decode(text[match.end():])
    except json.JSONDecodeError as error:
        raise ValueError("The Tennis Abstract match array is not valid JSON.") from error
    _validate_matches(rows)
    return rows

def _match_frame(matches):
    rows = []
    for match in matches:
        rows.append({
            "match_date": match[0], "tournament": match[1],
            "surface": match[2], "result": match[4],
            "round": match[8], "match_score_sets": match[9],
            "opponent_name": match[11], "opponent_age": match[16],
        })
    return pd.DataFrame(rows)

def _opponent_age(value, match_date):
    value = str(value)
    if len(value) == 8 and value.isdigit():
        birthday = pd.to_datetime(value, format="%Y%m%d", errors="coerce")
        return (match_date - birthday).days / 365.25
    return pd.to_numeric(value, errors="coerce")

def _add_ages(frame, player_dob):
    ages = []
    for value, date in zip(frame["opponent_age"], frame["match_date"]):
        ages.append(_opponent_age(value, date))
    frame["opponent_age"] = ages
    frame["player_age"] = (frame["match_date"] - player_dob).dt.days / 365.25
    frame["age_difference"] = frame["player_age"] - frame["opponent_age"]
    return frame

def _filter_matches(frame):
    frame = frame[frame["result"].isin(["W", "L"])]
    frame = frame[frame["player_age"].between(0, 100)]
    frame = frame[frame["opponent_age"].between(0, 100)]
    frame = frame.drop_duplicates().sort_values("match_date", kind="stable") # for matches with the same date
    return frame.reset_index(drop=True)

def _clean_matches(matches, player_name, player_dob):
    if not matches:
        return pd.DataFrame()
    frame = _match_frame(matches)
    frame["match_date"] = pd.to_datetime(frame["match_date"], format="%Y%m%d", errors="coerce")
    frame = _add_ages(frame, player_dob)
    frame["player_name"] = player_name
    return _filter_matches(frame)

def _matches_player(text, formatted_name):
    try:
        return _format_player_name(_read_metadata(text, "fullname")).lower() == formatted_name.lower()
    except ValueError:
        return False

def _load_player(formatted_name):
    # try from the TA player page directly, as I discovered Nadal's JS is missing many rows from recent years
    text = _fetch_text(f"/cgi-bin/player-classic.cgi?p={quote(formatted_name)}")
    if not _matches_player(text, formatted_name):
        text = _fetch_text(f"/jsmatches/{quote(formatted_name)}.js")
    if not _matches_player(text, formatted_name):
        raise ValueError(f"Player {formatted_name!r} not found please check the Tennis Abstract spelling.")
    return text

def get_career_data(player_name):
    """Return clean career matches for a spaced or joined player name on Tennis Abstract."""
    formatted_name = _format_player_name(player_name)
    text = _load_player(formatted_name)
    full_name = _read_metadata(text, "fullname")
    birthday = pd.to_datetime(_read_metadata(text, "dob"), format="%Y%m%d", errors="coerce")
    if pd.isna(birthday):
        raise ValueError(f"No valid date of birth is available for {player_name!r}.")
    rows = _parse_matches(text, "matchmx")
    if _read_metadata(text, "careerjs") == "1":
        career = _fetch_text(f"/jsmatches/{quote(formatted_name)}Career.js")
        rows += _parse_matches(career)
    frame = _clean_matches(rows, full_name, birthday)
    if frame.empty:
        raise ValueError(f"No plottable career matches found for {player_name!r}.")
    return frame