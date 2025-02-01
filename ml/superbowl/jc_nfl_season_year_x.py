import json
import csv

def parse_json_data(json_filename, csv_filename):
    with open(json_filename, 'r') as open_file:
        json_data = open_file.read()
        # Parse the JSON data
        data = json.loads(json_data)
        data = json.loads(data)
        
        # Extract the main season information
        year = data.get('year')
        start_date = data.get('startDate')
        end_date = data.get('endDate')
        display_name = data.get('displayName')
        
        # Extract the types of seasons
        season_types = data.get('types', {}).get('items', [])
        
        # Prepare data for CSV
        csv_data = []
        for season_type in season_types:
            csv_data.append({
                'Year': year,
                'Season Name': season_type.get('name'),
                'Abbreviation': season_type.get('abbreviation'),
                'Start Date': season_type.get('startDate'),
                'End Date': season_type.get('endDate'),
                'Has Groups': season_type.get('hasGroups'),
                'Has Standings': season_type.get('hasStandings'),
                'Slug': season_type.get('slug')
            })
        
        # Define CSV column headers
        csv_columns = ['Year', 'Season Name', 'Abbreviation', 'Start Date', 'End Date', 'Has Groups', 'Has Standings', 'Slug']
        
        # Write to CSV file
        try:
            with open(csv_filename, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                writer.writeheader()
                for row in csv_data:
                    writer.writerow(row)
            print(f"Data successfully written to {csv_filename}")
        except IOError:
            print("I/O error while writing to CSV")

# Example usage
json_data = """
{
    "year": 2019,
    "startDate": "2019-07-31T07:00Z",
    "endDate": "2020-02-06T07:59Z",
    "displayName": "2019",
    "type": {
        "id": "2",
        "type": 2,
        "name": "Regular Season",
        "abbreviation": "reg",
        "year": 2019,
        "startDate": "2019-09-05T07:00Z",
        "endDate": "2020-01-01T07:59Z",
        "hasGroups": false,
        "hasStandings": true,
        "hasLegs": false,
        "slug": "regular-season"
    },
    "types": {
        "count": 4,
        "pageIndex": 1,
        "pageSize": 4,
        "pageCount": 1,
        "items": [
            {
                "id": "1",
                "type": 1,
                "name": "Preseason",
                "abbreviation": "pre",
                "year": 2019,
                "startDate": "2019-07-31T07:00Z",
                "endDate": "2019-09-05T06:59Z",
                "hasGroups": false,
                "hasStandings": true,
                "hasLegs": false,
                "slug": "preseason"
            },
            {
                "id": "2",
                "type": 2,
                "name": "Regular Season",
                "abbreviation": "reg",
                "year": 2019,
                "startDate": "2019-09-05T07:00Z",
                "endDate": "2020-01-01T07:59Z",
                "hasGroups": false,
                "hasStandings": true,
                "hasLegs": false,
                "slug": "regular-season"
            },
            {
                "id": "3",
                "type": 3,
                "name": "Postseason",
                "abbreviation": "post",
                "year": 2019,
                "startDate": "2020-01-01T08:00Z",
                "endDate": "2020-02-06T07:59Z",
                "hasGroups": false,
                "hasStandings": false,
                "hasLegs": false,
                "slug": "post-season"
            },
            {
                "id": "4",
                "type": 4,
                "name": "Off Season",
                "abbreviation": "off",
                "year": 2019,
                "startDate": "2020-02-06T08:00Z",
                "endDate": "2020-08-05T06:59Z",
                "hasGroups": false,
                "hasStandings": false,
                "hasLegs": false,
                "slug": "off-season"
            }
        ]
    }
}
"""

# extract_nfl_data_to_csv(json_data, 'nfl_season_2019.csv')