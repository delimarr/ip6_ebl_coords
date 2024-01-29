"""Functions to transform/visualize GoT data."""
import warnings

import numpy as np
from scipy.spatial.distance import cdist


def get_tolerance_mask(coords: np.ndarray, tolerance: int) -> np.ndarray:
    """Compare the distance to both neighbours, disregard first and last point.

    Args:
        coords (np.ndarray): coordinates
        tolerance (int): minimal distance of closer neighbour.

    Returns:
        np.ndarray: boolean mask
    """
    # scatter & and reduce with minus
    d = coords[1:, :] - coords[:-1, :]
    # calculate norm
    d = np.apply_along_axis(np.linalg.norm, axis=1, arr=d)

    # scatter
    d_mask = np.c_[d[:-1], d[1:]]
    # reduce with min
    d_mask = d_mask.min(axis=1) <= tolerance
    return d_mask


def get_track_switches_hit(
    labels: np.ndarray,
    label_coords: np.ndarray,
    waypoints: np.ndarray,
    threshold: float,
) -> np.ndarray:
    """Get all labels, which near any waypoint.

    Raise Warning if not all waypoint are distinctively mapped.

    Args:
        labels (np.ndarray): lables of coords, labels-length = number of label_coords
        label_coords (np.ndarray): coordinates of labels
        waypoints (np.ndarray): any waypoints
        threshold (float): radius <= of sphere around label_coords

    Returns:
        np.ndarray: All labels which have at least one waypoint in threshold distance.
    """
    distances = cdist(label_coords, waypoints)
    distances = distances <= threshold
    labels_hits = distances.sum(axis=1)
    if distances.sum(axis=0).max() > 1:
        warnings.warn("double hits!")
    return labels[labels_hits >= 1]
