"""
Bincom ICT - Python Basic Developer Test
Answers all 9 questions. Works on Python 3.

Usage:
    python bincom_test.py                 # uses the table embedded below
    python bincom_test.py page.html       # parses your own saved HTML file

PostgreSQL (question 6) needs:  pip install psycopg2-binary
Easiest (Neon or any hosted Postgres): set DATABASE_URL to the connection string, e.g.
    export DATABASE_URL="postgresql://user:pass@host/dbname?sslmode=require"
Or set connection details with environment variables (defaults shown):
    PGHOST=localhost PGPORT=5432 PGDATABASE=bincom PGUSER=postgres PGPASSWORD=postgres
"""
import os
import random
import re
import statistics
import sys
from collections import Counter

# The web page data (same table as the given HTML)
HTML = """
<table><tbody>
<tr><td>MONDAY</td><td>GREEN, YELLOW, GREEN, BROWN, BLUE, PINK, BLUE, YELLOW, ORANGE, CREAM, ORANGE, RED, WHITE, BLUE, WHITE, BLUE, BLUE, BLUE, GREEN</td></tr>
<tr><td>TUESDAY</td><td>ARSH, BROWN, GREEN, BROWN, BLUE, BLUE, BLEW, PINK, PINK, ORANGE, ORANGE, RED, WHITE, BLUE, WHITE, WHITE, BLUE, BLUE, BLUE</td></tr>
<tr><td>WEDNESDAY</td><td>GREEN, YELLOW, GREEN, BROWN, BLUE, PINK, RED, YELLOW, ORANGE, RED, ORANGE, RED, BLUE, BLUE, WHITE, BLUE, BLUE, WHITE, WHITE</td></tr>
<tr><td>THURSDAY</td><td>BLUE, BLUE, GREEN, WHITE, BLUE, BROWN, PINK, YELLOW, ORANGE, CREAM, ORANGE, RED, WHITE, BLUE, WHITE, BLUE, BLUE, BLUE, GREEN</td></tr>
<tr><td>FRIDAY</td><td>GREEN, WHITE, GREEN, BROWN, BLUE, BLUE, BLACK, WHITE, ORANGE, RED, RED, RED, WHITE, BLUE, WHITE, BLUE, BLUE, BLUE, WHITE</td></tr>
</tbody></table>
"""

# Typos found in the data: "BLEW" is BLUE, "ARSH" is ASH.
CORRECTIONS = {"BLEW": "BLUE", "ARSH": "ASH"}


def load_colours(html):
    """Return a flat list of every colour worn during the week."""
    rows = re.findall(r"<td>[A-Z]+DAY</td>\s*<td>(.*?)</td>", html, re.S)
    colours = []
    for row in rows:
        for c in row.split(","):
            c = c.strip().upper()
            if c:
                colours.append(CORRECTIONS.get(c, c))
    return colours


# Questions 1-5: statistics
def analyse(colours):
    freq = Counter(colours)
    total = len(colours)

    # 1. Mean colour: the colour whose frequency is closest to the mean frequency
    mean_freq = total / len(freq)
    mean_colour = min(freq, key=lambda c: (abs(freq[c] - mean_freq), c))

    # 2. Most worn colour
    most_worn = freq.most_common(1)[0][0]

    # 3. Median colour: sort colours by frequency, take the middle one
    ordered = sorted(freq, key=lambda c: (freq[c], c))
    median_colour = ordered[len(ordered) // 2]
    median_note = ""
    if len(ordered) % 2 == 0:
        median_note = " (even number of colours; the other middle colour is %s)" % ordered[len(ordered) // 2 - 1]

    # 4. Variance of the colour frequencies
    variance = statistics.pvariance(list(freq.values()))

    # 5. Probability of picking red at random
    p_red = freq["RED"] / total

    print("Colour frequencies:", dict(freq.most_common()))
    print("Total shirts counted:", total)
    print()
    print("1. Mean frequency = %.2f -> mean colour: %s" % (mean_freq, mean_colour))
    print("2. Most worn colour: %s (%d times)" % (most_worn, freq[most_worn]))
    print("3. Median colour: %s%s" % (median_colour, median_note))
    print("4. Variance of frequencies: %.4f" % variance)
    print("5. P(red) = %d/%d = %.4f" % (freq["RED"], total, p_red))
    return freq


# Question 6: save to PostgreSQL
def save_to_postgres(freq):
    try:
        import psycopg2
    except ImportError:
        print("6. psycopg2 not installed (pip install psycopg2-binary). Skipping DB step.")
        return
    try:
        db_url = os.getenv("DATABASE_URL")  # e.g. the connection string from Neon
        if db_url:
            conn = psycopg2.connect(db_url)
        else:
            conn = psycopg2.connect(
                host=os.getenv("PGHOST", "localhost"),
                port=os.getenv("PGPORT", "5432"),
                dbname=os.getenv("PGDATABASE", "bincom"),
                user=os.getenv("PGUSER", "postgres"),
                password=os.getenv("PGPASSWORD", "postgres"),
            )
    except Exception as e:
        print("6. Could not connect to PostgreSQL (%s). Skipping DB step." % str(e).strip())
        return
    with conn, conn.cursor() as cur:
        cur.execute(
            """CREATE TABLE IF NOT EXISTS colour_frequencies (
                   colour VARCHAR(50) PRIMARY KEY,
                   frequency INTEGER NOT NULL
               )"""
        )
        for colour, count in freq.items():
            cur.execute(
                """INSERT INTO colour_frequencies (colour, frequency) VALUES (%s, %s)
                   ON CONFLICT (colour) DO UPDATE SET frequency = EXCLUDED.frequency""",
                (colour, count),
            )
    conn.close()
    print("6. Saved %d colours to table colour_frequencies." % len(freq))


# Question 7: recursive search
def recursive_search(numbers, target, index=0):
    """Return the index of target in numbers, or -1 if not found."""
    if index >= len(numbers):
        return -1
    if numbers[index] == target:
        return index
    return recursive_search(numbers, target, index + 1)


def search_demo():
    numbers = [4, 8, 15, 16, 23, 42, 7, 99]
    print("7. Recursive search. List:", numbers)
    try:
        target = int(input("   Enter a number to search for: "))
    except (ValueError, EOFError):
        target = 23
        print("   (no valid input, using %d)" % target)
    pos = recursive_search(numbers, target)
    print("   Found at index %d" % pos if pos != -1 else "   %d is not in the list" % target)


# Question 8: random 4-digit binary number -> base 10
def random_binary_to_decimal():
    binary = "".join(random.choice("01") for _ in range(4))
    print("8. Random binary %s = %d in base 10" % (binary, int(binary, 2)))


# Question 9: sum of first 50 Fibonacci numbers (0, 1, 1, 2, 3, ...)
def sum_fibonacci(n=50):
    a, b, total = 0, 1, 0
    for _ in range(n):
        total += a
        a, b = b, a + b
    return total


if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            html = f.read()
    else:
        html = HTML

    frequencies = analyse(load_colours(html))
    print()
    save_to_postgres(frequencies)
    print()
    search_demo()
    print()
    random_binary_to_decimal()
    print("9. Sum of the first 50 Fibonacci numbers = %d" % sum_fibonacci(50))