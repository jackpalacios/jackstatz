# 🏀 Sports Buddy Finder

A simple web application built with Flask and HTMX to help kids find other kids to play sports with nearby.

## Features

- **Search for Sports Buddies**: Filter by sport, location, and age range
- **Add Yourself**: Kids can add themselves as sports buddies
- **Real-time Updates**: Uses HTMX for dynamic content updates without page refreshes
- **Responsive Design**: Works on desktop and mobile devices
- **Kid-friendly UI**: Colorful, modern design that's appealing to children

## Tech Stack

- **Backend**: Python Flask
- **Frontend**: HTML, CSS, HTMX
- **Styling**: Vanilla CSS with modern design patterns

## Setup Instructions

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python app.py
   ```

3. **Open your browser** and go to:
   ```
   http://localhost:5000
   ```

## How to Use

1. **Search for Sports Buddies**:
   - Use the search filters at the top to find kids playing specific sports
   - Filter by location, age range, and sport type
   - Results update automatically as you change filters

2. **Add Yourself as a Sports Buddy**:
   - Fill out the form at the bottom of the page
   - Include your name, age, preferred sport, location, availability, and skill level
   - Click "Add Me as a Sports Buddy!" to join the community

3. **Contact Other Kids**:
   - Use the "Contact" and "Message" buttons on buddy cards (currently placeholder buttons)

## Project Structure

```
jackhacks/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   ├── index.html        # Main page template
│   └── buddy_list.html   # Buddy list partial template
└── static/
    └── css/
        └── style.css     # Stylesheet
```

## Future Enhancements

- User authentication and profiles
- Real-time messaging between users
- Location-based matching using GPS
- Photo uploads for sports buddies
- Event creation and RSVP system
- Parent/guardian approval system
- Integration with sports facilities and parks

## Development Notes

- Currently uses in-memory storage for demo purposes
- In a production environment, you'd want to use a proper database
- The app is designed to be simple and kid-friendly
- HTMX provides smooth, dynamic interactions without complex JavaScript

## Contributing

This is a basic starter project. Feel free to extend it with additional features like:
- Database integration (SQLite, PostgreSQL, etc.)
- User authentication
- Real-time features
- Mobile app version
- Parent dashboard
