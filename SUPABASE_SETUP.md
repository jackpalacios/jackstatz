# Supabase Setup Guide

This guide will help you set up Supabase to persist your basketball stats data.

## 1. Create a Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign up/login
2. Click "New Project"
3. Choose your organization
4. Enter project details:
   - **Name**: `jackhacks-basketball` (or your preferred name)
   - **Database Password**: Choose a strong password
   - **Region**: Choose closest to you
5. Click "Create new project"

## 2. Get Your Project Credentials

1. In your Supabase dashboard, go to **Settings** → **API**
2. Copy the following values:
   - **Project URL** (looks like: `https://your-project.supabase.co`)
   - **anon public** key (starts with `eyJ...`)

## 3. Configure Your App

### Option A: Using Environment Variables (Recommended)

1. Create a `.env` file in your project root:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
```

2. Make sure `.env` is in your `.gitignore` file

### Option B: Direct Configuration

1. Edit `config.py` and replace the placeholder values:
```python
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key-here"
```

## 4. Set Up Database Schema

1. In your Supabase dashboard, go to **SQL Editor**
2. Copy the contents of `supabase_schema.sql`
3. Paste and run the SQL commands
4. This will create all necessary tables and policies

## 5. Install Dependencies

```bash
pip3 install -r requirements.txt
```

## 6. Test the Integration

1. Start your Flask app:
```bash
python3 app.py
```

2. Go to `/live-game` and try updating some stats
3. Check your Supabase dashboard → **Table Editor** → **live_games** to see the data

## Database Schema

### live_games Table
- Stores current live game data
- JSONB columns for team player data
- Automatic timestamps

### basketball_games Table  
- Stores completed game statistics
- Individual player performance data

### sports_buddies Table
- Stores sports buddy finder data
- Sample data included

## Features

✅ **Real-time Persistence**: All stat updates are saved to Supabase  
✅ **Fallback Mode**: App works even if Supabase is unavailable  
✅ **Automatic Game Creation**: New games are created automatically  
✅ **Data Recovery**: Stats persist between app restarts  

## Troubleshooting

### "Supabase client not initialized"
- Check your URL and key in `config.py`
- Make sure your `.env` file exists and has correct values

### "Table does not exist"
- Run the SQL schema in Supabase SQL Editor
- Check that RLS policies are created

### "Permission denied"
- Verify RLS policies are set to allow public access
- Check that your anon key is correct

## Security Notes

⚠️ **For Production**: 
- Use more restrictive RLS policies
- Implement user authentication
- Use service role key for admin operations
- Enable SSL connections

The current setup allows public read/write access for demo purposes.
