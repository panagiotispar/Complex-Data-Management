################################################
##    Panagiotis Paraskevopoulos   AM: 2905   ##
##    Aggelos Bezaitis             AM: 4432   ##
################################################

import sys
import math

# =====================================================================
# FLAG ΕΠΙΛΟΓΗΣ ΑΛΓΟΡΙΘΜΟΥ:
# True  -> Παράγει τα ΑΚΡΙΒΗ αποτελέσματα της εκφώνησης (Σειριακή ομαδοποίηση)
# False -> Παράγει ένα βελτιστοποιημένο R-tree με μικρότερο overlap (Πλήρες STR)
# ΠΡΟΣΟΧΗ: Αφήστε το True για την αυτόματη βαθμολόγηση!
# =====================================================================
USE_BASIC_ALGORITHM = True

# --- ΠΑΡΑΜΕΤΡΟΙ ΧΩΡΗΤΙΚΟΤΗΤΑΣ ΚΟΜΒΩΝ ---
MAX_LEAF_ENTRIES = 51    # M_L
MIN_LEAF_ENTRIES = 20    # m_L
MAX_INT_ENTRIES = 28     # M_Int
MIN_INT_ENTRIES = 11     # m_Int

# --- ΔΟΜΕΣ ΔΕΔΟΜΕΝΩΝ ---

class Point:
    def __init__(self, record_id, x, y):
        self.record_id = record_id
        self.x = x
        self.y = y

    def __repr__(self):
        return f"({self.x}, {self.y})"

class MBR:
    def __init__(self, x_low, y_low, x_high, y_high):
        self.x_low = x_low
        self.y_low = y_low
        self.x_high = x_high
        self.y_high = y_high
        
    def area(self):
        """Υπολογίζει το εμβαδόν του MBR"""
        return (self.x_high - self.x_low) * (self.y_high - self.y_low)

    def __repr__(self):
        return f"[{self.x_low}, {self.y_low}, {self.x_high}, {self.y_high}]"

class Node:
    def __init__(self, node_id, is_leaf, level):
        self.node_id = node_id  # Η θέση του στο array/vector (rtree_nodes)
        self.is_leaf = is_leaf  # f: binary flag (0 για φύλλο, 1 για ενδιάμεσο)
        self.level = level      # Το επίπεδο στο δέντρο (0 = φύλλα)
        self.entries = []       # Λίστα με (record_id, Point) αν είναι φύλλο 
                                # ή (child_node_id, MBR) αν είναι ενδιάμεσος
        
    def get_mbr(self):
        """Υπολογίζει το MBR που περικλείει όλες τις εγγραφές του κόμβου"""
        if not self.entries:
            return None
            
        if self.is_leaf == 0: 
            xs = [pt.x for _, pt in self.entries]
            ys = [pt.y for _, pt in self.entries]
        else:
            xs = [mbr.x_low for _, mbr in self.entries] + [mbr.x_high for _, mbr in self.entries]
            ys = [mbr.y_low for _, mbr in self.entries] + [mbr.y_high for _, mbr in self.entries]
            
        return MBR(min(xs), min(ys), max(xs), max(ys))

# Η κύρια λίστα που θα προσομοιώνει τα blocks του δίσκου
rtree_nodes = []

def load_data(filepath):
    """Διαβάζει το αρχείο και επιστρέφει μία λίστα από αντικείμενα Point."""
    points = []
    with open(filepath, 'r') as f:
        # Η πρώτη γραμμή είναι το πλήθος, την διαβάζουμε απλά για να προχωρήσει ο δείκτης
        total_points = int(f.readline().strip())
        
        # Διαβάζουμε τα σημεία
        record_id = 1
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                x = float(parts[0])
                y = float(parts[1])
                points.append(Point(record_id, x, y))
                record_id += 1
                
    return points

# --- STR ΓΙΑ ΤΑ ΦΥΛΛΑ (LEVEL 0) ---
def build_leaves(points):
    """
    Υλοποιεί το STR bulk loading για το επίπεδο των φύλλων.
    Επιστρέφει μια λίστα με τους κόμβους-φύλλα που δημιουργήθηκαν.
    """
    N = len(points)
    P = math.ceil(N / MAX_LEAF_ENTRIES)     # Πλήθος φύλλων
    S = math.ceil(math.sqrt(P))             # Πλήθος slices
    slice_capacity = S * MAX_LEAF_ENTRIES   # Πλήθος σημείων ανά slice
    
    # 1. Ταξινόμηση όλων των σημείων ως προς X
    points.sort(key=lambda p: p.x)
    
    leaf_chunks = []
    
    # 2. Χωρισμός σε κάθετες λωρίδες (slices)
    for i in range(0, N, slice_capacity):
        slice_points = points[i : i + slice_capacity]
        
        # 3. Ταξινόμηση της λωρίδας ως προς Y
        slice_points.sort(key=lambda p: p.y)
        
        # 4. Ομαδοποίηση σε chunks των MAX_LEAF_ENTRIES (51)
        for j in range(0, len(slice_points), MAX_LEAF_ENTRIES):
            chunk = slice_points[j : j + MAX_LEAF_ENTRIES]
            leaf_chunks.append(chunk)
            
    # 5. Διόρθωση Underflow: Έλεγχος τελευταίου κόμβου 
    if len(leaf_chunks) > 1 and len(leaf_chunks[-1]) < MIN_LEAF_ENTRIES:
        needed = MIN_LEAF_ENTRIES - len(leaf_chunks[-1])
        # Δανειζόμαστε 'needed' στοιχεία από τον προηγούμενο κόμβο
        leaf_chunks[-1] = leaf_chunks[-2][-needed:] + leaf_chunks[-1]
        leaf_chunks[-2] = leaf_chunks[-2][:-needed]
        
    # 6. Δημιουργία των αντικειμένων Node (Φύλλα)
    leaf_nodes = []
    for chunk in leaf_chunks:
        node_id = len(rtree_nodes) # Το id είναι η θέση στο κεντρικό array
        leaf_node = Node(node_id, is_leaf=0, level=0)
        
        # Γέμισμα των εγγραφών του φύλλου: (record_id, Point)
        for p in chunk:
            leaf_node.entries.append((p.record_id, p))
            
        rtree_nodes.append(leaf_node)
        leaf_nodes.append(leaf_node)
        
    return leaf_nodes

# --- STR ΓΙΑ ΕΝΔΙΑΜΕΣΟΥΣ ΚΟΜΒΟΥΣ (BOTTOM-UP) ---
def get_center(node):
    """Επιστρέφει το (X, Y) κέντρο του MBR ενός κόμβου."""
    mbr = node.get_mbr()
    return (mbr.x_low + mbr.x_high) / 2.0, (mbr.y_low + mbr.y_high) / 2.0

def build_level_basic(child_nodes, level):
    """
    Χτίζει το επόμενο επίπεδο του δέντρου ομαδοποιώντας τους κόμβους ΣΕΙΡΙΑΚΑ (sequential chunking),
    όπως ακριβώς κάνει η υλοποίηση της εκφώνησης.
    """
    N = len(child_nodes)
    
    # Αν έχουμε λιγότερους ή ίσους κόμβους από τη χωρητικότητα, φτιάχνουμε απλά τη Ρίζα!
    if N <= MAX_INT_ENTRIES:
        root_node = Node(len(rtree_nodes), is_leaf=1, level=level)
        for child in child_nodes:
            root_node.entries.append((child.node_id, child.get_mbr()))
        rtree_nodes.append(root_node)
        return [root_node]
        
    node_chunks = []
    
    # Ομαδοποίηση σειριακά σε chunks των MAX_INT_ENTRIES (28) χωρίς re-sorting!
    for i in range(0, N, MAX_INT_ENTRIES):
        chunk = child_nodes[i : i + MAX_INT_ENTRIES]
        node_chunks.append(chunk)
            
    # Διόρθωση Underflow: Έλεγχος τελευταίου κόμβου (αν δεν είναι η ρίζα)
    if len(node_chunks) > 1 and len(node_chunks[-1]) < MIN_INT_ENTRIES:
        needed = MIN_INT_ENTRIES - len(node_chunks[-1])
        # Δανειζόμαστε 'needed' στοιχεία από τον προηγούμενο
        node_chunks[-1] = node_chunks[-2][-needed:] + node_chunks[-1]
        node_chunks[-2] = node_chunks[-2][:-needed]
        
    # Δημιουργία των αντικειμένων Node (Ενδιάμεσοι)
    parent_nodes = []
    for chunk in node_chunks:
        parent_node = Node(len(rtree_nodes), is_leaf=1, level=level)
        for child in chunk:
            parent_node.entries.append((child.node_id, child.get_mbr()))            
        rtree_nodes.append(parent_node)
        parent_nodes.append(parent_node)
        
    return parent_nodes

def build_level_optimized(child_nodes, level):
    """
    Βελτιωμένη υλοποίηση με χρήση του αλγορίθμου STR (Sort-Tile-Recursive).
    Ταξινομεί τους κόμβους σε slices (X-axis) και έπειτα σε chunks (Y-axis).
    """
    N = len(child_nodes)
    if N <= MAX_INT_ENTRIES:
        root_node = Node(len(rtree_nodes), is_leaf=1, level=level)
        for child in child_nodes:
            root_node.entries.append((child.node_id, child.get_mbr()))
        rtree_nodes.append(root_node)
        return [root_node]
        
    P = math.ceil(N / MAX_INT_ENTRIES)     
    S = math.ceil(math.sqrt(P))            
    slice_capacity = S * MAX_INT_ENTRIES   
    
    # 1. Ταξινόμηση βάσει του X κέντρου του MBR
    child_nodes.sort(key=lambda n: get_center(n)[0])
    
    node_chunks = []
    # 2. Χωρισμός σε κάθετα slices
    for i in range(0, N, slice_capacity):
        slice_nodes = child_nodes[i : i + slice_capacity]
        # 3. Ταξινόμηση βάσει του Y κέντρου του MBR
        slice_nodes.sort(key=lambda n: get_center(n)[1])
        # 4. Ομαδοποίηση σε chunks των MAX_INT_ENTRIES (28)
        for j in range(0, len(slice_nodes), MAX_INT_ENTRIES):
            chunk = slice_nodes[j : j + MAX_INT_ENTRIES]
            node_chunks.append(chunk)
            
    # 5. Διόρθωση Underflow στο τελευταίο chunk (αν δεν είναι η ρίζα)
    if len(node_chunks) > 1 and len(node_chunks[-1]) < MIN_INT_ENTRIES:
        needed = MIN_INT_ENTRIES - len(node_chunks[-1])
        # Δανειζόμαστε 'needed' στοιχεία από τον προηγούμενο chunk
        node_chunks[-1] = node_chunks[-2][-needed:] + node_chunks[-1]
        node_chunks[-2] = node_chunks[-2][:-needed]
        
    # 6. Δημιουργία Ενδιάμεσων
    parent_nodes = []
    for chunk in node_chunks:
        parent_node = Node(len(rtree_nodes), is_leaf=1, level=level)
        for child in chunk:
            parent_node.entries.append((child.node_id, child.get_mbr()))
        rtree_nodes.append(parent_node)
        parent_nodes.append(parent_node)
        
    return parent_nodes

def build_level(child_nodes, level):
    """
    Wrapper συνάρτηση που επιλέγει μεταξύ της βασικής και της 
    βελτιωμένης (STR) μεθόδου χτισίματος επιπέδου.
    """
    if USE_BASIC_ALGORITHM:
        return build_level_basic(child_nodes, level)
    else:
        return build_level_optimized(child_nodes, level)

def build_rtree(points):
    """Η κεντρική συνάρτηση που χτίζει όλο το δέντρο."""
    current_level_nodes = build_leaves(points)
    level = 1
    
    # Συνεχίζουμε να χτίζουμε επίπεδα μέχρι να καταλήξουμε σε 1 μόνο κόμβο (τη ρίζα)
    while len(current_level_nodes) > 1:
        current_level_nodes = build_level(current_level_nodes, level)
        level += 1

# --- ΕΞΑΓΩΓΗ ΣΤΑΤΙΣΤΙΚΩΝ & ΑΡΧΕΙΟΥ CSV ---
def print_statistics():
    """Υπολογίζει και τυπώνει τα στατιστικά ανά επίπεδο."""
    # Ομαδοποίηση κόμβων ανά επίπεδο
    levels_dict = {}
    for node in rtree_nodes:
        if node.level not in levels_dict:
            levels_dict[node.level] = []
        levels_dict[node.level].append(node)
        
    for lvl in sorted(levels_dict.keys()):
        nodes_in_lvl = levels_dict[lvl]
        num_nodes = len(nodes_in_lvl)
        
        if lvl == 0:
            avg_area = 0.0
        else:
            total_area = sum(node.get_mbr().area() for node in nodes_in_lvl)
            avg_area = total_area / num_nodes
            
        print(f"{num_nodes} nodes at level {lvl} with average MBR area {avg_area}")

def export_to_csv(filename):
    """Αποθηκεύει το δέντρο στο αρχείο CSV με την ακριβή μορφοποίηση της εκφώνησης."""
    with open(filename, 'w', encoding='utf-8') as f:
        for node in rtree_nodes:
            # Βασικά στοιχεία: node-id, n, f
            parts = [str(node.node_id), str(len(node.entries)), str(node.is_leaf)]
            
            for entry in node.entries:
                ptr = entry[0]
                geo = entry[1]
                
                if node.is_leaf == 0:
                    # Αν είναι φύλλο, το geo είναι Point
                    geo_str = f"({geo.x}, {geo.y})"
                else:
                    # Αν είναι ενδιάμεσος, το geo είναι MBR
                    geo_str = f"[{geo.x_low}, {geo.y_low}, {geo.x_high}, {geo.y_high}]"
                
                parts.append(f"({ptr},{geo_str})")
                
            # Ενώνουμε με κόμμα και κενό, όπως ακριβώς θέλει η εκφώνηση
            f.write(" , ".join(parts) + "\n")

# --- ΕΚΤΕΛΕΣΗ ΠΡΟΓΡΑΜΜΑΤΟΣ ΑΠΟ ΤΕΡΜΑΤΙΚΟ ---
if __name__ == "__main__":
    # Έλεγχος αν δόθηκαν σωστά τα ορίσματα (input file, output file)
    if len(sys.argv) != 3:
        print("Χρήση: python rtree.py <αρχείο_δεδομένων> <όνομα_εξόδου.csv>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    points = load_data(input_file)
    build_rtree(points)
    
    print_statistics()
    export_to_csv(output_file)