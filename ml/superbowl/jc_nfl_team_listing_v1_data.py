import json
import csv

def parse_json_data(json_filename, csv_filename):
    with open(json_filename, 'r') as open_file:
        json_data = open_file.read()
        # Load the JSON data
        data = json.loads(json_data)
        data = json.loads(data)

        # Open a CSV file for writing
        with open(csv_filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            
            # Write the header
            writer.writerow([
                'Team ID', 'Team Name', 'Abbreviation', 'Location', 
                'Color', 'Alternate Color', 'Is Active', 'Default Logo URL', 'Clubhouse URL'
            ])
            
            # Iterate over each team in the JSON data
            for item in data:
                team = item['team']
                
                # Extract the required information
                team_id = team['id']
                team_name = team['displayName']
                abbreviation = team['abbreviation']
                location = team['location']
                color = team['color']
                alternate_color = team['alternateColor']
                is_active = team['isActive']
                
                # Extract the default logo URL
                default_logo_url = next((logo['href'] for logo in team['logos'] if 'default' in logo['rel']), None)
                
                # Extract the Clubhouse URL
                clubhouse_url = next((link['href'] for link in team['links'] if 'clubhouse' in link['rel']), None)
                
                # Write the row to the CSV file
                writer.writerow([
                    team_id, team_name, abbreviation, location, 
                    color, alternate_color, is_active, default_logo_url, clubhouse_url
                ])

# Example usage
# json_data = '''[{"team": {"id": "22", "uid": "s:20~l:28~t:22", "slug": "arizona-cardinals", "abbreviation": "ARI", "displayName": "Arizona Cardinals", "shortDisplayName": "Cardinals", "name": "Cardinals", "nickname": "Cardinals", "location": "Arizona", "color": "a40227", "alternateColor": "ffffff", "isActive": true, "isAllStar": false, "logos": [{"href": "https://a.espncdn.com/i/teamlogos/nfl/500/ari.png", "alt": "", "rel": ["full", "default"], "width": 500, "height": 500}], "links": [{"language": "en-US", "rel": ["clubhouse", "desktop", "team"], "href": "https://www.espn.com/nfl/team/_/name/ari/arizona-cardinals", "text": "Clubhouse", "shortText": "Clubhouse", "isExternal": false, "isPremium": false, "isHidden": false}]}}]'''
# csv_filename = 'nfl_teams.csv'
# extract_nfl_data_to_csv(json_data, csv_filename)
