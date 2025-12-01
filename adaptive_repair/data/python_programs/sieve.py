def sieve(max):
    if max < 2:
        return []

    # Create a boolean list 'is_prime' of size (max + 1) and initialize all entries to True.
    # is_prime[i] will be True if i is prime, False otherwise.
    is_prime = [True] * (max + 1)

    # 0 and 1 are not prime numbers, so mark them as False.
    is_prime[0] = is_prime[1] = False

    # Iterate from 2 up to the square root of max.
    # We only need to check for prime factors up to sqrt(max)
    # because if a number n has a prime factor greater than sqrt(n),
    # it must also have a prime factor smaller than sqrt(n).
    for p in range(2, int(max**0.5) + 1):
        # If is_prime[p] is still True, then p is a prime number.
        if is_prime[p]:
            # Mark all multiples of p (starting from p*p) as not prime.
            # Multiples smaller than p*p (e.g., 2*p, 3*p, ..., (p-1)*p)
            # would have already been marked by their smaller prime factors (2, 3, ..., p-1).
            for multiple in range(p*p, max + 1, p):
                is_prime[multiple] = False

    # Collect all numbers that are still marked as prime.
    primes = [i for i in range(2, max + 1) if is_prime[i]]
    return primes

"""
Sieve of Eratosthenes

Input:
    max: A positive int representing an upper bound.

Output:
    A list containing all primes up to and including max
"""
