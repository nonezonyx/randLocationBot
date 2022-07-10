from haversine import inverse_haversine, Unit
import random

def random_coordinates(coords, radius, unit='m'):
    """
    args - coords (Tuple: (lat: float, lng: float)), radius (float), unit (haversine.Unit enum)
    returns - new_coords (Tuple: (lat: float, lng: float))
    """

    # Choosing a random float between 0 and 2π
    random_direction = random.uniform(0.0, 3.14159 * 2)

    random_distance = random.uniform(0.0, radius)

    new_coords = inverse_haversine(
            point=coords,
            distance=random_distance,
            direction=random_direction,
            unit=unit
        )

    return new_coords
