# General settings
RUNNERS = 2000              # Total number of runners
CANDIDATE_RUNNERS = 10      # Number of candidate runners per patient
CANDIDATE_AEDS = 1          # Number of candidate aeds per runner


# Neural Network settings
NN_INPUT = 2*CANDIDATE_RUNNERS
NN_OUTPUT = CANDIDATE_RUNNERS


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