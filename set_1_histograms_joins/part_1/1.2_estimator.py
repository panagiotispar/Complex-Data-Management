################################################
##    Παναγιώτης Παρασκευόπουλος   ΑΜ: 2905   ##
##    Άγγελος Μπεζαΐτης            ΑΜ: 4432   ##
################################################

import sys

def calculate_overlap_ratio(alpha, beta, bin_start, bin_end):
    """Υπολογίζει τι ποσοστό του bin [bin_start, bin_end) καλύπτεται από το [alpha, beta]"""
    overlap_start = max(alpha, bin_start)
    overlap_end = min(beta, bin_end)
    overlap_length = max(0, overlap_end - overlap_start)
    
    bin_length = bin_end - bin_start
    if bin_length == 0:
        return 0
    return overlap_length / bin_length

def load_histograms(filename):
    """Διαβάζει τα ιστογράμματα από το αρχείο txt"""
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # Γραμμή 1: "EQUI-WIDTH", Γραμμή 2: Min, Max, Width, Γραμμή 3: Συχνότητες
    eq_width_meta = lines[1].strip().split(', ')
    min_val = float(eq_width_meta[0].split(': ')[1])
    max_val = float(eq_width_meta[1].split(': ')[1])
    width = float(eq_width_meta[2].split(': ')[1])
    eq_width_freqs = [int(x) for x in lines[2].strip().split(',')]
    
    # Γραμμή 4: "EQUI-DEPTH", Γραμμή 5: Όρια (Boundaries)
    eq_depth_bounds = [float(x) for x in lines[4].strip().split(',')]
    
    return min_val, max_val, width, eq_width_freqs, eq_depth_bounds

def main():
    if len(sys.argv) != 3:
        print("Χρήση: python estimator.py <alpha> <beta>")
        sys.exit(1)
        
    alpha = float(sys.argv[1])
    beta = float(sys.argv[2])
    
    # Διαβάζουμε τα δεδομένα από το αρχείο που φτιάξαμε πριν
    min_val, max_val, width, eq_width_freqs, eq_depth_bounds = load_histograms("histograms_output.txt")
    
    # ---------------------------------------------------------
    # 1. Εκτίμηση με Equi-Width
    # ---------------------------------------------------------
    est_width_count = 0
    for i, freq in enumerate(eq_width_freqs):
        bin_start = min_val + i * width
        bin_end = min_val + (i + 1) * width
        # Αν είναι το τελευταίο bin, βεβαιωνόμαστε ότι κλείνει στο μέγιστο όριο
        if i == len(eq_width_freqs) - 1:
            bin_end = max_val
            
        ratio = calculate_overlap_ratio(alpha, beta, bin_start, bin_end)
        est_width_count += ratio * freq

    # ---------------------------------------------------------
    # 2. Εκτίμηση με Equi-Depth
    # ---------------------------------------------------------
    est_depth_count = 0
    total_elements = sum(eq_width_freqs) # 10104
    num_bins = len(eq_depth_bounds) - 1
    freq_per_bin = total_elements / num_bins # Στο equi-depth, κάθε bin έχει ίδιο αριθμό στοιχείων
    
    for i in range(num_bins):
        bin_start = eq_depth_bounds[i]
        bin_end = eq_depth_bounds[i+1]
        
        ratio = calculate_overlap_ratio(alpha, beta, bin_start, bin_end)
        est_depth_count += ratio * freq_per_bin

    # ---------------------------------------------------------
    # 3. Πραγματικό Αποτέλεσμα
    # ---------------------------------------------------------
    actual_count = 0
    with open('final_general.dat', 'r', encoding='utf-8') as f:
        for line in f:
            cols = line.strip().split()
            if len(cols) >= 2:
                try:
                    age = float(cols[1])
                    if alpha <= age <= beta:
                        actual_count += 1
                except ValueError:
                    continue

    # Τύπωμα αποτελεσμάτων
    err_width = abs(actual_count - est_width_count)
    err_depth = abs(actual_count - est_depth_count)

    # Καθαρό και μορφοποιημένο τύπωμα αποτελεσμάτων
    print("\n" + "=" * 55)
    print(f" ΕΡΩΤΗΜΑ: Αναζήτηση ατόμων με ηλικία από {alpha} έως {beta}")
    print("=" * 55)
    print(f"{'ΜΕΘΟΔΟΣ':<30} | {'ΕΚΤΙΜΗΣΗ':<10} | {'ΣΦΑΛΜΑ':<10}")
    print("-" * 55)
    print(f"{'Πραγματικό Αποτέλεσμα':<30} | {actual_count:<10} | {'-':<10}")
    print(f"{'Equi-Width Histogram':<30} | {est_width_count:<10.2f} | {err_width:<10.2f}")
    print(f"{'Equi-Depth Histogram':<30} | {est_depth_count:<10.2f} | {err_depth:<10.2f}")
    print("=" * 55)
    
    # Αυτόματο συμπέρασμα
    if err_width < err_depth:
        print(">> Συμπέρασμα: Το Equi-Width είχε καλύτερη προσέγγιση εδώ.\n")
    elif err_depth < err_width:
        print(">> Συμπέρασμα: Το Equi-Depth είχε καλύτερη προσέγγιση εδώ.\n")
    else:
        print(">> Συμπέρασμα: Και τα δύο ιστογράμματα είχαν το ίδιο σφάλμα.\n")

if __name__ == "__main__":
    main()