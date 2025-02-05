import json
import csv

# created using chatgpt - modified to fit use case

def parse_json_data(json_input_path, csv_output_path):
    """
    Reads a file containing JSON objects with NFL statistics, extracts important features,
    and writes the flattened information into a CSV file.

    The expected JSON structure is:
      {
          "statistics": {
              "splits": {
                  "id": "...",
                  "name": "...",
                  "abbreviation": "...",
                  "categories": [
                      {
                          "name": "general",
                          "displayName": "General",
                          "stats": [
                              {
                                  "name": "fumbles",
                                  "displayName": "Fumbles",
                                  "description": "The number of times a player/team has fumbled the ball",
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
                                  "name": "avgGain",
                                  "displayName": "Average Gain",
                                  "description": "The average gained yards per position.",
                                  "abbreviation": "AG",
                                  "value": 536.94,
                                  "displayValue": "536.9",
                                  "rank": 18,
                                  "rankDisplayValue": "18th"
                              },
                              ...
                          ]
                      }
                  ]
              }
          }
      }

    Each row in the CSV will include the split information, category, and individual stat details.
    """
    # Define the CSV header (feel free to modify the fields if you need more or less detail)
    header = [
        "split_id", "split_name", "split_abbreviation",
        "category_name", "category_displayName",
        "stat_name", "stat_displayName", "stat_abbreviation",
        "stat_value", "stat_displayValue",
        "stat_perGameValue", "stat_perGameDisplayValue",
        "stat_rank", "stat_rankDisplayValue"
    ]
    
    # Open the CSV file for writing
    with open(csv_output_path, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=header)
        writer.writeheader()
        
        # Process the input JSON file
        # Here, we assume that the input file may have one JSON object per line.
        with open(json_input_path, mode='r', encoding='utf-8') as infile:
            for line in infile:
                line = line.strip()
                if not line:
                    continue  # skip blank lines
                try:
                    data = json.loads(line) # for whatever reason, this returns a string
                    data = json.loads(data) # so we need to load the data again as a dict
                except json.JSONDecodeError as e:
                    print(f"Skipping a line due to JSON error: {e}")
                    continue

                statistics = data.get("statistics", {})
                splits = statistics.get("splits", {})
                # Get split-level metadata
                split_id = splits.get("id", "")
                split_name = splits.get("name", "")
                split_abbreviation = splits.get("abbreviation", "")
                
                # Get each category (e.g., "general", "passing")
                categories = splits.get("categories", [])
                for cat in categories:
                    category_name = cat.get("name", "")
                    category_displayName = cat.get("displayName", "")
                    
                    # Get each stat entry within the category
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
                            "stat_value": stat.get("value", ""),
                            "stat_displayValue": stat.get("displayValue", ""),
                            "stat_perGameValue": stat.get("perGameValue", ""),
                            "stat_perGameDisplayValue": stat.get("perGameDisplayValue", ""),
                            "stat_rank": stat.get("rank", ""),
                            "stat_rankDisplayValue": stat.get("rankDisplayValue", "")
                        }
                        writer.writerow(row)

# Example usage:
# extract_nfl_stats('nfl_stats.json', 'nfl_stats.csv')
