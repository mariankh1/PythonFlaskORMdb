#
#
#
#>>> from manager import db
#>>> db.create_all()
#>>> exit()
import os
from flask import redirect
from flask import Flask
from flask import render_template
from flask import request
from marshmallow_jsonapi.flask import Schema
from marshmallow_jsonapi import fields 
from flask_sqlalchemy import SQLAlchemy
from flask_rest_jsonapi import Api, ResourceDetail, ResourceList 
project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "dronedatabase.db"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file

db = SQLAlchemy(app)

class Pilot(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  birth_year = db.Column(db.Integer)

class Drone(db.Model):
    id = db.Column(db.Integer, db.Sequence('seq_reg_id', start=1, increment=1),
               primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False, primary_key=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    altitude = db.Column(db.Float)

    def __repr__(self):
        return "<Name: {}>".format(self.name)

db.create_all()

@app.route("/", methods=["GET", "POST"])
def home():
    if request.form:
        drone = Drone(name=request.form.get("name"))
        db.session.add(drone)
        db.session.commit()
    drones = Drone.query.all()
    return render_template("home.html", drones=drones)

@app.route("/delete", methods=["POST"])
def delete():
    name = request.form.get("name")
    drone = Drone.query.filter_by(name=name).first()
    db.session.delete(drone)
    db.session.commit()
    return redirect("/")
 
@app.route("/update", methods=["POST"])
def update():
    newname = request.form.get("newname")
    oldname = request.form.get("oldname")
    drone = Drone.query.filter_by(name=oldname).first()
    drone.name = newname
    db.session.commit()
    return redirect("/")

# Create data abstraction layer 
class DroneSchema(Schema):
  class Meta:
    type_ = 'drone'

    self_view = 'drone_one'
    self_view_kwargs = {'id': '<id>'}
    self_view_many = 'drone_many'
  id = fields.Integer()
  name = fields.Str(required=True)
  latitude = fields.Float(required=False)
  longitude = fields.Float(required=False)
  altitude = fields.Float(required=False)
class DroneMany(ResourceList):
  schema = DroneSchema
  data_layer = {'session': db.session, 'model': Drone}

class DroneOne(ResourceDetail):
  schema = DroneSchema
  data_layer = {'session': db.session, 'model': Drone}
 
api = Api(app)
api.route(DroneMany, 'drone_many', '/drones')
api.route(DroneOne, 'drone_one', '/drones/<int:id>')

# Create data abstraction layer 
class PilotSchema(Schema):
  class Meta:
    type_ = 'pilot'
    self_view = 'pilot_one'
    self_view_kwargs = {'id': '<id>'}
    self_view_many = 'pilot_many'

  id = fields.Integer()
  name = fields.Str(required=True)
  birth_year = fields.Integer(load_only=True)
  genre = fields.Str()

class PilotMany(ResourceList):
  schema = PilotSchema
  data_layer = {'session': db.session, 'model': Pilot}

class PilotOne(ResourceDetail):
  schema = PilotSchema
  data_layer = {'session': db.session, 'model': Pilot}
 
api = Api(app)
api.route(PilotMany, 'pilot_many', '/pilots')
api.route(PilotOne, 'pilot_one', '/pilots/<int:id>')

if __name__ == "__main__":
    app.run(debug=True)



