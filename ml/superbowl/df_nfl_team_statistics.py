import json
import pandas as pd

# created using chatgpt - modified to fit use case

def json_to_dataframe(json_input_path):
    """
    Reads a JSON file containing NFL statistics, extracts important features and their associated values,
    and returns a pandas DataFrame.

    The JSON data is expected to have a nested structure like:
      {
          "statistics": {
              "splits": {
                  "id": "0",
                  "name": "All Splits",
                  "abbreviation": "Any",
                  "categories": [
                      {
                          "name": "general",
                          "displayName": "General",
                          "stats": [
                              {
                                  "name": "fumbles",
                                  "displayName": "Fumbles",
                                  "abbreviation": "FUM",
                                  "value": 21,
                                  "displayValue": "21",
                                  "perGameValue": 1,
                                  "perGameDisplayValue": "1",
                                  "rank": 14,
                                  "rankDisplayValue": "Tied-14th"
                              },
                              ...
                          ]
                      },
                      {
                          "name": "passing",
                          "displayName": "Passing",
                          "stats": [
                              {
                                  "name": "completionPct",
                                  "displayName": "Completion Percentage",
                                  "abbreviation": "CMP%",
                                  "value": 63.964,
                                  "displayValue": "64.0",
                                  "perGameValue": 64.285,
                                  "perGameDisplayValue": "64.285",
                                  "rank": 20,
                                  "rankDisplayValue": "20th"
                              },
                              ...
                          ]
                      }
                  ]
              }
          }
      }

    Each row in the resulting DataFrame represents a single stat entry with its associated split and category context.
    """
    rows = []
    
    # Open and process the JSON file line by line (this approach works well for large files).
    with open(json_input_path, 'r', encoding='utf-8') as infile:
        for line in infile:
            line = line.strip()
            if not line:
                continue  # Skip empty lines
            try:
                data = json.loads(line) # for whatever reason, this returns a string
                data = json.loads(data) # so I need to decode it again into a dict
            except json.JSONDecodeError as e:
                print(f"Skipping a line due to JSON error: {e}")
                continue

            # Navigate the JSON structure
            statistics = data.get("statistics", {})
            splits = statistics.get("splits", {})
            split_id = splits.get("id", "")
            split_name = splits.get("name", "")
            split_abbreviation = splits.get("abbreviation", "")
            
            categories = splits.get("categories", [])
            for cat in categories:
                category_name = cat.get("name", "")
                category_displayName = cat.get("displayName", "")
                
                # Iterate over each stat entry in the category
                for stat in cat.get("stats", []):
                    row = {
                        "split_id": split_id,
                        "split_name": split_name,
                        "split_abbreviation": split_abbreviation,
                        "category_name": category_name,
                        "category_displayName": category_displayName,
                        "stat_name": stat.get("name", ""),
                        "stat_displayName": stat.get("displayName", ""),
                        "stat_abbreviation": stat.get("abbreviation", ""),
                        "stat_value": stat.get("value", None),
                        "stat_displayValue": stat.get("displayValue", None),
                        "stat_perGameValue": stat.get("perGameValue", None),
                        "stat_perGameDisplayValue": stat.get("perGameDisplayValue", None),
                        "stat_rank": stat.get("rank", None),
                        "stat_rankDisplayValue": stat.get("rankDisplayValue", None)
                    }
                    rows.append(row)
    
    # Create a DataFrame from the list of rows
    df = pd.DataFrame(rows)
    return df