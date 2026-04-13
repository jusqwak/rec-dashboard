# Metaphorical Recreation Center
A sample application for a metaphorical recreational center. Includes passes, members, bookings

# Setup
## Requirements
```
flask
mysql-connector-python
```

Install with:
```
pip install flask mysql-connector-python
```

## MySQL Setup
1. Create a `.env` file in the project root with your database credentials:
   ```env
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=yourpass
   DB_DATABASE=rec_center
   ```

2. The app will automatically load that `.env` file when it starts.

3. The `rec_center` database and all tables are **created automatically** on first run.
   You do NOT need to run any SQL manually.

## Running the app
```
python app.py
```

Open site with localhost link


## Features
- ✅ Member check-in / check-out (persisted in MySQL)
- ✅ Check-in button disabled when already inside; Check-out disabled when not inside
- ✅ Activity log (persists across restarts)
- ✅ Guest pass issuance
- ✅ Facility bookings (pool lane, gym court, meeting room, racquetball)
- ✅ Live stats: inside count, today's check-ins, guest passes, bookings
- ✅ Auto-refreshes every 15 seconds
