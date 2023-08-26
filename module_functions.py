# Normalise model scores
def normalise_score(original_score, old_min, old_max, new_min, new_max):
    old_range = old_max - old_min
    new_range = new_max - new_min
    normalised_score = (original_score - old_min) / old_range
    normalised_score = new_min + (normalised_score * new_range)
    return normalised_score