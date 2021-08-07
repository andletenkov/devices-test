import random


def random_hz():
    return random.choice([1, 2, 5, 10, 20, 50, 100, 200, 500])


def random_percent():
    return random.randint(0, 100)
