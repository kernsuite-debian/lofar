from fractions import gcd

__all__ = ["lcm"]

def lcm(a, b):
    """ Return the Least Common Multiple of a and b. """
    return abs(a * b) / gcd(a, b) if a and b else 0
