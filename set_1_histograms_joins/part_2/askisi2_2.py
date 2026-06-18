################################################
##    Παναγιώτης Παρασκευόπουλος   ΑΜ: 2905   ##
##    Άγγελος Μπεζαΐτης            ΑΜ: 4432   ##
################################################

"""
Διαχείριση Σύνθετων Δεδομένων - Assignment 2
Semi-joins, Sort-Merge Joins, and 3-way Pipelined Joins
"""

import sys

# ============================================================================
# PART 2: Real Data Application (airports.dat and routes.dat)
# ============================================================================

def read_airports(filepath):
    airport_records = []

    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            split_line = line.strip().split(',')
            airport_records.append(tuple(split_line))
    return airport_records

def read_routes(filepath):
    route_records = []
    
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            split_line = line.strip().split(',')
            route_records.append(tuple(split_line))
    return route_records


# [ ] TODO 2.5: Υλοποίηση παραλλαγής του sort-merge join (Semi-join)
# για να τυπώσεις ολόκληρη την πλειάδα των αεροδρομίων (από το airports.dat)
# που ικανοποιούν τη συνθήκη.
# Υπενθύμιση: το airports.dat είναι ήδη ταξινομημένο ως προς το 1ο πεδίο
# (index 0).
def semijoin_airports_with_routes(airports, filtered_routes):
    """
    Semi-join to find airports that have routes using the specified aircraft.
    Returns complete airport tuples.
    
    airports: List of airport tuples (already sorted by ID at index 0)
    filtered_routes: List of filtered and sorted route tuples
    
    Returns:
        List of complete airport tuples that have matching routes
    """
    i = 0
    j = 0
    match_count = 0
    result = []
    
    while i < len(airports) and j < len(filtered_routes):
        route_dest_id = int(filtered_routes[j][5])  # Destination airport ID in filtered_routes
        airport_id = int(airports[i][0])    # Airport ID in airports
        
        if airport_id == route_dest_id:
            result.append(airports[i])  # Add the complete airport tuple to the result
            match_count += 1
            i += 1  # Move to the next airport
        elif airport_id < route_dest_id:
            i += 1  # Move to the next airport
        else:
            j += 1  # Move to the next route
        
    print(f"Total matching airports found: {match_count}")
    return result


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("Usage: python onoma_arxeiou.py <aircraft_type>")
        print("Example: python onoma_arxeiou.py 737")
        sys.exit(1) # Κλείσιμο του προγράμματος με κωδικό σφάλματος
        
    aircraft_type = sys.argv[1]
    print(f"\nΑναζήτηση αεροδρομίων για τύπο αεροσκάφους: {aircraft_type}")
    
    routes = read_routes("routes.dat")
    airports = read_airports("airports.dat")
    
    # Ελέγχουμε αν ο τύπος αεροσκάφους υπάρχει στη λίστα των αεροσκαφών αυτής της πτήσης
    filtered_routes = [
        route for route in routes 
        if aircraft_type in route[-1].split() and route[5].isdigit()
    ]
    filtered_routes.sort(key=lambda x: int(x[5]) if x[5].isdigit() else 0)  # Ταξινόμηση με βάση το 6ο πεδίο (index 5)
    
    matching_airports = semijoin_airports_with_routes(airports, filtered_routes)
    
    # Εκτύπωση αποτελεσμάτων (τα πρώτα 10 για να μη γεμίσει η οθόνη)
    print("\nΕνδεικτικά αποτελέσματα (πρώτα 5):")
    for a in matching_airports[:5]:
        print(a)
