from flask import Flask, render_template, request, jsonify, Response
import json
import time
import threading
from datetime import datetime
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

app = Flask(__name__)

# Global variable to store connected SSE clients
sse_clients = []

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
        {"jersey_number": 1, "name": "", "position": "PG", "points_2": 0, "points_3": 0, "assists": 0, "rebounds": 0, "steals": 0},
        {"jersey_number": 2, "name": "", "position": "SG", "points_2": 0, "points_3": 0, "assists": 0, "rebounds": 0, "steals": 0},
        {"jersey_number": 3, "name": "", "position": "SF", "points_2": 0, "points_3": 0, "assists": 0, "rebounds": 0, "steals": 0},
        {"jersey_number": 4, "name": "", "position": "PF", "points_2": 0, "points_3": 0, "assists": 0, "rebounds": 0, "steals": 0},
        {"jersey_number": 5, "name": "", "position": "C", "points_2": 0, "points_3": 0, "assists": 0, "rebounds": 0, "steals": 0}
    ],
    "team2": [
        {"jersey_number": 6, "name": "", "position": "PG", "points_2": 0, "points_3": 0, "assists": 0, "rebounds": 0, "steals": 0},
        {"jersey_number": 7, "name": "", "position": "SG", "points_2": 0, "points_3": 0, "assists": 0, "rebounds": 0, "steals": 0},
        {"jersey_number": 8, "name": "", "position": "SF", "points_2": 0, "points_3": 0, "assists": 0, "rebounds": 0, "steals": 0},
        {"jersey_number": 9, "name": "", "position": "PF", "points_2": 0, "points_3": 0, "assists": 0, "rebounds": 0, "steals": 0},
        {"jersey_number": 10, "name": "", "position": "C", "points_2": 0, "points_3": 0, "assists": 0, "rebounds": 0, "steals": 0}
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
    games = get_all_games()
    return render_template('index.html', games=games)

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
    
    # Broadcast the update to all connected clients
    broadcast_update('stat_update', {
        'team': team,
        'player_index': player_index,
        'stat_type': stat_type,
        'value': value,
        'total_points': total_points,
        'team_totals': calculate_team_totals_from_data(game_data)
    })
    
    return jsonify({
        'success': True,
        'total_points': total_points,
        'team_totals': calculate_team_totals_from_data(game_data)
    })

@app.route('/update_team_name', methods=['POST'])
def update_team_name():
    data = request.json
    team = data['team']  # 'team1' or 'team2'
    new_name = data['name']
    game_id = data.get('game_id')
    
    # Update in Supabase if available
    if supabase is not None and game_id:
        try:
            # Update the team name in the database
            update_data = {f'{team}_name': new_name}
            supabase.table('live_games').update(update_data).eq('id', game_id).execute()
            
            # Broadcast the update to all connected clients
            broadcast_update('team_name_update', {
                'team': team,
                'name': new_name
            })
            
            return jsonify({'success': True, 'message': 'Team name updated successfully'})
        except Exception as e:
            print(f"Error updating team name: {e}")
            return jsonify({'success': False, 'error': 'Failed to update team name in database'})
    
    return jsonify({'success': False, 'error': 'No database connection or game ID'})

@app.route('/update_player_name', methods=['POST'])
def update_player_name():
    data = request.json
    team = data['team']  # 'team1' or 'team2'
    player_index = data['player_index']
    new_name = data['name']
    game_id = data.get('game_id')
    
    # Update in Supabase if available
    if supabase is not None and game_id:
        try:
            # Get current game data
            response = supabase.table('live_games').select('*').eq('id', game_id).execute()
            
            if response.data:
                game_data = response.data[0]
                team_data = game_data[f'{team}_data']
                
                # Update the player name
                if player_index < len(team_data):
                    team_data[player_index]['name'] = new_name
                    
                    # Update the database
                    update_data = {f'{team}_data': team_data}
                    supabase.table('live_games').update(update_data).eq('id', game_id).execute()
                    
                    # Broadcast the update to all connected clients
                    broadcast_update('player_name_update', {
                        'team': team,
                        'player_index': player_index,
                        'name': new_name
                    })
                    
                    return jsonify({'success': True, 'message': 'Player name updated successfully'})
                else:
                    return jsonify({'success': False, 'error': 'Invalid player index'})
            else:
                return jsonify({'success': False, 'error': 'Game not found'})
        except Exception as e:
            print(f"Error updating player name: {e}")
            return jsonify({'success': False, 'error': 'Failed to update player name in database'})
    
    return jsonify({'success': False, 'error': 'No database connection or game ID'})

def broadcast_update(event_type, data):
    """Broadcast updates to all connected SSE clients"""
    message = json.dumps({
        'type': event_type,
        'data': data,
        'timestamp': datetime.now().isoformat()
    })
    
    # Remove disconnected clients
    global sse_clients
    active_clients = []
    
    for client in sse_clients:
        try:
            client.put(f"data: {message}\n\n", block=False)
            active_clients.append(client)
        except:
            # Client disconnected, remove from list
            pass
    
    sse_clients = active_clients
    print(f"📡 Broadcasted {event_type} to {len(active_clients)} clients")

@app.route('/events')
def events():
    """SSE endpoint for live updates"""
    def event_stream():
        import queue
        client_queue = queue.Queue()
        sse_clients.append(client_queue)
        print(f"🔌 New SSE client connected. Total clients: {len(sse_clients)}")
        
        try:
            # Send initial connection message
            yield "data: {\"type\": \"connected\", \"message\": \"SSE connection established\"}\n\n"
            
            while True:
                try:
                    # Wait for updates with timeout
                    message = client_queue.get(timeout=30)
                    yield message
                except queue.Empty:
                    # Send heartbeat to keep connection alive
                    yield "data: {\"type\": \"heartbeat\"}\n\n"
        except GeneratorExit:
            # Client disconnected
            if client_queue in sse_clients:
                sse_clients.remove(client_queue)
            print(f"🔌 SSE client disconnected. Remaining clients: {len(sse_clients)}")
    
    return Response(event_stream(), mimetype='text/event-stream',
                   headers={'Cache-Control': 'no-cache',
                           'Connection': 'keep-alive',
                           'Access-Control-Allow-Origin': '*',
                           'X-Accel-Buffering': 'no'})

def get_all_games():
    """Get all games from the database"""
    if supabase is None:
        return []
    
    try:
        # Get all live games
        live_games_response = supabase.table('live_games').select('*').order('created_at', desc=True).execute()
        
        # Get all completed basketball games
        basketball_games_response = supabase.table('basketball_games').select('*').order('created_at', desc=True).execute()
        
        games = []
        
        # Add live games
        for game in live_games_response.data:
            # Calculate total scores
            team1_score = sum((player.get('points_2', 0) * 2) + (player.get('points_3', 0) * 3) for player in game.get('team1_data', []))
            team2_score = sum((player.get('points_2', 0) * 2) + (player.get('points_3', 0) * 3) for player in game.get('team2_data', []))
            
            games.append({
                'id': game['id'],
                'type': 'live',
                'date': game['created_at'][:10],  # Extract date part
                'team1_name': game.get('team1_name', 'TEAM 1'),
                'team2_name': game.get('team2_name', 'TEAM 2'),
                'team1_score': team1_score,
                'team2_score': team2_score,
                'status': game.get('status', 'active')
            })
        
        # Add completed basketball games
        for game in basketball_games_response.data:
            games.append({
                'id': game['id'],
                'type': 'completed',
                'date': game['date'],
                'opponent': game['opponent'],
                'team_score': game['team_score'],
                'opponent_score': game['opponent_score'],
                'result': game['result'],
                'points': game['points'],
                'rebounds': game['rebounds'],
                'assists': game['assists']
            })
        
        return games
    except Exception as e:
        print(f"Error fetching games: {e}")
        return []

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
