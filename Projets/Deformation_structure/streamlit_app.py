import json
import random
from datetime import datetime
import sqlite3
from Projets.Deformation_structure.utils import *
from fastdist import fastdist

flag = False


def format_distance(max_def):
    if max_def < 0.001:  # Less than 1 mm
        return f'{max_def * 1000:.2f} mm'
    elif max_def < 1.0:  # Less than 1 m
        return f'{max_def * 100:.2f} cm'
    else:
        return f'{max_def:.2f} m'


def generate_test_data():
    data = {
        "acceleration": {
            "x": random.uniform(-10.0, 10.0),
            "y": random.uniform(-10.0, 10.0),
            "z": random.uniform(-10.0, 10.0)
        },
        "gyroscope": {
            "x": random.uniform(-180.0, 180.0),
            "y": random.uniform(-180.0, 180.0),
            "z": random.uniform(-180.0, 180.0)
        }
    }

    return data


# Generate test data for each sensor
test_data_capteur1 = generate_test_data()
test_data_capteur2 = generate_test_data()
test_data_capteur3 = generate_test_data()

# Convert data to JSON format
test_data_capteur1_json = json.dumps(test_data_capteur1)
test_data_capteur2_json = json.dumps(test_data_capteur2)
test_data_capteur3_json = json.dumps(test_data_capteur3)

# Base de données SQLite
database = sqlite3.connect('Projets/Deformation_structure/accelerometer_sensor_data.db')

# Création de la table s'il n'existe pas déjà
cursor = database.cursor()
if flag:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS donnees_capteurs(
         id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
         timestamp DATETIME,
         capteur TEXT,
         acceleration_x INTEGER,
         acceleration_y INTEGER,
         acceleration_z INTEGER,
         gyroscope_x INTEGER,
         gyroscope_y INTEGER,
         gyroscope_z INTEGER
    )
    """)
    datetime_ = datetime.now()
    # Add data to sqlite database
    cursor.execute("""
        INSERT INTO donnees_capteurs(timestamp, capteur, 
        acceleration_x, acceleration_y, acceleration_z, 
        gyroscope_x, gyroscope_y, gyroscope_z) 
        VALUES(?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime_, "topicCapteur1",
        test_data_capteur1['acceleration']['x'],
        test_data_capteur1['acceleration']['y'],
        test_data_capteur1['acceleration']['z'],
        test_data_capteur1['gyroscope']['x'],
        test_data_capteur1['gyroscope']['y'],
        test_data_capteur1['gyroscope']['z']))
    cursor.execute("""
        INSERT INTO donnees_capteurs(timestamp, capteur, 
        acceleration_x, acceleration_y, acceleration_z, 
        gyroscope_x, gyroscope_y, gyroscope_z) 
        VALUES(?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime_, "topicCapteur2",
        test_data_capteur2['acceleration']['x'],
        test_data_capteur2['acceleration']['y'],
        test_data_capteur2['acceleration']['z'],
        test_data_capteur2['gyroscope']['x'],
        test_data_capteur2['gyroscope']['y'],
        test_data_capteur2['gyroscope']['z']))
    cursor.execute("""
        INSERT INTO donnees_capteurs(timestamp, capteur, 
        acceleration_x, acceleration_y, acceleration_z, 
        gyroscope_x, gyroscope_y, gyroscope_z) 
        VALUES(?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime_, "topicCapteur3",
        test_data_capteur3['acceleration']['x'],
        test_data_capteur3['acceleration']['y'],
        test_data_capteur3['acceleration']['z'],
        test_data_capteur3['gyroscope']['x'],
        test_data_capteur3['gyroscope']['y'],
        test_data_capteur3['gyroscope']['z']))
    database.commit()


# Récupérer uniquement les données des capteurs pour le dernier timestamp
def get_data_from_db_last_timestamp():
    cursor.execute("""
        SELECT * FROM donnees_capteurs
        WHERE timestamp = (SELECT MAX(timestamp) FROM donnees_capteurs)
    """)
    rows = cursor.fetchall()
    return rows


data = get_data_from_db_last_timestamp()

# create a dictionary to store the data
sensor_data = {}
for row in data:
    sensor_data[row[2]] = {
        "acceleration": {
            "x": row[3],
            "y": row[4],
            "z": row[5]
        },
        "gyroscope": {
            "x": row[6],
            "y": row[7],
            "z": row[8]
        }
    }


def load_initial_positions(file):
    with open(file, 'r') as f:
        data = json.load(f)
    return data


# initial_positions = load_initial_positions('Projets/Deformation_structure/sensor_positions.json')

# Exemple de données d'accélération
sensor_data = {'capteur0': {'x': 0, 'y': 0.1, 'z': 0},
               'capteur1': {'x': 0., 'y': 0.0, 'z': 0.1},
               'capteur2': {'x': 0.01, 'y': 0.0, 'z': -0.1},
               'capteur3': {'x': 0.2, 'y': 0.5, 'z': 0.9}}

# Initial positions
initial_positions = {'capteur0': a([0, 0, 0]),
                     'capteur1': a([0, 0, 3]),
                     'capteur2': a([0, 0, 6]),
                     'capteur3': a([0, 0, 10])}

# Calculer les vecteurs à partir des données d'accélération
vectors = {k: a([v['x'], v['y'], v['z']]) for k, v in sensor_data.items()}

# Calculer la moyenne des accélérations
mean_vector = np.mean(list(vectors.values()), axis=0)

# Convertir le vecteur moyen en vecteur distance en calculant la norme
distance_deplacement_moyen = format_distance(np.linalg.norm(mean_vector))

# Calculer les accélérations résiduelles et les utiliser pour ajuster les vecteurs
residual_vectors = {k: np.maximum(v - mean_vector, 0) for k, v in vectors.items()}

# Créer les points de contrôle et les vecteurs pour la courbe de Bézier
points_control = list(initial_positions.values())
vector_points = list(residual_vectors.values())

# Créer une nouvelle liste pour les points de contrôle déplacés
moved_points_control = [a(point) + mean_vector for point in points_control]

# Créer une instance de Bezier_Vector_3D
bezier = Bezier_Vector_3D(moved_points_control, vector_points)

data, max_def_per_segment = bezier.bezier_seg_per_seg(normal=True, show=False)
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
    midpoint = [(points_control[i][0] + points_control[i+1][0]) / 2,
                (points_control[i][1] + points_control[i+1][1]) / 2,
                (points_control[i][2] + points_control[i+1][2]) / 2]

    fig.add_trace(
        go.Scatter3d(
            x=[midpoint[0]],  # Position the annotation at the midpoint of the segment
            y=[midpoint[1]],
            z=[midpoint[2]],
            mode='text',
            text=[f'Max deformation: {formatted_def}'],
            textposition='bottom center',
            textfont=dict(size=8),
            marker=dict(size=1, color="black"),
            showlegend=False
        )
    )
fig.update_layout(
    title=f"Aperçu de la structure - Déplacement de la structure: {distance_deplacement_moyen}",
    scene=dict(
        xaxis=dict(range=[xmin, xmax], ),
        yaxis=dict(range=[ymin, ymax], ),
        zaxis=dict(range=[zmin * 0.9, zmax * 1.1], ),
    ),
    # transparent background
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
)
plot(fig)
