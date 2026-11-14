import json
from pathlib import Path
from urllib.error import HTTPError
import pandas as pd
import pytest

from tennis_career import data, get_career_data

_fixtures = Path(__file__).parent / "fixtures"

def _fixture(filename):
    return (_fixtures / filename).read_text()

def test_female_matches():
    matches = data._parse_matches(_fixture("FemalePlayerCareer.js"))
    frame = data._clean_matches(matches, "Serena Williams", pd.Timestamp("1981-09-26"))
    first = frame.iloc[0]
    date = pd.Timestamp("1995-10-30")
    expected_age = (date - pd.Timestamp("1977-01-19")).days / 365.25
    expected_player_age = (date - pd.Timestamp("1981-09-26")).days / 365.25
    assert len(frame) == 3
    assert first["opponent_name"] == "Anne Miller"
    assert first["match_date"] == date
    assert first["opponent_age"] == pytest.approx(expected_age)
    assert first["player_age"] == pytest.approx(expected_player_age)
    assert first["age_difference"] == pytest.approx(expected_player_age - expected_age)
    assert first["result"] == "L"

def test_male_matches():
    matches = data._parse_matches(_fixture("MalePlayerCareer.js"))
    frame = data._clean_matches(matches, "Rafael Nadal", pd.Timestamp("1986-06-03"))
    expected_ages = [22.264202601, 24.2902121834, 18.7597535934]
    first = frame.iloc[0]
    expected_player_age = (pd.Timestamp("2001-09-10") - pd.Timestamp("1986-06-03")).days / 365.25
    assert len(frame) == 3
    assert frame["opponent_age"].tolist() == pytest.approx(expected_ages)
    assert first["player_age"] == pytest.approx(expected_player_age)
    assert first["age_difference"] == pytest.approx(expected_player_age - expected_ages[0])
    assert frame["result"].tolist() == ["L", "L", "W"]
    assert frame["match_date"].is_monotonic_increasing

def test_player_name_formats():
    names = ["serena williams", "Serena Williams", "SerenaWilliams"]
    for name in names:
        assert data._format_player_name(name) == "SerenaWilliams"

def test_invalid_array():
    with pytest.raises(ValueError):
        data._parse_matches("This text has no match array.")

def test_missing_age_and_duplicates():
    matches = data._parse_matches(_fixture("FemalePlayerCareer.js"))
    missing_age = matches[0].copy()
    missing_age[16] = ""
    matches = matches + matches + [missing_age]
    frame = data._clean_matches(matches, "Serena Williams", pd.Timestamp("1981-09-26"))
    assert len(frame) == 3
    assert not frame["opponent_age"].isna().any()

def _current_matches():
    row = [""] * 17
    row[0] = "20000101"
    row[4] = "W"
    row[11] = "Example Opponent"
    row[16] = "19780101"
    return "var matchmx=" + json.dumps([row]) + ";"

def _fake_fetch_text(path):
    if path == "/cgi-bin/player-classic.cgi?p=SerenaWilliams":
        return "<html>No matching profile</html>"
    if path == "/jsmatches/SerenaWilliamsCareer.js":
        return _fixture("FemalePlayerCareer.js")
    if path == "/jsmatches/SerenaWilliams.js":
        metadata = "var fullname='Serena Williams'; var dob=19810926; var careerjs=1;"
        return metadata + _current_matches()
    raise AssertionError(f"Unexpected fetch path: {path}")

def test_get_career_data(monkeypatch):
    monkeypatch.setattr(data, "_fetch_text", _fake_fetch_text)
    frame = get_career_data("serena williams")
    assert len(frame) == 4
    assert frame["player_name"].tolist() == ["Serena Williams"] * 4
    assert frame["opponent_name"].tolist() == [
        "Anne Miller", "Alexia Dechaume Balleret", "Magui Serna", "Example Opponent"
    ]
    assert frame["match_date"].iloc[-1] == pd.Timestamp("2000-01-01")
    assert "age_difference" in frame.columns

def _not_found(*args, **kwargs):
    raise HTTPError("https://example.invalid", 404, "Not found", {}, None)

def test_unknown_player(monkeypatch):
    monkeypatch.setattr(data, "urlopen", _not_found)
    with pytest.raises(ValueError, match="Player data not found"):
        get_career_data("GastonSanchez")

def test_wrong_player_identity():
    text = "var fullname='Rafael Nadal';"
    assert not data._matches_player(text, "SerenaWilliams")

def test_formatted_names_and_periods():
    assert data._format_player_name("John McEnroe") == "JohnMcenroe"
    assert data._format_player_name("JohnMcenroe") == "JohnMcenroe"
    assert data._format_player_name("JohnMcEnroe") == "JohnMcEnroe"

def test_invalid_names():
    for name in ["", "   ", None, "Serena123", "../", "..."]:
        with pytest.raises(ValueError):
            get_career_data(name)

def test_lowercase_joined_name():
    with pytest.raises(ValueError, match="Use spaces"):
        get_career_data("serenawilliams")

def _server_error(*args, **kwargs):
    raise HTTPError("https://example.invalid", 503, "Unavailable", {}, None)

def test_server_error(monkeypatch):
    monkeypatch.setattr(data, "urlopen", _server_error)
    with pytest.raises(ConnectionError, match="503"):
        get_career_data("Serena Williams")

def test_complete_profile(monkeypatch):
    matches = _fixture("MalePlayerCareer.js").replace("morematchmx", "matchmx")
    profile = "var fullname='Rafael Nadal'; var dob=19860603; var careerjs=0;"
    requested_paths = []
    def fake_fetch_text(path):
        requested_paths.append(path)
        return profile + matches
    monkeypatch.setattr(data, "_fetch_text", fake_fetch_text)
    frame = get_career_data("Rafael Nadal")
    assert len(frame) == 3
    assert requested_paths == ["/cgi-bin/player-classic.cgi?p=RafaelNadal"]

def test_invalid_player_birthday(monkeypatch):
    profile = "var fullname='Serena Williams'; var dob=invalid;"
    monkeypatch.setattr(data, "_fetch_text", lambda path: profile)
    with pytest.raises(ValueError, match="date of birth"):
        get_career_data("Serena Williams")

def test_non_json_and_invalid_rows():
    for text in ["var morematchmx=[bad];", "var morematchmx={};", "var morematchmx=[[1]];"]:
        with pytest.raises(ValueError):
            data._parse_matches(text)

def test_three_word_name():
    assert data._format_player_name("Alexia Dechaume Balleret") == "AlexiaDechaumeBalleret"
    assert data._format_player_name("alexia dechaume balleret") == "AlexiaDechaumeBalleret"