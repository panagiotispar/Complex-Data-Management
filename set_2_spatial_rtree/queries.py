################################################
##    Panagiotis Paraskevopoulos   AM: 2905   ##
##    Aggelos Bezaitis             AM: 4432   ##
################################################

import sys
import ast
import math
import heapq

# 1. ΒΑΣΙΚΕΣ ΔΟΜΕΣ (Όπως και στο Μέρος 1)
class Point:
    def __init__(self, record_id, x, y):
        self.record_id = record_id
        self.x = x
        self.y = y

class MBR:
    def __init__(self, x_low, y_low, x_high, y_high):
        self.x_low = x_low
        self.y_low = y_low
        self.x_high = x_high
        self.y_high = y_high

class Node:
    def __init__(self, node_id, is_leaf):
        self.node_id = node_id
        self.is_leaf = is_leaf
        self.entries = []

# Η κεντρική δομή που θα κρατάει το δέντρο μας
rtree_nodes = []

# 2. ΦΟΡΤΩΣΗ ΤΟΥ ΔΕΝΤΡΟΥ ΑΠΟ ΤΟ CSV
def load_rtree(filename):
    """Διαβάζει το rtree.csv και ανακατασκευάζει το δέντρο στη μνήμη."""
    global rtree_nodes
    rtree_nodes = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # Αρχικοποιούμε τη λίστα με None για να βάλουμε τους κόμβους στη σωστή θέση
    rtree_nodes = [None] * len(lines)
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # Με το maxsplit=3 κόβουμε σωστά τα 3 πρώτα νούμερα
        parts = line.split(" , ", 3) 
        node_id = int(parts[0])
        n = int(parts[1])
        f_flag = int(parts[2])
        
        node = Node(node_id, f_flag)
        
        # Η υπόλοιπη γραμμή περιέχει τις εγγραφές
        entries_str = parts[3] if len(parts) > 3 else ""
        if entries_str:
            # Τυλίγουμε το string σε αγκύλες για να το διαβάσει σαν λίστα από tuples
            clean_entries = entries_str.replace(" , ", ",")
            entries_data = ast.literal_eval(f"[{clean_entries}]")
            
            for entry in entries_data:
                ptr = entry[0]
                geo_data = entry[1]
                
                if f_flag == 0:
                    # geo_data είναι tuple (x, y)
                    geo = Point(ptr, geo_data[0], geo_data[1])
                else:
                    # geo_data είναι list [x_low, y_low, x_high, y_high]
                    geo = MBR(geo_data[0], geo_data[1], geo_data[2], geo_data[3])
                node.entries.append((ptr, geo))
        rtree_nodes[node_id] = node
    return len(rtree_nodes) - 1

# 3. ΥΛΟΠΟΙΗΣΗ WINDOW RANGE QUERIES
def check_mbr_intersection(mbr1, mbr2):
    """Βοηθητική 1: Ελέγχει αν δύο MBRs επικαλύπτονται."""
    if (mbr1.x_high < mbr2.x_low or mbr1.x_low > mbr2.x_high or
        mbr1.y_high < mbr2.y_low or mbr1.y_low > mbr2.y_high):
        return False
    return True

def check_point_in_mbr(point, mbr):
    """Βοηθητική 2: Ελέγχει αν ένα σημείο βρίσκεται μέσα σε ένα MBR."""
    return (mbr.x_low <= point.x <= mbr.x_high and 
            mbr.y_low <= point.y <= mbr.y_high)

def window_range_query(root_id, W):
    """Εκτελεί αναζήτηση παραθύρου και επιστρέφει λίστα με τα record_ids."""
    results = []
    nodes_to_visit = [root_id]
    
    while nodes_to_visit:
        current_node_id = nodes_to_visit.pop(0) # Παίρνουμε τον επόμενο κόμβο από την "ουρά"
        current_node = rtree_nodes[current_node_id]
        
        if current_node.is_leaf == 0:
            # Αν είναι φύλλο, ελέγχουμε τα σημεία
            for record_id, point in current_node.entries:
                if check_point_in_mbr(point, W):
                    results.append(record_id)
        else:
            # Αν είναι ενδιάμεσος, ελέγχουμε τα MBRs των παιδιών του
            for child_id, child_mbr in current_node.entries:
                if check_mbr_intersection(child_mbr, W):
                    nodes_to_visit.append(child_id) # Το βάζουμε στην "ουρά" για να το επισκεφτούμε
                    
    return results

# --- ΥΛΟΠΟΙΗΣΗ DISTANCE RANGE QUERIES ---
def point_distance(p1, p2):
    """Βοηθητική 1: Υπολογίζει την Ευκλείδεια απόσταση μεταξύ δύο σημείων."""
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

def min_dist_to_mbr(point, mbr):
    """Βοηθητική 2: Υπολογίζει την ελάχιστη απόσταση (MinDist) ενός σημείου από ένα MBR."""
    if point.x < mbr.x_low:
        dx = mbr.x_low - point.x
    elif point.x > mbr.x_high:
        dx = point.x - mbr.x_high
    else:
        dx = 0
        
    if point.y < mbr.y_low:
        dy = mbr.y_low - point.y
    elif point.y > mbr.y_high:
        dy = point.y - mbr.y_high
    else:
        dy = 0
        
    return math.sqrt(dx*dx + dy*dy)

def distance_range_query(root_id, q_point, radius):
    """Εκτελεί αναζήτηση ακτίνας και επιστρέφει λίστα με τα record_ids."""
    results = []
    nodes_to_visit = [root_id]
    
    while nodes_to_visit:
        current_node_id = nodes_to_visit.pop(0)
        current_node = rtree_nodes[current_node_id]
        
        if current_node.is_leaf == 0:
            # Φύλλο: Ελέγχουμε την ακριβή απόσταση κάθε σημείου
            for record_id, point in current_node.entries:
                if point_distance(q_point, point) <= radius:
                    results.append(record_id)
        else:
            # Ενδιάμεσος κόμβος: Ελέγχουμε αν το MBR του "τέμνει" τον κύκλο αναζήτησης
            for child_id, child_mbr in current_node.entries:
                if min_dist_to_mbr(q_point, child_mbr) <= radius:
                    nodes_to_visit.append(child_id)
                    
    return results

# --- ΥΛΟΠΟΙΗΣΗ k-NN QUERIES ---
def knn_query(root_id, q_point, k):
    """Εκτελεί k-NN αναζήτηση χρησιμοποιώντας Priority Queue (Min-Heap)."""
    # Στην ουρά βάζουμε tuples της μορφής: (απόσταση, τύπος_στοιχείου, id)
    # τύπος_στοιχείου: 0 για MBR (κόμβος), 1 για Σημείο (εστιατόριο)
    # Αυτό βοηθάει αν οι αποστάσεις είναι ίσες, να συγκρίνονται τα επόμενα πεδία με ασφάλεια.
    pq = []
    heapq.heappush(pq, (0.0, 0, root_id))
    
    results = []
    
    while pq and len(results) < k:
        dist, item_type, item_id = heapq.heappop(pq)
        
        if item_type == 1:
            # Βγάλαμε σημείο (εστιατόριο)! Είναι σίγουρα το επόμενο κοντινότερο.
            results.append(item_id)
        else:
            # Βγάλαμε κόμβο (MBR). Τον "ανοίγουμε" (expand).
            node = rtree_nodes[item_id]
            if node.is_leaf == 0:
                # Αν είναι φύλλο, βάζουμε στην ουρά τις ακριβείς αποστάσεις των εστιατορίων
                for ptr, point in node.entries:
                    d = point_distance(q_point, point)
                    heapq.heappush(pq, (d, 1, ptr)) # 1 = Σημείο
            else:
                # Αν είναι ενδιάμεσος, βάζουμε στην ουρά τα παιδιά-MBRs
                for child_id, child_mbr in node.entries:
                    d = min_dist_to_mbr(q_point, child_mbr)
                    heapq.heappush(pq, (d, 0, child_id)) # 0 = Κόμβος
                    
    return results

# --- ΕΚΤΕΛΕΣΗ ΚΑΙ ΑΞΙΟΛΟΓΗΣΗ ΓΙΑ ΟΛΑ ΤΑ QUERIES ---
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Χρήση: python queries.py <rtree.csv> <αρχείο_ερωτημάτων.txt> [k_για_knn]")
        sys.exit(1)
        
    rtree_file = sys.argv[1]
    queries_file = sys.argv[2]
    
    # Διαβάζουμε το k (Αν το query είναι kNN). Default k=10
    k_value = int(sys.argv[3]) if len(sys.argv) > 3 else 10 
    
    root_id = load_rtree(rtree_file)
    
    with open(queries_file, 'r') as f:
        for q_index, line in enumerate(f):
            parts = line.strip().split()
            if not parts: continue
            
            if len(parts) == 4:
                # Window Range Query
                W = MBR(float(parts[0]), float(parts[1]), float(parts[2]), float(parts[3]))
                res = window_range_query(root_id, W)
                
            elif len(parts) == 3:
                # Distance Range Query
                q_point = Point(-1, float(parts[0]), float(parts[1]))
                radius = float(parts[2])
                res = distance_range_query(root_id, q_point, radius)
                
            elif len(parts) == 2:
                # k-NN Query
                q_point = Point(-1, float(parts[0]), float(parts[1]))
                res = knn_query(root_id, q_point, k_value)
                
            res_str = ",".join(map(str, res))
            
            # ΔΙΑΧΩΡΙΣΜΟΣ ΕΚΤΥΠΩΣΗΣ ΓΙΑ ΝΑ ΜΑΤΣΑΡΕΙ ΤΗΝ ΕΚΦΩΝΗΣΗ
            if len(parts) == 2: # Αν ήταν k-NN
                print(f"{q_index}: {res_str}")
            else: # Αν ήταν Window ή Distance
                print(f"{q_index} ({len(res)}): {res_str}")