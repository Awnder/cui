import json
import pandas as pd

# created with chatgpt and corrected

def json_to_dataframe(json_input_path: str) -> pd.DataFrame:
    with open(json_input_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue  # Skip empty lines
            try:
                data = json.loads(line) # for whatever reason, this returns a string
                data = json.loads(data) # so I need to decode it again into a dict
            except json.JSONDecodeError as e:
                print(f"Skipping a line due to JSON error: {e}")
                continue
            
    # Extracting team information
    teams_data = []
    for entry in data:
        team = entry.get("team", {})
        teams_data.append({
            "id": team.get("id"),
            "uid": team.get("uid"),
            "slug": team.get("slug"),
            "abbreviation": team.get("abbreviation"),
            "displayName": team.get("displayName"),
            "shortDisplayName": team.get("shortDisplayName"),
            "name": team.get("name"),
            "nickname": team.get("nickname"),
            "location": team.get("location"),
            "color": team.get("color"),
            "alternateColor": team.get("alternateColor"),
            "isActive": team.get("isActive"),
            "isAllStar": team.get("isAllStar"),
            "primaryLogo": team.get("logos", [{}])[0].get("href", "")  # First logo
        })
    
    return pd.DataFrame(teams_data)
