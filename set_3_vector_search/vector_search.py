################################################
##    Panagiotis Paraskevopoulos   AM: 2905   ##
##    Aggelos Bezaitis             AM: 4432   ##
################################################

import math
import sys
import bisect
import time
import heapq

###########################################################
## Μέρος 1: Φόρτωση δεδομένων και υπολογισμός των pivots ##
###########################################################

def load_data(filepath):
    data = [] 
    with open(filepath, 'r') as file:
        for line in file:
            vector = tuple(float(x) for x in line.strip().split())
            if vector:
                data.append(vector)
    return data

def euclidean_distance(vec1, vec2):
    return math.dist(vec1, vec2)

def select_pivots(D, numpivots):
    """
    Επιλέγει τα pivots βασισμένο στην απόσταση από το seed και επιστρέφει
    τα IDs των pivots και τον πίνακα αποστάσεων όλων των αντικειμένων από αυτά.
    """
    num_objects = len(D)
    pivots = []
    
    # Αρχικοποίηση 2D πίνακα για τις αποστάσεις: distances[i][j]
    # Θα έχει μέγεθος (πλήθος αντικειμένων) x (πλήθος pivots)
    distances = [[0.0] * numpivots for _ in range(num_objects)]
    
    # 1. Εύρεση 1ου pivot (πιο απομακρυσμένο από το seed)
    seed_id = 0
    max_distance = -1
    p0 = -1
    for i in range(num_objects):
        dist = euclidean_distance(D[seed_id], D[i])
        if dist > max_distance:
            max_distance = dist
            p0 = i
    
    pivots.append(p0)
    
    # Υπολογισμός αποστάσεων όλων των αντικειμένων από το p0
    for i in range(num_objects):
        distances[i][0] = euclidean_distance(D[p0], D[i])
    
    # 2. Εύρεση των υπόλοιπων pivots (από το 2ο έως το numpivots-οστό)
    for k in range(1, numpivots):
        max_sum_dist = -1
        pk = -1
        
        for i in range(num_objects):
            # Υπολογίζουμε το άθροισμα των αποστάσεων του αντικειμένου i
            # από όλα τα ΗΔΗ επιλεγμένα pivots
            sum_dist = 0
            for j in range(k):
                sum_dist += distances[i][j]
            
            if sum_dist > max_sum_dist:
                max_sum_dist = sum_dist
                pk = i
        pivots.append(pk)
        
        # Υπολογισμός αποστάσεων όλων των αντικειμένων από το νέο pivot pk
        for i in range(num_objects):
            distances[i][k] = euclidean_distance(D[i], D[pk])
    return pivots, distances

################################
## Μέρος 2: Μέθοδος iDistance ##
################################

def build_idistance_index(pivots, distances):
    num_objects = len(distances)
    numpivots = len(pivots)
    
    # Πίνακας για να κρατάμε σε ποιο pivot (index) ανήκει το κάθε αντικείμενο
    closest_pivot_idx = [-1] * num_objects
    
    # maxd_p[i] θα κρατάει τη μέγιστη απόσταση για το pivot i
    maxd_p = [0.0] * numpivots
    
    # 1 & 2. Εύρεση κοντινότερου pivot και υπολογισμός των maxd(p)
    for i in range(num_objects):
        # H λίστα των αποστάσεων του αντικειμένου i από όλα τα pivots
        dist_list = distances[i] 
        
        # Βρίσκουμε κατευθείαν την ελάχιστη απόσταση και το index της (δηλ. το pivot)
        min_dist = min(dist_list)
        closest_p = dist_list.index(min_dist)
        
        closest_pivot_idx[i] = closest_p
        
        # Ενημέρωση του maxd(p)
        if min_dist > maxd_p[closest_p]:
            maxd_p[closest_p] = min_dist
            
    # 3. Υπολογισμός του συνολικού maxd
    maxd = max(maxd_p)
    
    # 4. Δημιουργία του array με τα ζεύγη (iDist, oid)
    idistance_array = []
    for i in range(num_objects):
        p_idx = closest_pivot_idx[i]          # Το index (0 έως numpivots-1) του pivot
        dist_to_p = distances[i][p_idx]       # Η απόσταση dist(o, pi)
        
        # Υπολογισμός iDistance σύμφωνα με τον τύπο της εκφώνησης: i * maxd + dist(o, pi)
        iDist = p_idx * maxd + dist_to_p
        
        idistance_array.append((iDist, i))    # Εδώ i είναι το object-id (oid)
        
    # 5. Ταξινόμηση (sort) του array με βάση την τιμή iDist
    idistance_array.sort(key=lambda x: x[0])
    
    return idistance_array, maxd_p, maxd, closest_pivot_idx

#######################################################################
## Μέρος 3: Ερωτήματα ομοιότητας εύρους (Range similarity queries)   ##
#######################################################################

def range_query_naive(D, q, epsilon):
    result = []
    dist_comps = 0
    
    for i, o in enumerate(D):
        dist = euclidean_distance(o, q)
        dist_comps += 1
        if dist <= epsilon:
            result.append(i)  # Προσθέτουμε το object-id (index) στη λίστα αποτελεσμάτων
    return result, dist_comps

def range_query_pivot(D, q, epsilon, pivots, distances):
    result = []
    dist_comps = 0
    
    # Υπολογισμός απόστασης του query q από όλα τα pivots (μία φορά)
    dist_q_p = [euclidean_distance(q, D[p]) for p in pivots]
    dist_comps += len(pivots)  # Μετράμε τις αποστάσεις από τα pivots
    
    for i, o in enumerate(D):
        pruned = False
        
        # Έλεγχος Triangle Inequality για κάθε pivot
        for j in range(len(pivots)):
            if abs(distances[i][j] - dist_q_p[j]) > epsilon:
                pruned = True
                break
        
        if not pruned:
            dist = euclidean_distance(o, q)
            dist_comps += 1
            if dist <= epsilon:
                result.append(i)  # Προσθέτουμε το object-id (index) στη λίστα αποτελεσμάτων

    return result, dist_comps

def range_query_idistance(D, q, epsilon, pivots, idistance_array, maxd, maxd_p, closest_pivot_idx):
    result = []
    dist_comps = 0
    
    # Υπολογισμός απόστασης του query q από όλα τα pivots (μία φορά)
    dist_q_p = [euclidean_distance(q, D[p]) for p in pivots]
    dist_comps += len(pivots)  # Μετράμε τις αποστάσεις από τα pivots
    
    # Εξαγωγή μόνο των τιμών iDist για να δουλέψει η bisect (binary search)
    iDist_keys = [item[0] for item in idistance_array]

    for i in range(len(pivots)):
        # Pruning ολόκληρου του partition i (όπως λέει η εκφώνηση)
        if dist_q_p[i] - maxd_p[i] > epsilon:
            continue
    
        # Υπολογισμός ορίων αναζήτησης με βάση την τριγωνική ανισότητα
        lower_bound = i * maxd + dist_q_p[i] - epsilon
        upper_bound = i * maxd + dist_q_p[i] + epsilon
                    
        # Binary search απευθείας στο lower_bound
        start_idx = bisect.bisect_left(iDist_keys, lower_bound)
        
        # Scan (γραμμική σάρωση) από το start_idx και μετά
        for idx in range(start_idx, len(idistance_array)):
            iDist, oid = idistance_array[idx]
            
            # Αν ξεπεράσουμε το άνω όριο αναζήτησης, σταματάμε τη σάρωση
            if iDist > upper_bound:
                break

            # ΣΙΓΟΥΡΟΣ ΕΛΕΓΧΟΣ 100%: Ανήκει στο partition i;
            if closest_pivot_idx[oid] != i:
                continue
            
            # Υπολογισμός ακριβούς απόστασης για τα υποψήφια αντικείμενα
            dist = euclidean_distance(D[oid], q)
            dist_comps += 1
            if dist <= epsilon:
                result.append(oid)  # Προσθέτουμε το object-id (index) στη λίστα αποτελεσμάτων
    
    return result, dist_comps
            
#################################################################
## Μέρος 4: Ερωτήματα ομοιότητας kNN (kNN similarity queries)  ##
#################################################################

def knn_query_naive(D, q, k):
    heap = []
    dist_comps = 0
    
    for i, o in enumerate(D):
        dist = euclidean_distance(o, q)
        dist_comps += 1
        
        if len(heap) < k:
            heapq.heappush(heap, (-dist, i))  # Αποθηκεύουμε αρνητική απόσταση για max-heap
        else:
            if dist < -heap[0][0]:  # Αν η τρέχουσα απόσταση είναι μικρότερη από τη μέγιστη στο heap
                heapq.heappushpop(heap, (-dist, i))
    
    result = [(-h[0], h[1]) for h in heap]  # Μετατροπή σε (distance, object-id)
    result.sort(key=lambda x: x[0])  # Ταξινόμηση κατά απόσταση
    return result, dist_comps

def knn_query_pivot(D, q, k, pivots, distances):
    heap = []
    dist_comps = 0
    
    # Υπολογισμός απόστασης του query q από όλα τα pivots (μία φορά)
    dist_q_p = [euclidean_distance(q, D[p]) for p in pivots]
    dist_comps += len(pivots)  # Μετράμε τις αποστάσεις από τα pivots
    
    for i, o in enumerate(D):
        if len(heap) < k:
            dist = euclidean_distance(o, q)
            dist_comps += 1
            heapq.heappush(heap, (-dist, i))  # Αποθηκεύουμε αρνητική απόσταση για max-heap
        else:
            epsilon = -heap[0][0]  # Η μέγιστη απόσταση στο heap
            pruned = False
            
            for j in range(len(pivots)):
                if abs(distances[i][j] - dist_q_p[j]) > epsilon:
                    pruned = True
                    break
            
            if not pruned:
                dist = euclidean_distance(o, q)
                dist_comps += 1
                if dist < epsilon:
                    heapq.heappushpop(heap, (-dist, i))
    
    result = [(-h[0], h[1]) for h in heap]  # Μετατροπή σε (distance, object-id)
    result.sort(key=lambda x: x[0])  # Ταξινόμηση
    return result, dist_comps
    

def knn_query_idistance(D, q, k, pivots, idistance_array, maxd, maxd_p, closest_pivot_idx):
    heap = []
    dist_comps = 0
    
    # Υπολογισμός απόστασης του query q από όλα τα pivots (μία φορά)
    dist_q_p = [euclidean_distance(q, D[p]) for p in pivots]
    dist_comps += len(pivots)
    
    closest_p = dist_q_p.index(min(dist_q_p))
    iDist_keys = [item[0] for item in idistance_array]
    
    # --- 1. Επεξεργασία του κοντινότερου partition πρώτα ---
    start_idx = bisect.bisect_left(iDist_keys, closest_p * maxd)
    for idx in range(start_idx, len(idistance_array)):
        iDist, oid = idistance_array[idx]
        
        # Αν ξεπεράσαμε το άνω όριο του partition, σταματάμε
        if iDist > closest_p * maxd + maxd:
            break

        if closest_pivot_idx[oid] != closest_p:
            continue
            
        dist = euclidean_distance(D[oid], q)
        dist_comps += 1
        
        if len(heap) < k:
            heapq.heappush(heap, (-dist, oid))
        else:
            if dist < -heap[0][0]:
                heapq.heappushpop(heap, (-dist, oid))
                
    # --- 2. Επεξεργασία των υπόλοιπων pivots ---
    for i in range(len(pivots)):
        if i == closest_p:
            continue
            
        # Αν ΔΕΝ έχουμε μαζέψει ακόμα k στοιχεία, δεν μπορούμε να κάνουμε prune (ε = άπειρο)
        epsilon = -heap[0][0] if len(heap) == k else float('inf')
        
        # Pruning ολόκληρου του partition i
        if dist_q_p[i] - maxd_p[i] > epsilon:
            continue
            
        # Τα όρια αναζήτησης με βάση την τριγωνική ανισότητα
        lower_bound = i * maxd + dist_q_p[i] - epsilon
        upper_bound = i * maxd + dist_q_p[i] + epsilon
                    
        start_idx = bisect.bisect_left(iDist_keys, lower_bound)
        for idx in range(start_idx, len(idistance_array)):
            iDist, oid = idistance_array[idx]
            
            # Έλεγχος με το στατικό upper_bound
            if iDist > upper_bound:
                break

            # Skip αν βρεθούμε σε άλλο partition
            if closest_pivot_idx[oid] != i:
                continue
                
            dist = euclidean_distance(D[oid], q)
            dist_comps += 1
            
            if len(heap) < k:
                heapq.heappush(heap, (-dist, oid))
            else:
                if dist < -heap[0][0]:
                    heapq.heappushpop(heap, (-dist, oid))
                
    result = [(-h[0], h[1]) for h in heap]
    result.sort(key=lambda x: x[0])
    return result, dist_comps

# ==========================================
# ΚΥΡΙΩΣ ΠΡΟΓΡΑΜΜΑ (MAIN)
# ==========================================
if __name__ == "__main__":
    # Προεπιλεγμένες τιμές
    numpivots = 5
    epsilon = 0.2
    k = 5
    
    # Λήψη command-line arguments
    if len(sys.argv) > 1:
        try: numpivots = int(sys.argv[1])
        except ValueError: pass
    if len(sys.argv) > 2:
        try: epsilon = float(sys.argv[2])
        except ValueError: pass
    if len(sys.argv) > 3:
        try: k = int(sys.argv[3])
        except ValueError: pass
            
    print(f"Execution for numpivots = {numpivots}, epsilon = {epsilon}, k = {k}")
    
    dataset = load_data('data10K10.txt')
    queries = load_data('queries10.txt')
    
    pivots, distances = select_pivots(dataset, numpivots)
    print(f"pivots: {pivots}")
    idistance_array, maxd_p, maxd, closest_pivot_idx = build_idistance_index(pivots, distances)    
    # --- ΜΕΡΟΣ 3: ΑΞΙΟΛΟΓΗΣΗ RANGE QUERIES ---
    print("\n--- Range Query Results (Meros 3) ---")
    total_comps_naive = 0; total_time_naive = 0.0
    total_comps_pivot = 0; total_time_pivot = 0.0
    total_comps_idist = 0; total_time_idist = 0.0
    
    num_queries = len(queries)
    
    for q in queries:
        start_time = time.time()
        _, comps = range_query_naive(dataset, q, epsilon)
        total_time_naive += time.time() - start_time
        total_comps_naive += comps
        
        start_time = time.time()
        _, comps = range_query_pivot(dataset, q, epsilon, pivots, distances)
        total_time_pivot += time.time() - start_time
        total_comps_pivot += comps
        
        start_time = time.time()
        _, comps = range_query_idistance(dataset, q, epsilon, pivots, idistance_array, maxd, maxd_p, closest_pivot_idx)
        total_time_idist += time.time() - start_time
        total_comps_idist += comps
        
    print(f"average distance comp per query (Naive) = {total_comps_naive / num_queries}")
    print(f"average distance comp per query (Pivot-based) = {total_comps_pivot / num_queries}")
    print(f"average distance comp per query (iDistance) = {total_comps_idist / num_queries}")
    print(f"total time Naive = {total_time_naive}")
    print(f"total time Pivot-based = {total_time_pivot}")
    print(f"total time iDistance = {total_time_idist}")

    # --- ΜΕΡΟΣ 4: ΑΞΙΟΛΟΓΗΣΗ kNN QUERIES ---
    print("\n--- kNN Query Results (Meros 4) ---")
    total_comps_naive_knn = 0; total_time_naive_knn = 0.0
    total_comps_pivot_knn = 0; total_time_pivot_knn = 0.0
    total_comps_idist_knn = 0; total_time_idist_knn = 0.0
    
    for q in queries:
        start_time = time.time()
        _, comps = knn_query_naive(dataset, q, k)
        total_time_naive_knn += time.time() - start_time
        total_comps_naive_knn += comps
        
        start_time = time.time()
        _, comps = knn_query_pivot(dataset, q, k, pivots, distances)
        total_time_pivot_knn += time.time() - start_time
        total_comps_pivot_knn += comps
        
        start_time = time.time()
        _, comps = knn_query_idistance(dataset, q, k, pivots, idistance_array, maxd, maxd_p, closest_pivot_idx)
        total_time_idist_knn += time.time() - start_time
        total_comps_idist_knn += comps
        
    print(f"average distance comp per query (Naive kNN) = {total_comps_naive_knn / num_queries}")
    print(f"average distance comp per query (Pivot-based kNN) = {total_comps_pivot_knn / num_queries}")
    print(f"average distance comp per query (iDistance kNN) = {total_comps_idist_knn / num_queries}")
    print(f"total time Naive kNN = {total_time_naive_knn}")
    print(f"total time Pivot-based kNN = {total_time_pivot_knn}")
    print(f"total time iDistance kNN = {total_time_idist_knn}")