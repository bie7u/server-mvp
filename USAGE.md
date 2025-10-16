# Usage Examples

## Setting Up

1. Clone the repository and install dependencies:
```bash
git clone <repository-url>
cd server-mvp
pip install -r requirements.txt
```

2. Set up your API key:
```bash
export FOOTBALL_DATA_API_KEY='your_api_key_here'
```

You can get a free API key from https://www.football-data.org/client/register

3. Run migrations:
```bash
python manage.py migrate
```

## Fetching League Data

### Fetch Premier League Current Season
```bash
python manage.py fetch_league_data 2021
```

### Fetch Multiple Leagues
```bash
python manage.py fetch_league_data 2021 2014 2015
```

This will fetch:
- 2021: Premier League (England)
- 2014: La Liga (Spain)  
- 2015: Ligue 1 (France)

### Fetch a Specific Season
```bash
python manage.py fetch_league_data 2021 --season 2023
```

### Fetch All Available Seasons
```bash
python manage.py fetch_league_data 2021 --all-seasons
```

## Working with Data

### Django Shell
```python
python manage.py shell

# Import models
from leagues.models import League, Season, Team, Match, Standing

# Get all leagues
leagues = League.objects.all()

# Get current season matches
from django.utils import timezone
upcoming_matches = Match.objects.filter(
    utc_date__gte=timezone.now()
).order_by('utc_date')[:10]

# Get standings for a season
season = Season.objects.first()
standings = Standing.objects.filter(season=season).order_by('position')

# Get matches by round/matchday
round_10_matches = Match.objects.filter(matchday=10)
```

### Django Admin

Start the development server:
```bash
python manage.py createsuperuser  # Create admin user first
python manage.py runserver
```

Visit http://localhost:8000/admin/ to:
- Browse leagues, seasons, and teams
- View match schedules and results
- Check league standings
- Filter by matchday/round numbers

## Common Competition IDs

- 2021: Premier League (England)
- 2014: La Liga (Spain)
- 2015: Ligue 1 (France)
- 2002: Bundesliga (Germany)
- 2019: Serie A (Italy)
- 2001: UEFA Champions League
- 2018: European Championship
- 2000: FIFA World Cup

## API Rate Limits

The free tier of football-data.org API has rate limits:
- 10 requests per minute
- 100 requests per day

Be mindful of these limits when fetching data, especially with `--all-seasons`.

## Data Structure

### Match Rounds
Each match has a `matchday` field that represents the round number. For example:
- Premier League: Matchday 1-38
- Champions League: Group stage matchdays, knockout rounds

### Match Status
- `SCHEDULED`: Match not yet played
- `TIMED`: Match scheduled with confirmed time
- `IN_PLAY`: Match currently being played
- `PAUSED`: Halftime
- `FINISHED`: Match completed
- `POSTPONED`: Match postponed
- `CANCELLED`: Match cancelled

### Standings
The Standing model tracks:
- Position in the table
- Games played, won, drawn, lost
- Goals for, goals against, goal difference
- Total points
