from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

app = Flask(__name__)

# Initialize Supabase client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase client initialized successfully")
except Exception as e:
    print(f"❌ Error initializing Supabase client: {e}")
    supabase = None

# In-memory storage for demo purposes (fallback if Supabase is not available)
# In a real app, you'd use a database
sports_buddies = [
    {
        "id": 1,
        "name": "Alex",
        "age": 12,
        "sport": "basketball",
        "location": "Central Park",
        "availability": "Weekends",
        "skill_level": "intermediate",
        "created_at": "2024-01-15"
    },
    {
        "id": 2,
        "name": "Sam",
        "age": 10,
        "sport": "soccer",
        "location": "Riverside Fields",
        "availability": "After school",
        "skill_level": "beginner",
        "created_at": "2024-01-14"
    },
    {
        "id": 3,
        "name": "Jordan",
        "age": 11,
        "sport": "tennis",
        "location": "Community Center",
        "availability": "Weekdays",
        "skill_level": "advanced",
        "created_at": "2024-01-13"
    }
]

# Basketball games storage
basketball_games = []

# Live game data storage (fallback if Supabase is not available)
default_live_game_data = {
    "team1": [
        {"jersey_number": 1, "position": "PG", "points_2": 0, "points_3": 0, "assists": 0, "rebounds": 0, "steals": 0},
        {"jersey_number": 2, "position": "SG", "points_2": 0, "points_3": 0, "assists": 0, "rebounds": 0, "steals": 0},
        {"jersey_number": 3, "position": "SF", "points_2": 0, "points_3": 0, "assists": 0, "rebounds": 0, "steals": 0},
        {"jersey_number": 4, "position": "PF", "points_2": 0, "points_3": 0, "assists": 0, "rebounds": 0, "steals": 0},
        {"jersey_number": 5, "position": "C", "points_2": 0, "points_3": 0, "assists": 0, "rebounds": 0, "steals": 0}
    ],
    "team2": [
        {"jersey_number": 6, "position": "PG", "points_2": 0, "points_3": 0, "assists": 0, "rebounds": 0, "steals": 0},
        {"jersey_number": 7, "position": "SG", "points_2": 0, "points_3": 0, "assists": 0, "rebounds": 0, "steals": 0},
        {"jersey_number": 8, "position": "SF", "points_2": 0, "points_3": 0, "assists": 0, "rebounds": 0, "steals": 0},
        {"jersey_number": 9, "position": "PF", "points_2": 0, "points_3": 0, "assists": 0, "rebounds": 0, "steals": 0},
        {"jersey_number": 10, "position": "C", "points_2": 0, "points_3": 0, "assists": 0, "rebounds": 0, "steals": 0}
    ]
}

def get_live_game_data():
    """Get live game data from Supabase or return default data"""
    if supabase is None:
        return default_live_game_data
    
    try:
        # Try to get the most recent live game
        response = supabase.table('live_games').select('*').order('created_at', desc=True).limit(1).execute()
        
        if response.data:
            game_data = response.data[0]
            return {
                "team1": game_data.get('team1_data', default_live_game_data['team1']),
                "team2": game_data.get('team2_data', default_live_game_data['team2']),
                "team1_name": game_data.get('team1_name', 'TEAM 1'),
                "team2_name": game_data.get('team2_name', 'TEAM 2'),
                "game_id": game_data.get('id')
            }
        else:
            # Create a new game if none exists
            return create_new_live_game()
    except Exception as e:
        print(f"Error fetching live game data: {e}")
        return default_live_game_data

def create_new_live_game():
    """Create a new live game in Supabase"""
    if supabase is None:
        return default_live_game_data
    
    try:
        new_game = {
            'team1_name': 'TEAM 1',
            'team2_name': 'TEAM 2',
            'team1_data': default_live_game_data['team1'],
            'team2_data': default_live_game_data['team2'],
            'status': 'active'
        }
        
        response = supabase.table('live_games').insert(new_game).execute()
        
        if response.data:
            game_data = response.data[0]
            return {
                "team1": game_data['team1_data'],
                "team2": game_data['team2_data'],
                "team1_name": game_data['team1_name'],
                "team2_name": game_data['team2_name'],
                "game_id": game_data['id']
            }
    except Exception as e:
        print(f"Error creating new live game: {e}")
    
    return default_live_game_data

def update_live_game_data(game_id, team, player_index, stat_type, value):
    """Update a specific stat in the live game"""
    if supabase is None:
        return False
    
    try:
        # Get current game data
        response = supabase.table('live_games').select('*').eq('id', game_id).execute()
        
        if response.data:
            game_data = response.data[0]
            team_data = game_data[f'{team}_data']
            
            # Update the specific stat
            team_data[player_index][stat_type] = value
            
            # Update the database
            update_data = {f'{team}_data': team_data}
            supabase.table('live_games').update(update_data).eq('id', game_id).execute()
            
            return True
    except Exception as e:
        print(f"Error updating live game data: {e}")
    
    return False

@app.route('/')
def index():
    return render_template('index.html', buddies=sports_buddies)

@app.route('/jack')
def jack():
    return render_template('jack.html')

@app.route('/live-game')
def live_game():
    game_data = get_live_game_data()
    return render_template('live_game.html', game_data=game_data)

@app.route('/update_player_stat', methods=['POST'])
def update_player_stat():
    data = request.json
    team = data['team']
    player_index = data['player_index']
    stat_type = data['stat_type']
    value = int(data['value'])
    game_id = data.get('game_id')
    
    # Update in Supabase if available
    if supabase is not None and game_id:
        update_success = update_live_game_data(game_id, team, player_index, stat_type, value)
        if not update_success:
            return jsonify({'success': False, 'error': 'Failed to update database'})
    
    # Get updated game data
    game_data = get_live_game_data()
    
    # Calculate totals for the updated player
    player = game_data[team][player_index]
    total_points = (player['points_2'] * 2) + (player['points_3'] * 3)
    
    return jsonify({
        'success': True,
        'total_points': total_points,
        'team_totals': calculate_team_totals_from_data(game_data)
    })

def calculate_team_totals():
    """Calculate team totals from current live game data"""
    game_data = get_live_game_data()
    return calculate_team_totals_from_data(game_data)

def calculate_team_totals_from_data(game_data):
    """Calculate team totals from provided game data"""
    team1_total = sum((player['points_2'] * 2) + (player['points_3'] * 3) for player in game_data['team1'])
    team2_total = sum((player['points_2'] * 2) + (player['points_3'] * 3) for player in game_data['team2'])
    return {'team1': team1_total, 'team2': team2_total}

@app.route('/add_game', methods=['POST'])
def add_game():
    data = request.form
    new_game = {
        "id": len(basketball_games) + 1,
        "date": data['date'],
        "opponent": data['opponent'],
        "result": data['result'],
        "points": int(data['points']),
        "rebounds": int(data['rebounds']),
        "assists": int(data['assists']),
        "steals": int(data['steals']),
        "blocks": int(data['blocks']),
        "turnovers": int(data['turnovers']),
        "minutes": int(data['minutes'])
    }
    basketball_games.append(new_game)
    
    # Calculate stats
    stats = calculate_stats(basketball_games)
    return render_template('stats_display.html', stats=stats, games=basketball_games)

def calculate_stats(games):
    if not games:
        return {
            'games_played': 0,
            'wins': 0,
            'win_percentage': 0,
            'avg_points': 0,
            'avg_rebounds': 0,
            'avg_assists': 0,
            'avg_steals': 0,
            'avg_blocks': 0
        }
    
    total_games = len(games)
    wins = sum(1 for game in games if game['result'] == 'win')
    win_percentage = (wins / total_games) * 100
    
    total_points = sum(game['points'] for game in games)
    total_rebounds = sum(game['rebounds'] for game in games)
    total_assists = sum(game['assists'] for game in games)
    total_steals = sum(game['steals'] for game in games)
    total_blocks = sum(game['blocks'] for game in games)
    
    return {
        'games_played': total_games,
        'wins': wins,
        'win_percentage': round(win_percentage, 1),
        'avg_points': round(total_points / total_games, 1),
        'avg_rebounds': round(total_rebounds / total_games, 1),
        'avg_assists': round(total_assists / total_games, 1),
        'avg_steals': round(total_steals / total_games, 1),
        'avg_blocks': round(total_blocks / total_games, 1)
    }

@app.route('/search')
def search():
    sport = request.args.get('sport', '').lower()
    location = request.args.get('location', '').lower()
    age_range = request.args.get('age_range', '')
    
    filtered_buddies = sports_buddies
    
    if sport:
        filtered_buddies = [b for b in filtered_buddies if sport in b['sport'].lower()]
    
    if location:
        filtered_buddies = [b for b in filtered_buddies if location in b['location'].lower()]
    
    if age_range:
        min_age, max_age = map(int, age_range.split('-'))
        filtered_buddies = [b for b in filtered_buddies if min_age <= b['age'] <= max_age]
    
    return render_template('buddy_list.html', buddies=filtered_buddies)

@app.route('/add_buddy', methods=['POST'])
def add_buddy():
    data = request.form
    new_buddy = {
        "id": len(sports_buddies) + 1,
        "name": data['name'],
        "age": int(data['age']),
        "sport": data['sport'],
        "location": data['location'],
        "availability": data['availability'],
        "skill_level": data['skill_level'],
        "created_at": datetime.now().strftime("%Y-%m-%d")
    }
    sports_buddies.append(new_buddy)
    return render_template('buddy_list.html', buddies=sports_buddies)

@app.route('/api/buddies')
def api_buddies():
    return jsonify(sports_buddies)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
