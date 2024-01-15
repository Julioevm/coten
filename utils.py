import random


def replace_items_in_list(target_list, start_index, items_to_replace):
    """
    Replaces elements in target_list with elements from items_to_replace
    """
    # Ensure the start_index + number of items does not exceed the length of the target_list
    end_index = min(start_index + len(items_to_replace), len(target_list))

    # Replace elements in target_list with elements from items_to_replace
    target_list[start_index:end_index] = items_to_replace[: end_index - start_index]

    return target_list


def triangular_dist(min_value: int, max_value: int) -> int:
    # The mode (most common value) is the midpoint of the range
    mode = (min_value + max_value) / 2.0
    # Return a random number following a triangular distribution
    return int(round(random.triangular(min_value, max_value, mode)))


def bell_curve_dist(min_value: int, max_value: int) -> int:
    # The mean (average) value
    mean = (min_value + max_value) / 2.0
    # Standard deviation
    std_dev = (max_value - min_value) / 6.0  # Approximation for a bell curve
    while True:
        # Generate a value from a Gaussian distribution
        value = random.gauss(mean, std_dev)
        # Check if it's within the desired range
        if min_value <= value <= max_value:
            return int(round(value))
