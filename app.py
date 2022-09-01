import numpy as np
import pandas as pd 
import datetime as dt 
from dateutil.relativedelta import relativedelta
import sqlalchemy 
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func 
from flask import Flask, jsonify

 
engine=create_engine("sqlite:///hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

app=Flask(__name__)

@app.route("/")
def welcome():
    return(    
        f"Hawaii Climate Analysis<br>"
        f"Available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )
       
  
@app.route("/api/v1.0/precipitation")
def prcp():
    
    session = Session(engine)  

    prcp= session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    all_prcp_data= []
    for date, prcp in prcp:
        prcp_dict= {}
        prcp_dict['date']= prcp
        all_prcp_data.append(prcp_dict)
    
    return jsonify(all_prcp_data)



@app.route('/api/v1.0/stations')
def stations():
  
    session= Session(engine)
    stations= session.query(Measurement.station).group_by(Measurement.station).all()
    session.close()

    all_stations= list(np.ravel(stations))
    return jsonify(all_stations)


@app.route('/api/v1.0/tobs')
def tobs():

    session=Session(engine)
    query_date=dt.date(2017,8,23) - dt.timedelta(days=365)

    active_station = session.query(Measurement.station).group_by(Measurement.station).\
    order_by(func.count(Measurement.date).desc()).first()
    active_station = active_station[0]

    tobs= session.query(Measurement.station, Measurement.tobs).filter(Measurement.station==active_station).\
    filter(Measurement.date >= query_date).all()

    session.close()

    all_tobs=list(np.ravel(tobs))
    return jsonify(all_tobs)




@app.route('/api/v1.0/<start>')
def start_date(start):
  
    session = Session(engine)
    start_date = dt.datetime.strptime(start,'%Y-%m-%d')
    
    
    results= session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    session.close()

    dt_list = []
    for result in results:
        dates = {}
        dates["Start Date"] = start_date
        dates["TMIN"] = result[0]
        dates["TAVG"] = result[1]
        dates["TMAX"] = result[2]
        dt_list.append(dates)

    return jsonify(dt_list)


@app.route('/api/v1.0/<start>/<end>')
def dates(start, end):
    session = Session(engine)

    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end,'%Y-%m-%d')

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date)

    session.close()

    dt_list = []
    for result in results:
        dates = {}
        dates["Start Date"] = start_date
        dates["End Date"] = end_date
        dates["TMIN"] = result[0]
        dates["TAVG"] = result[1]
        dates["TMAX"] = result[2]
        dt_list.append(dates)
        if ((dates["TMIN"] =="null") and (dates["TAVG"] == "null") and (dates["TMAX"] == "null")):
            print("That does not appear in this dataset")

    return jsonify(dt_list)


if __name__ == "__main__":
    app.run(debug=True)