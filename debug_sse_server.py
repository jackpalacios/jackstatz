#!/usr/bin/env python3
"""
Server-side SSE debugging script
Run this on your server to diagnose SSE issues
"""
import requests
import json
import time
import subprocess
import sys
import os

def check_flask_app():
    """Check if Flask app is running"""
    print("🔍 Checking Flask app...")
    try:
        response = requests.get('http://127.0.0.1:8000/', timeout=5)
        print(f"✅ Flask app running: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Flask app not accessible: {e}")
        return False

def check_sse_direct():
    """Test SSE directly to Flask (bypass Nginx)"""
    print("🔍 Testing SSE direct to Flask...")
    try:
        response = requests.get('http://127.0.0.1:8000/events', stream=True, timeout=10)
        print(f"✅ Direct SSE connection: {response.status_code}")
        
        count = 0
        for line in response.iter_lines():
            if line and count < 3:  # Only show first 3 messages
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    print(f"📡 Direct SSE: {line_str}")
                    count += 1
            elif count >= 3:
                break
        return True
    except Exception as e:
        print(f"❌ Direct SSE failed: {e}")
        return False

def check_sse_nginx():
    """Test SSE through Nginx"""
    print("🔍 Testing SSE through Nginx...")
    try:
        # Try both localhost and domain
        for url in ['http://localhost/events', 'http://127.0.0.1/events']:
            try:
                response = requests.get(url, stream=True, timeout=10)
                print(f"✅ Nginx SSE connection ({url}): {response.status_code}")
                
                count = 0
                for line in response.iter_lines():
                    if line and count < 3:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            print(f"📡 Nginx SSE: {line_str}")
                            count += 1
                    elif count >= 3:
                        break
                return True
            except Exception as e:
                print(f"❌ Nginx SSE failed ({url}): {e}")
        return False
    except Exception as e:
        print(f"❌ Nginx SSE failed: {e}")
        return False

def check_nginx_config():
    """Check Nginx configuration"""
    print("🔍 Checking Nginx configuration...")
    try:
        result = subprocess.run(['nginx', '-t'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Nginx config is valid")
        else:
            print(f"❌ Nginx config error: {result.stderr}")
        
        # Check if our site is enabled
        sites_enabled = '/etc/nginx/sites-enabled/'
        if os.path.exists(sites_enabled):
            sites = os.listdir(sites_enabled)
            print(f"📁 Enabled sites: {sites}")
        
    except Exception as e:
        print(f"❌ Cannot check Nginx config: {e}")

def check_processes():
    """Check running processes"""
    print("🔍 Checking processes...")
    try:
        # Check Flask processes
        result = subprocess.run(['pgrep', '-f', 'python.*app.py'], capture_output=True, text=True)
        if result.stdout.strip():
            print(f"✅ Flask processes: {result.stdout.strip()}")
        else:
            print("❌ No Flask processes found")
        
        # Check Nginx processes
        result = subprocess.run(['pgrep', 'nginx'], capture_output=True, text=True)
        if result.stdout.strip():
            print(f"✅ Nginx processes: {result.stdout.strip()}")
        else:
            print("❌ No Nginx processes found")
            
    except Exception as e:
        print(f"❌ Cannot check processes: {e}")

def check_ports():
    """Check what's listening on ports"""
    print("🔍 Checking ports...")
    try:
        # Check port 8000 (Flask)
        result = subprocess.run(['lsof', '-i', ':8000'], capture_output=True, text=True)
        if result.stdout.strip():
            print("✅ Port 8000 (Flask):")
            print(result.stdout)
        else:
            print("❌ Nothing listening on port 8000")
        
        # Check port 80 (Nginx)
        result = subprocess.run(['lsof', '-i', ':80'], capture_output=True, text=True)
        if result.stdout.strip():
            print("✅ Port 80 (Nginx):")
            print(result.stdout)
        else:
            print("❌ Nothing listening on port 80")
            
    except Exception as e:
        print(f"❌ Cannot check ports: {e}")

def test_stat_update():
    """Test making a stat update to trigger SSE"""
    print("🔍 Testing stat update...")
    try:
        response = requests.post('http://127.0.0.1:8000/update_player_stat', 
                               json={
                                   "team": "team1", 
                                   "player_index": 0, 
                                   "stat_type": "points_2", 
                                   "value": 99, 
                                   "game_id": "1"
                               }, timeout=5)
        print(f"✅ Stat update: {response.status_code} - {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Stat update failed: {e}")
        return False

def main():
    print("🏀 SSE Server Debugging Tool")
    print("=" * 50)
    
    # Run all checks
    flask_ok = check_flask_app()
    check_processes()
    check_ports()
    check_nginx_config()
    
    if flask_ok:
        sse_direct_ok = check_sse_direct()
        sse_nginx_ok = check_sse_nginx()
        test_stat_update()
        
        print("\n" + "=" * 50)
        print("📊 DIAGNOSIS:")
        
        if sse_direct_ok and sse_nginx_ok:
            print("✅ SSE is working correctly!")
        elif sse_direct_ok and not sse_nginx_ok:
            print("❌ SSE works direct but NOT through Nginx")
            print("🔧 Check your Nginx configuration for /events location")
        elif not sse_direct_ok:
            print("❌ SSE not working directly to Flask")
            print("🔧 Check your Flask app SSE implementation")
        else:
            print("❌ SSE not working at all")
    else:
        print("❌ Flask app is not running - start it first!")
    
    print("\n🔧 Next steps:")
    print("1. Make sure Flask app is running: python app.py")
    print("2. Check Nginx config has the /events location block")
    print("3. Restart Nginx: sudo systemctl restart nginx")
    print("4. Test in browser: open Developer Tools > Console")

if __name__ == "__main__":
    main()
