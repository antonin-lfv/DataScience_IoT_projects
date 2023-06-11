from Projets.Deformation_structure.utils import *
from fastdist import fastdist
import json

# Initial positions from Projets/Deformation_structure/sensor_initial_positions.json
with open("Projets/Deformation_structure/sensor_initial_positions.json", "r") as f:
    initial_positions = json.load(f)
    # convert all values to numpy arrays
    initial_positions = {k: a(v) for k, v in initial_positions.items()}

# accelerations
accel_data = {'capteur0': {'x': 0, 'y': 0.1, 'z': 0},
              'capteur1': {'x': 0., 'y': 0.0, 'z': 0.1},
              'capteur2': {'x': 0.01, 'y': 0.0, 'z': -0.1},
              'capteur3': {'x': 0.2, 'y': 0.5, 'z': 0.9}}

# Exemple de données de gyroscope
gyro_data = {'capteur0': {'x': 0, 'y': 0.1, 'z': 0},
             'capteur1': {'x': 0., 'y': 0.0, 'z': 0.1},
             'capteur2': {'x': 0.01, 'y': 0.0, 'z': -0.1},
             'capteur3': {'x': 0.01, 'y': 0.1, 'z': 0.1}}


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
                textfont=dict(size=8),
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
                textfont=dict(size=8),
                marker=dict(size=1, color="black"),
                showlegend=False
            )
        )
    fig.update_layout(
        title=f"Aperçu de la structure",
        scene=dict(
            xaxis=dict(range=[xmin, xmax], ),
            yaxis=dict(range=[ymin, ymax], ),
            zaxis=dict(range=[zmin * 0.9, zmax * 1.1], ),
        ),
        template="plotly_white",
    )

    return fig, moved_points_control


fig, new_positions = compute_structure(accel_data, initial_positions, gyro_data)
plot(fig)
