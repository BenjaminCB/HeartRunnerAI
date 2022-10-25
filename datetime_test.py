from datetime import datetime, timedelta
from random import random


if __name__ == "__main__":
    count = 0
    for i in range(86400):
        if random() < 0.0001:
            count += 1
    print(count)