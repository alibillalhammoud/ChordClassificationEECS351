

# takes in a time and returns the corresponding index in the spectrogram matrix
def t2ind(t):
    return next(x for x, val in enumerate(times) if val > t)

def freq2note(freq, piano_frequencies):
    smallest_diff = 1e6
    for (n, f) in piano_frequencies:
        diff = abs(f - freq)
        if diff < smallest_diff:
            smallest_diff = diff
            note = n
    return note
