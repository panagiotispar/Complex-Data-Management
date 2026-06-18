################################################
##    Παναγιώτης Παρασκευόπουλος   ΑΜ: 2905   ##
##    Άγγελος Μπεζαΐτης            ΑΜ: 4432   ##
################################################

def load_ages(filename):
    ages = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                columns = line.strip().split()
                if len(columns) >= 2:
                    try:
                        ages.append(int(columns[1]))
                    except ValueError:
                        continue
        return ages
    except FileNotFoundError:
        print(f"Το αρχείο {filename} δεν βρέθηκε.")
        return []

def create_equi_width_histogram(ages, num_bins=10):
    min_age, max_age = min(ages), max(ages)
    width = (max_age - min_age) / num_bins
    frequencies = [0] * num_bins
    
    for age in ages:
        bin_index = int((age - min_age) / width)
        if bin_index == num_bins:
            bin_index -= 1
        frequencies[bin_index] += 1
        
    return frequencies, min_age, max_age, width

def create_equi_depth_histogram(ages, num_bins=10):
    sorted_ages = sorted(ages)
    total_elements = len(sorted_ages)
    elements_per_bin = total_elements / num_bins
    
    boundaries = [sorted_ages[0]]
    for i in range(1, num_bins):
        cut_index = int(i * elements_per_bin)
        boundaries.append(sorted_ages[cut_index])
    boundaries.append(sorted_ages[-1])
    
    return boundaries

def print_ascii_chart(title, labels, values, max_bar_length=30):
    """Βοηθητική συνάρτηση για εκτύπωση ASCII ραβδογραμμάτων στο τερματικό."""
    print(f"\n{title}")
    print("=" * 60)
    max_val = max(values) if values else 1
    
    for label, val in zip(labels, values):
        bar_len = int((val / max_val) * max_bar_length)
        bar = '█' * bar_len
        print(f"{label:>15} | {bar} ({int(val)})")
    print("=" * 60)

# --- Κυρίως Πρόγραμμα ---
ages_data = load_ages('final_general.dat')

if ages_data:
    print(f"[+] Διαβάστηκαν επιτυχώς {len(ages_data)} εγγραφές ηλικιών.")

    # Δημιουργία Ιστογραμμάτων (10 bins όπως ζητάει η εκφώνηση)
    eq_width_freqs, min_a, max_a, bin_w = create_equi_width_histogram(ages_data)
    eq_depth_boundaries = create_equi_depth_histogram(ages_data)

    # --- Εκτύπωση Equi-Width στο τερματικό ---
    width_labels = [f"[{int(min_a + i*bin_w)}, {int(min_a + (i+1)*bin_w)})" for i in range(10)]
    print_ascii_chart(">>> EQUI-WIDTH HISTOGRAM (Σταθερό Πλάτος)", width_labels, eq_width_freqs)

    # --- Εκτύπωση Equi-Depth στο τερματικό ---
    depth_labels = [f"[{int(eq_depth_boundaries[i])}, {int(eq_depth_boundaries[i+1])})" for i in range(10)]
    # Στο equi-depth όλα τα bins έχουν τον ίδιο αριθμό στοιχείων
    depth_freqs = [len(ages_data) / 10] * 10 
    print_ascii_chart(">>> EQUI-DEPTH HISTOGRAM (Σταθερή Συχνότητα)", depth_labels, depth_freqs)

    # --- Αποθήκευση στο αρχείο ---
    output_filename = "histograms_output.txt"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write("EQUI-WIDTH\n")
        f.write(f"Min: {min_a}, Max: {max_a}, Width: {bin_w}\n")
        f.write(",".join(map(str, eq_width_freqs)) + "\n")
        f.write("EQUI-DEPTH\n")
        f.write(",".join(map(str, eq_depth_boundaries)) + "\n")

    print(f"\n[+] Τα ιστογράμματα αποθηκεύτηκαν επιτυχώς στο '{output_filename}'.\n")