import pytest

from plaix.sports.cricket.features import (
    CricketFeatureExtractionInput,
    CricketFeatureExtractor,
    MatchContextFeatures,
    PlayerFeatures,
    TeamFeatures,
    VenueWeatherFeatures,
)


def _build_input() -> CricketFeatureExtractionInput:
    return CricketFeatureExtractionInput(
        payload={},
        match_context=MatchContextFeatures(match_id="M1", tournament="Demo"),
        teams=TeamFeatures(batting_team="A", bowling_team="B"),
        players=PlayerFeatures(key_batters=["p1"], key_bowlers=["p2"]),
        venue_weather=VenueWeatherFeatures(venue="V1"),
        recent_matches=[],
    )


def test_feature_extractor_structure() -> None:
    extractor = CricketFeatureExtractor()
    payload = _build_input()

    output = extractor.extract(payload)

    assert output.sport == "cricket"
    assert output.match_id == "M1"
    assert "match_context" in output.features
    assert "teams" in output.features
    assert "players" in output.features
    assert "venue_weather" in output.features


def test_feature_extractor_handles_missing_optional_fields() -> None:
    extractor = CricketFeatureExtractor()
    payload = _build_input()
    payload.match_context.tournament = None

    output = extractor.extract(payload)

    assert output.features["match_context"].get("tournament") is None


def test_feature_extractor_accepts_extra_fields() -> None:
    extractor = CricketFeatureExtractor()
    payload = _build_input()
    payload.players.top_batter_form = {"p1": 0.8}

    output = extractor.extract(payload)

    assert output.features["players"]["top_batter_form"]["p1"] == 0.8
