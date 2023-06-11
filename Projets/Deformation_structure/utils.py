import numpy as np
import plotly.graph_objects as go
from plotly.offline import plot
from fastdist import fastdist

a = np.array


def distance(p1, p2):
    """euclidean distance between 2 points"""
    return fastdist.euclidean(p1, p2)


def distance_between_1pts_and_segment(p, a, b):
    """distance between the segment [a, b] and the point p"""
    # normalized tangent vector
    epsilon = 1e-9  # Add a small value to avoid zero division
    d = np.divide(b - a, np.linalg.norm(b - a) + epsilon)

    # signed parallel distance components
    s = np.dot(a - p, d)
    t = np.dot(p - b, d)

    # clamped parallel distance
    h = np.maximum.reduce([s, t, 0])

    # perpendicular distance component
    c = np.cross(p - a, d)

    return np.hypot(h, np.linalg.norm(c))


class Bezier_Vector_3D:
    """
    This class allows you to make a bezier curve with n control points and n position vectors in 3D
    Example:
    >>> points_control = [[0, 0, 0], [2, 2, 2]]
    >>> vector_points = [[1, 0, 0], [1, 0, 0]]
    >>> bezier = Bezier_Vector_3D(points_control, vector_points)
    >>> bezier.bezier_seg_per_seg()
    """

    def __init__(self, points_control, vector_points, echantillonnage=2000, show_control_points=False):
        """
        :param points_control: list of list of size 3, with x, y, z of each point
        :param vector_points: list of list of size 3, with coord of the vector at this point
        :param echantillonnage: Amount of points in Bezier curve
        """
        self.points_control = points_control
        self.vector_points = vector_points
        self.echantillonnage = echantillonnage
        self.show_control_points = show_control_points

    @staticmethod
    def TwoPoints(t, P1, P2):
        """Bezier function"""
        Q1 = (1 - t) * P1 + t * P2
        return Q1

    def Points(self, t, points):
        """Bezier function"""
        n_points = []
        for i1 in range(0, len(points) - 1):
            n_points += [self.TwoPoints(t, points[i1], points[i1 + 1])]
        return n_points

    def Point(self, t, points):
        """Bezier function"""
        n_points = points
        while len(n_points) > 1:
            n_points = self.Points(t, n_points)
        return n_points[0]

    def Curve(self, t_values, points):
        """Bezier function"""
        curve = np.array([[0.0] * len(points[0])])
        for t in t_values:
            curve = np.append(curve, [self.Point(t, points)], axis=0)
        curve = np.delete(curve, 0, 0)
        return curve

    def bezier_seg_per_seg(self, show=True, figure_name: str = None):
        """Create the figure, and return the length of each segment and bezier curve of the figure
        :param show: if True, plot the result
        :param figure_name: if not None, add the name in the plot
        """
        Capteurs = self.points_control
        Vectors = self.vector_points

        plotly_bezier_curve = []
        plotly_control_points = []

        dict_deformation_max_per_segment = {}

        for i in range(len(Capteurs) - 1):
            points_control = np.array(
                [Capteurs[i], [Capteurs[i][0] + Vectors[i][0], Capteurs[i][1] + Vectors[i][1],
                               Capteurs[i][2] + Vectors[i][2]],
                 [Capteurs[i + 1][0] + Vectors[i + 1][0],
                  Capteurs[i + 1][1] + Vectors[i + 1][1],
                  Capteurs[i + 1][2] + Vectors[i + 1][2]],
                 Capteurs[i + 1]])
            t_points = np.arange(0, 1, 1 / self.echantillonnage)
            curve_bezier = self.Curve(t_points, points_control)
            x_curve, y_curve, z_curve = list(curve_bezier[:, 0]), list(curve_bezier[:, 1]), list(
                curve_bezier[:, 2])
            x_pts, y_pts, z_pts = list(points_control[:, 0]), list(points_control[:, 1]), list(
                points_control[:, 2])
            # Plotly figure
            difference_normal_deformation = a([distance_between_1pts_and_segment(
                a([x_curve[j], y_curve[j], z_curve[j]]), self.points_control[i], self.points_control[i + 1])
                for j in range(self.echantillonnage)])
            dict_deformation_max_per_segment[i] = max(difference_normal_deformation)
            if max(difference_normal_deformation) < 0.0005:
                plotly_bezier_curve.append(go.Scatter3d(x=x_curve,
                                                        y=y_curve,
                                                        z=z_curve,
                                                        marker=dict(size=2,
                                                                    color="#0d0183",
                                                                    ),
                                                        name=f"Segment {i}"
                                                        ))
            else:
                plotly_bezier_curve.append(go.Scatter3d(x=x_curve,
                                                        y=y_curve,
                                                        z=z_curve,
                                                        marker=dict(size=1,
                                                                    color=difference_normal_deformation,
                                                                    colorscale='jet'),
                                                        name=f"Segment {i}"
                                                        ))
            if self.show_control_points:
                plotly_control_points.append(go.Scatter3d(x=x_pts,
                                                          y=y_pts,
                                                          z=z_pts,
                                                          marker=dict(size=1, color="black"),
                                                          name=None
                                                          ))

        data = plotly_bezier_curve + plotly_control_points if self.show_control_points else plotly_bezier_curve
        if show:
            fig_ = go.Figure(data=data, layout=go.Layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)'))
            plot(fig_)
        return data, dict_deformation_max_per_segment
