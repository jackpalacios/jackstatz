-- Supabase Database Schema for Basketball Stats Tracker

-- Create the live_games table
CREATE TABLE IF NOT EXISTS live_games (
    id BIGSERIAL PRIMARY KEY,
    team1_name TEXT NOT NULL DEFAULT 'TEAM 1',
    team2_name TEXT NOT NULL DEFAULT 'TEAM 2',
    team1_data JSONB NOT NULL,
    team2_data JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create the basketball_games table for completed games
CREATE TABLE IF NOT EXISTS basketball_games (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    opponent TEXT NOT NULL,
    team_score INTEGER NOT NULL,
    opponent_score INTEGER NOT NULL,
    result TEXT NOT NULL,
    points INTEGER NOT NULL,
    rebounds INTEGER NOT NULL,
    assists INTEGER NOT NULL,
    steals INTEGER NOT NULL,
    blocks INTEGER NOT NULL,
    turnovers INTEGER NOT NULL,
    fouls INTEGER NOT NULL,
    minutes_played INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create the sports_buddies table
CREATE TABLE IF NOT EXISTS sports_buddies (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    sport TEXT NOT NULL,
    location TEXT NOT NULL,
    availability TEXT NOT NULL,
    skill_level TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security (RLS)
ALTER TABLE live_games ENABLE ROW LEVEL SECURITY;
ALTER TABLE basketball_games ENABLE ROW LEVEL SECURITY;
ALTER TABLE sports_buddies ENABLE ROW LEVEL SECURITY;

-- Create policies for public read/write access (for demo purposes)
-- In production, you'd want more restrictive policies

-- Live games policies
CREATE POLICY "Allow public read access to live_games" ON live_games
    FOR SELECT USING (true);

CREATE POLICY "Allow public insert access to live_games" ON live_games
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public update access to live_games" ON live_games
    FOR UPDATE USING (true);

-- Basketball games policies
CREATE POLICY "Allow public read access to basketball_games" ON basketball_games
    FOR SELECT USING (true);

CREATE POLICY "Allow public insert access to basketball_games" ON basketball_games
    FOR INSERT WITH CHECK (true);

-- Sports buddies policies
CREATE POLICY "Allow public read access to sports_buddies" ON sports_buddies
    FOR SELECT USING (true);

CREATE POLICY "Allow public insert access to sports_buddies" ON sports_buddies
    FOR INSERT WITH CHECK (true);

-- Insert some sample data
INSERT INTO sports_buddies (name, age, sport, location, availability, skill_level) VALUES
    ('Alex', 12, 'basketball', 'Central Park', 'Weekends', 'intermediate'),
    ('Sam', 10, 'soccer', 'Riverside Fields', 'After school', 'beginner'),
    ('Jordan', 11, 'tennis', 'Community Center', 'Weekdays', 'advanced')
ON CONFLICT DO NOTHING;

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_live_games_updated_at 
    BEFORE UPDATE ON live_games 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
