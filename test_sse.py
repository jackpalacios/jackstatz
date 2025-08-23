#!/usr/bin/env python3
"""
Simple script to test SSE functionality
"""
import requests
import json
import time
import threading

def test_sse_connection():
    """Test SSE connection and listen for events"""
    print("🔌 Connecting to SSE endpoint...")
    try:
        response = requests.get('http://localhost:8000/events', stream=True, timeout=60)
        print(f"✅ Connected! Status: {response.status_code}")
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_str = line_str[6:]  # Remove 'data: ' prefix
                    try:
                        data = json.loads(data_str)
                        print(f"📡 Received: {data}")
                    except json.JSONDecodeError:
                        print(f"📡 Raw data: {data_str}")
                        
    except Exception as e:
        print(f"❌ SSE Error: {e}")

def make_stat_update():
    """Make a stat update to trigger SSE broadcast"""
    time.sleep(3)  # Wait for SSE connection to establish
    print("📊 Making stat update...")
    
    try:
        response = requests.post('http://localhost:8000/update_player_stat', 
                               json={
                                   "team": "team1", 
                                   "player_index": 0, 
                                   "stat_type": "points_2", 
                                   "value": 8, 
                                   "game_id": "1"
                               })
        print(f"✅ Stat update response: {response.json()}")
    except Exception as e:
        print(f"❌ Stat update error: {e}")

if __name__ == "__main__":
    print("🏀 Testing SSE functionality for JackStatz")
    
    # Start SSE listener in background
    sse_thread = threading.Thread(target=test_sse_connection, daemon=True)
    sse_thread.start()
    
    # Make a stat update after a delay
    update_thread = threading.Thread(target=make_stat_update, daemon=True)
    update_thread.start()
    
    # Keep main thread alive
    try:
        time.sleep(10)
        print("🏁 Test completed")
    except KeyboardInterrupt:
        print("🛑 Test interrupted")
