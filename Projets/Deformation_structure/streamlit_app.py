from utils import *
from fastdist import fastdist
import json
from pymongo import MongoClient
import streamlit as st

# ====== Streamlit ====== #
st.set_page_config(layout="wide")
st.title("Deformation structure")
st.divider()
figure = st.empty()

# Configuration du serveur MQTT
file_path_config = "config.json"
# le fichier config ressemble à ça :
# {
#   "ssid" : "your ssid",
#   "password" : "your password
#   "mqtt_server_ip" : "your mqtt server ip",
#   "mongo_server_url" : "mongodb://localhost:27017/"
# }
try:
    with open(file_path_config) as config_file:
        config = json.load(config_file)
    mqtt_server = config['mqtt_server_ip']
    mongo_server_url = config['mongo_server_url']
except FileNotFoundError:
    print("Le fichier de configuration n'a pas été trouvé")
    exit()

client = MongoClient(mongo_server_url)
db = client.deformation_structure_db

# Get initial positions :
# Get the last timestamp from the collection history_positions and sensor_data
# If the two timestamps are the same, we get the before last timestamp for the current positions
# Else, we get the last timestamp for the current positions
last_timestamp_history_positions = db.history_positions.find().sort('timestamp', -1).limit(1)[0]['timestamp']
last_timestamp_sensor_data = db.sensor_data.find().sort('timestamp', -1).limit(1)[0]['timestamp']
if last_timestamp_history_positions == last_timestamp_sensor_data:
    initial_positions = db.history_positions.find().sort('timestamp', -1).limit(2)[1]
    initial_positions = {k: a(v) for k, v in initial_positions['positions'].items() if k != '_id'}
else:
    initial_positions = db.history_positions.find().sort('timestamp', -1).limit(1)[0]
    initial_positions = {k: a(v) for k, v in initial_positions['positions'].items() if k != '_id'}

# Get acceleration and gyro data from the database deformation_structure_db and collection sensor_data
# Select the one with the most recent timestamp
data = db.sensor_data.find().sort('timestamp', -1).limit(1)[0]
accel_data = data['acceleration']
gyro_data = data['gyroscope']
timestamp = data['timestamp']


def compute_structure(accel_data, initial_positions, gyro_data):
    """
    :param accel_data: dict of dict with x, y, z of each sensor
    :param initial_positions: dict of array of size 3, with x, y, z of each sensor
    :param gyro_data: dict of dict with x, y, z of each sensor
    :return: fig, new_positions
    """
    # Compute the vectors from the acceleration data
    vectors = {k: a([v['x'], v['y'], v['z']]) for k, v in accel_data.items()}

    # Compute the mean of the accelerations
    mean_vector = np.mean(list(vectors.values()), axis=0)

    # Compute the residual accelerations and use them to adjust the vectors
    residual_vectors = {k: np.maximum(v - mean_vector, 0) for k, v in vectors.items()}

    # Create the control points and vectors for the Bezier curve
    points_control = list(initial_positions.values())
    vector_points = list(residual_vectors.values())

    # Compute the vectors from the gyroscope data
    gyro_vectors = {k: a([v['x'], v['y'], v['z']]) for k, v in gyro_data.items()}

    # Compute the mean of the rotations
    mean_gyro_vector = np.mean(list(gyro_vectors.values()), axis=0)

    # Compute the residual rotations
    residual_gyro_vectors = {k: v - mean_gyro_vector for k, v in gyro_vectors.items()}

    # Rotate and move control points
    moved_points_control = [rotate_point(a(point) + mean_vector, residual_gyro_vectors[k]) for k, point in
                            initial_positions.items()]

    # Créer une instance de Bezier_Vector_3D
    bezier = Bezier_Vector_3D(moved_points_control, vector_points)

    data, max_def_per_segment = bezier.bezier_seg_per_seg(show=False)
    # moved structure
    data.append(go.Scatter3d(x=[moved_points_control[i][0] for i in range(len(moved_points_control))],
                             y=[moved_points_control[i][1] for i in range(len(moved_points_control))],
                             z=[moved_points_control[i][2] for i in range(len(moved_points_control))],
                             mode="lines+markers",
                             opacity=1,
                             name=f"moved structure",
                             marker=dict(color="black", size=2),
                             line=dict(color="black", width=2)))
    # initial structure
    data.append(go.Scatter3d(x=[initial_positions[i][0] for i in initial_positions.keys()],
                             y=[initial_positions[i][1] for i in initial_positions.keys()],
                             z=[initial_positions[i][2] for i in initial_positions.keys()],
                             mode="lines+markers",
                             opacity=1,
                             name=f"initial structure",
                             marker=dict(color="green", size=2),
                             line=dict(color="green", width=2)))

    # Compute the euclidean distance between the initial and moved points using fastdist
    distances = [fastdist.euclidean(point, moved_points_control[i]) for i, point in enumerate(points_control)]
    # Convert distances to appropriate units
    distances = [format_distance(d) for d in distances]

    # Add text to the graph showing the distance moved by each sensor
    for i, (point, distance) in enumerate(zip(moved_points_control, distances)):
        data.append(
            go.Scatter3d(
                x=[point[0]], y=[point[1]], z=[point[2]],
                mode="text",
                text=[f"Déplacement du capteur : {distance}"],
                textposition="top left",
                textfont=dict(size=10),
                showlegend=False
            )
        )

    zmax = max([moved_points_control[i][2] for i in range(len(moved_points_control))])
    zmin = min([moved_points_control[i][2] for i in range(len(moved_points_control))])
    xmax = max([moved_points_control[i][0] for i in range(len(moved_points_control))]) + abs(zmax - zmin)
    xmin = min([moved_points_control[i][0] for i in range(len(moved_points_control))]) - abs(zmax - zmin)
    ymax = max([moved_points_control[i][1] for i in range(len(moved_points_control))]) + abs(zmax - zmin)
    ymin = min([moved_points_control[i][1] for i in range(len(moved_points_control))]) - abs(zmax - zmin)

    fig = go.Figure(data=data)
    # Add scatter plots to the figure for each segment
    for i, max_def in max_def_per_segment.items():
        formatted_def = format_distance(max_def)

        # Calculate the midpoint of the segment
        midpoint = [(points_control[i][0] + points_control[i + 1][0]) / 2,
                    (points_control[i][1] + points_control[i + 1][1]) / 2,
                    (points_control[i][2] + points_control[i + 1][2]) / 2]

        fig.add_trace(
            go.Scatter3d(
                x=[midpoint[0]],  # Position the annotation at the midpoint of the segment
                y=[midpoint[1]],
                z=[midpoint[2]],
                mode='text',
                text=[f'Max deformation: {formatted_def}'],
                textposition='top right',
                textfont=dict(size=10),
                marker=dict(size=1, color="black"),
                showlegend=False
            )
        )
    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[xmin, xmax], ),
            yaxis=dict(range=[ymin, ymax], ),
            zaxis=dict(range=[zmin * 0.9, zmax * 1.1], ),
            # add zoom
            camera=dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=1.25, y=1.25, z=1.25))
        ),
        width=800,
        height=800,
        template="plotly_white",
        # set margin to 0
        margin=dict(l=0, r=0, b=0, t=0)
    )

    return fig, moved_points_control


fig, new_positions = compute_structure(accel_data, initial_positions, gyro_data)
figure.plotly_chart(fig, use_container_width=True)

# === Insert new positions in mongoDB only if the last timestamp in history_positions is different
# from the last timestamp of sensor_data collection ===
# Get the last timestamp of the sensor_data collection
last_timestamp = list(db.sensor_data.find().sort("timestamp", -1).limit(1))[0]["timestamp"]
# Get the last timestamp of the history_positions collection
last_timestamp_history = list(db.history_positions.find().sort("timestamp", -1).limit(1))[0]["timestamp"]

if last_timestamp != last_timestamp_history:
    # Save the new positions to mongoDB in the database deformation_structure_db and the collection history_positions
    db = client.deformation_structure_db
    collection = db.history_positions
    # create the json to insert with same keys as initial_positions
    collection.insert_one({"timestamp": timestamp,
                           "positions": {key: list(val) for key, val in zip(initial_positions.keys(), new_positions)}})
