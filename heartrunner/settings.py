# General settings
RUNNERS = 15000              # Total number of runners
CANDIDATE_RUNNERS = 30      # Number of candidate runners per patient
CANDIDATE_AEDS = 3          # Number of candidate aeds per runner


# Neural Network settings
NN_INPUT = 2*CANDIDATE_RUNNERS
NN_HIDDEN = 2*NN_INPUT
NN_OUTPUT = CANDIDATE_RUNNERS


# Default Evolution settings
POPULATION_SIZE = 100
GENERATIONS = 10
MUTATION_RATE = 0.1
MUTATION_AMOUNT = 0.1
CROSSOVER_RATE = 0.1


# Intersection dataset
INTERSECTIONS_CSV_HEADER = ["id", "latitude", "longitude"]
INTERSECTIONS_CSV_PATH = "data/csv/intersections.csv"

# Streetsegment dataset
STREETS_GEOJSON_PATH = "data/geojson/wdc_streetsegments.geojson"
STREETS_CSV_HEADER = ["id", "head_id", "tail_id", "length", "geometry"]
STREETS_CSV_PATH = "data/csv/streetsegments.csv"

# AED dataset
AEDS_GEOJSON_PATH = "data/geojson/wdc_aeds.geojson"
AEDS_CSV_HEADER = ["id", "intersection_id", "in_use", "open_hour", "close_hour"]
AEDS_CSV_PATH = "data/csv/aeds.csv"


# Tasks dataset
TASK_PATH = "data/training/"