# See http://norvig.com/sudoku.html

def cross(A, B):
    "Cross production of elements in A and elements in B."
    return [a+b for a in A for b in B]

digits = '123456789'
rows   = 'ABCDEFGHI'
cols   = digits
squares = cross(rows, cols)

unitlist = ([cross(rows, c) for c in cols] +                                                 # column units
            [cross(r, cols) for r in rows] +                                                 # row units
            [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]) # box units

units = dict((s, [u for u in unitlist if s in u])
             for s in squares)

peers = dict((s, set(sum(units[s], []))-set([s]))   # Note: sum(listOfLists, []) flattens a listOfLists
             for s in squares)

# Initial state
# This is just a string. Digits represent given values.
# '0' or '.' represent unknowns. All other chars ignored
grid = """
4 . . |. . . |8 . 5 
. 3 . |. . . |. . . 
. . . |7 . . |. . . 
------+------+------
. 2 . |. . . |. 6 . 
. . . |. 8 . |4 . . 
. . . |. 1 . |. . . 
------+------+------
. . . |6 . 3 |. 7 . 
5 . . |2 . . |. . . 
1 . 4 |. . . |. . . 
"""

# Current state
# We use a dict {square: digits}, where digits is either
#   a) a single digit (value given or found)
#   b) a string of digits (i.e. '368')
# So this dict might look like {'A1': '7', 'C7': '123456789', ...}

def parse_grid(grid):
    """convert grid to a dict of possible values, {square: digits}, or
    return False if a contradiction detected"""
    ## To start, every square can be any digit; then assign values from the grid.
    values = dict((s, digits) for s in squares)
    ## Now, assigns the initial values
    for s,d in grid_values(grid).items():
        if d in digits and not assign(values, s, d):
            return False ## (Fail if we can't assign d to square s.')
    return values
    
def grid_values(grid):
    "Convert grid into a dict of {square: char} with '0 or '.' for empties."
    chars = [c for c in grid if c in digits or c in '0.'] # remove extra chars
    assert len(chars) == 81
    return dict(zip(squares, chars))

def assign(values, s, d):
    """Eliminate all the other values (except d) from values[s] and propagate.
    Return values, except return False if a contraciction is detected."""
    other_values = values[s].replace(d, '') # possible values for s, but excluding d
    if all(eliminate(values, s, d2) for d2 in other_values):
        return values
    else:
        return False
    
def eliminate(values, s, d):
    """Eliminate d from values[s]; propagate when values or places <= 2.
    Return values, except return False if a contradiction is detected."""
    if d not in values[s]:
        return values ## Already eliminated
    values[s] = values[s].replace(d, '')
    ## (1) If a square s is reduced to one value d2, then eliminate d2 from the peers
    if len(values[s]) == 0:
        return False ## Contradiction: removed last value
    elif len(values[s]) == 1:
        d2 = values[s]
        if not all(eliminate(values, s2, d2) for s2 in peers[s]):
            return False
    ## (2) If a unit u is reduced to only one place for a value d, then put it there.
    for u in units[s]:
        dplaces = [s for s in u if d in values[s]]
        if len(dplaces) == 0:
            return False ## Contradiction: no place for this value
        elif len(dplaces) == 1:
            # d can only be in one place in unit; assign it there
            if not assign(values, dplaces[0], d):
                return False
    return values

def display(values):
    "Display these balues as 2-D grid."
    width = 1+max(len(values[s]) for s in squares)  ## i.e. this will be 2 for a completed puzzle, larger otherwise
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:        
        print ''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols)
        if r in 'CF': print line
    print

def test():
    "A set of unit tests."
    assert len(squares) == 81
    assert len(unitlist) == 27
    assert all(len(units[s]) == 3 for s in squares)
    assert all(len(peers[s]) == 20 for s in squares)
    assert units['C2'] == [['A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2', 'I2'],
                           ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9'],
                           ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']]
    assert peers['C2'] == set(['A2', 'B2', 'D2', 'E2', 'F2', 'G2', 'H2', 'I2',
                               'C1', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9',
                               'A1', 'A3', 'B1', 'B3'])
    print 'All tests pass.'

# Here's an easy puzzle:
# It can be solved by strategies (1) abd (2) alone
# grid1 = '003020600900305001001806400008102900700000008006708200002609500800203009005010300'
# display(parse_grid(grid1))

# Here's a harder puzzle:
# (1) and (2) alone are insufficient to solve it
grid2 = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'
# display(parse_grid(grid2))

def solve(grid):
    return search(parse_grid(grid))
    
def search(values):
    "Using depth-first search and propagation, try all possible values."
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in squares):
        return values ## Solved!
    ## Choose the unfilled square s with the fewest possibilities
    n,s = min((len(values[s]), s) for s in squares if len(values[s]) > 1)
    return some(search(assign(values.copy(), s, d))
                for d in values[s])

def some(seq):
    "Return some element of seq that is true."
    for e in seq:
      if e: return e;
    return False

# Now we can solve grid2
display(solve(grid2))

    

