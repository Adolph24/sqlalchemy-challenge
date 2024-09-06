# Import the dependencies.
# SQLAlchemy dependencies for ORM and database connection
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

from flask import Flask, jsonify

# Dependencies for data manipulation and analysis
import pandas as pd
import numpy as np

# Dependencies for date handling
from datetime import datetime, timedelta

# Matplotlib for data visualization
import matplotlib.pyplot as plt



#################################################
# Database Setup
#################################################

# Step 1: Create an engine to connect to the SQLite database
engine = create_engine("sqlite:///mnt/data/hawaii.sqlite")

# Step 2: Reflect the database into a new model
Base = automap_base()

# Step 3: Reflect the tables
Base.prepare(engine, reflect=True)

# Step 4: View all of the classes that automap found
print("Classes found by automap:", Base.classes.keys())

# Step 5: Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Step 6: Create a session to link Python to the database
session = Session(engine)

# Verify setup by querying the first row in the Station table
first_station = session.query(Station).first()
print("First station entry:", first_station.__dict__)



#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

# Step 5: Define Flask Routes

@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a JSON representation of the precipitation data for the last year."""
    # Create session from Python to the DB
    session = Session(engine)
    
    # Find the most recent date in the data set
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    
    # Calculate the date one year ago from the last data point in the database
    one_year_ago = datetime.strptime(most_recent_date, "%Y-%m-%d") - timedelta(days=365)
    
    # Perform a query to retrieve the date and precipitation scores
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()
    
    session.close()

    # Convert the query results to a dictionary with 'date' as the key and 'prcp' as the value
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations."""
    # Create session from Python to the DB
    session = Session(engine)
    
    # Query all stations
    stations_data = session.query(Station.station).all()
    
    session.close()

    # Convert the list of tuples into a normal list
    stations_list = list(np.ravel(stations_data))

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def temperature_observations():
    """Return a JSON list of temperature observations (TOBS) for the previous year."""
    # Create session from Python to the DB
    session = Session(engine)
    
    # Find the most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).\
        first()[0]

    # Find the most recent date in the data set
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    
    # Calculate the date one year ago from the last data point in the database
    one_year_ago = datetime.strptime(most_recent_date, "%Y-%m-%d") - timedelta(days=365)

    # Query temperature observations for the most active station for the last year
    temperature_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).all()
    
    session.close()

    # Convert the query results to a list of dictionaries
    temperature_list = [{date: tobs} for date, tobs in temperature_data]

    return jsonify(temperature_list)

# Step 6: Run the application
if __name__ == '__main__':
    app.run(debug=True)
