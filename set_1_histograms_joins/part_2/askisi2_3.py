################################################
##    Παναγιώτης Παρασκευόπουλος   ΑΜ: 2905   ##
##    Άγγελος Μπεζαΐτης            ΑΜ: 4432   ##
################################################

# ============================================================================
# PART 3: Pipelining & 3-way Join
# ============================================================================

def join_r_s_generator(r, s):
    """
    Generator for joining r and s.
    Yields tuples that satisfy the join condition between r and s.
    
    Args:
        r: First relation (sorted by index 0)
        s: Second relation (sorted by index 0)

    Yields:
        Tuples that satisfy the join condition between r and s.
    """
    
    i, j = 0, 0
    
    while i < len(r) and j < len(s):
        if r[i][0] == s[j][0]:
            temp_j = j 
            while temp_j < len(s) and s[temp_j][0] == r[i][0]:
                yield (r[i][0], r[i][1], s[temp_j][1]) 
                temp_j += 1
            i += 1
        elif r[i][0] < s[j][0]:
            i += 1
        else:
            j += 1


# [ ] TODO 3.1: Υλοποίηση της pipelined_merge_join(r, s, t)
# Tip: Python generators και yield για να στέλνουμε δεδομένα στο επόμενο join
# χωρίς να τα αποθηκεύουμε σε ενδιάμεσες λίστες ή αρχεία

def pipelined_merge_join(r, s, t):
    # Ξεκινάμε το pipeline (δεν υπολογίζει τίποτα ακόμα, απλά ετοιμάζεται)
    rs_gen = join_r_s_generator(r, s)
    
    k = 0  # Δείκτης για τη σχέση t
    result = []
    
    # Προσπαθούμε να τραβήξουμε το πρώτο tuple από το pipeline
    try:
        current_rs = next(rs_gen)
    except StopIteration:
        return result  # Αν το join(r,s) είναι άδειο, τελειώσαμε
        
    while k < len(t):
        # current_rs έχει μορφή (A, B, C), άρα το κλειδί είναι current_rs[0]
        # Το t[k] έχει μορφή (A, D), άρα το κλειδί είναι t[k][0]
        
        if current_rs[0] == t[k][0]:
            # Βρήκαμε ταύτιση! 
            # 1. Φτιάξε το νέο tuple (A, B, C, D) και κάνε το append στο result
            #    Hint: current_rs[0], current_rs[1], current_rs[2], t[k][1]
            temp_k = k
            while temp_k < len(t) and t[temp_k][0] == current_rs[0]:
                result.append((current_rs[0], current_rs[1], current_rs[2], t[temp_k][1]))
                temp_k += 1
            
            # 2. Τράβα το επόμενο στοιχείο από το pipeline για να συνεχίσουμε
            try:
                current_rs = next(rs_gen)
            except StopIteration:
                break # Αν άδειασε το pipeline, σταματάμε το ψάξιμο
                
        elif current_rs[0] < t[k][0]:
            # Το pipeline έμεινε πίσω, τράβα το επόμενο στοιχείο από το pipeline
            try:
                current_rs = next(rs_gen)
            except StopIteration:
                break
        else:
            # Η σχέση t έμεινε πίσω, προχώρα τον δείκτη k
            k += 1
            
    return result


# [ ] TODO 3.2: Υλοποίηση της three_way_sort_merge_join(r, s, t)
# Αντί για 2 δείκτες, εδώ θα ελέγχουμε 3 δείκτες ταυτόχρονα στις 3
# ήδη ταξινομημένες λίστες
def three_way_sort_merge_join(r, s, t):
    """
    Sort-merge join for three relations r, s, t.
    All three relations should be sorted by their first attribute.
    """
    i, j, k = 0, 0, 0
    result = []
    
    # Το loop συνεχίζεται όσο ΔΕΝ έχουμε φτάσει στο τέλος ΚΑΜΙΑΣ από τις τρεις σχέσεις
    while i < len(r) and j < len(s) and k < len(t):
        r_key = r[i][0]
        s_key = s[j][0]
        t_key = t[k][0]
        
        # Αν και τα 3 κλειδιά είναι ίσα, βρήκαμε 3-way ταύτιση
        if r_key == s_key == t_key:
            # 1. Πρέπει να συνδυάσουμε το r[i] με ΟΛΑ τα s και ΟΛΑ τα t 
            #    που έχουν αυτό το κοινό κλειδί.
            #    Θα χρειαστούμε temp_j και temp_k όπως κάναμε πριν.
            temp_j = j
            while temp_j < len(s) and s[temp_j][0] == r_key:
                temp_k = k
                while temp_k < len(t) and t[temp_k][0] == r_key:
                    # Κάνε append το συνδυασμένο tuple (A, B, C, D)
                    # Hint: r[i][0], r[i][1], s[temp_j][1], t[temp_k][1]
                    # ...
                    result.append((r[i][0], r[i][1], s[temp_j][1], t[temp_k][1])) 
                    temp_k += 1
                temp_j += 1
                
            # Αφού συνδυάσαμε το r[i], προχωράμε στο επόμενο στοιχείο της r
            i += 1
        else:
            # Αν δεν είναι όλα ίσα, βρίσκουμε το μέγιστο από τα 3 κλειδιά
            max_key = max(r_key, s_key, t_key)
            
            # 2. Προωθούμε ΟΛΟΥΣ τους δείκτες που "υστέρησαν" σε σχέση με το max_key
            if r_key < max_key: i += 1
            if s_key < max_key: j += 1
            if t_key < max_key: k += 1
                
    return result

def test_part3():
    # Δημιουργία δοκιμαστικών δεδομένων (ήδη ταξινομημένων ως προς το index 0)
    r = [(1, 'b1'), (2, 'b2'), (3, 'b3'), (4, 'b4')]
    s = [(1, 'c1'), (1, 'c2'), (2, 'c3'), (3, 'c4')]
    t = [(1, 'd1'), (2, 'd2'), (3, 'd3'), (5, 'd4')]

    print("=" * 70)
    print("PART 3: Testing 3-Way Joins")
    print("=" * 70)
    
    print("\n[Pipelined Merge Join]")
    pipelined_result = pipelined_merge_join(r, s, t)
    for row in pipelined_result:
        print(row)
        
    print("\n[Three-way Sort-Merge Join]")
    three_way_result = three_way_sort_merge_join(r, s, t)
    for row in three_way_result:
        print(row)
        
    if pipelined_result == three_way_result:
        print("\nSuccess: Both joins produced the same result!")
    else:
        print("\nError: The results differ between the two join methods.")

if __name__ == "__main__":
    test_part3()