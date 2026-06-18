################################################
##    Παναγιώτης Παρασκευόπουλος   ΑΜ: 2905   ##
##    Άγγελος Μπεζαΐτης            ΑΜ: 4432   ##
################################################

# ============================================================================
# PART 1: Semi-joins & Anti-semijoins (Hash and Sort-Merge variants)
# ============================================================================

def hash_semijoin(r, s):
    s_keys = set()
    result = [] 
    
    for tuple_s in s:
        s_keys.add(tuple_s[0])

    for tuple_r in r:
        if tuple_r[0] in s_keys:
            result.append(tuple_r)

    return result

def hash_antisemijoin(r, s):
    s_keys = set()
    result = []
    
    for tuple_s in s:
        s_keys.add(tuple_s[0])
    
    for tuple_r in r:
        if tuple_r[0] not in s_keys:
            result.append(tuple_r)

    return result

def sort_merge_semijoin(r, s):
    sorted_r = sorted(r)
    sorted_s = sorted(s)
    i = 0
    j = 0
    result = []
    
    while i < len(sorted_r) and j < len(sorted_s):
        if sorted_r[i][0] == sorted_s[j][0]:
            result.append(sorted_r[i])
            i += 1
        elif sorted_r[i][0] < sorted_s[j][0]:
            i += 1
        else:
            j += 1
    
    return result
    
def sort_merge_antisemijoin(r, s):
    i = 0
    j = 0
    result = []
    sorted_r = sorted(r)
    sorted_s = sorted(s)
    
    while i < len(sorted_r) and j < len(sorted_s):
        if sorted_r[i][0] == sorted_s[j][0]:
            i += 1
        elif sorted_r[i][0] < sorted_s[j][0]:
            result.append(sorted_r[i])
            i += 1
        else:
            j += 1
            
    result.extend(sorted_r[i:])
    return result

def test_part1():
    """
    Test the 4 functions with small test data from the assignment.
    
    Expected results:
    - hash_semijoin(r, s): [(1,2), (1,4)]
    - hash_antisemijoin(r, s): [(2,5)]
    - sort_merge_semijoin(r, s): [(1,2), (1,4)]
    - sort_merge_antisemijoin(r, s): [(2,5)]
    """
    r = [(1, 2), (1, 4), (2, 5)]
    s = [(1, 'a'), (1, 'c'), (3, 'a')]
    
    print("=" * 70)
    print("PART 1.5: Testing Semi-joins and Anti-semijoins")
    print("=" * 70)
    print(f"Relation r: {r}")
    print(f"Relation s: {s}")
    print()
    
    # Test hash_semijoin
    result_hash_semijoin = hash_semijoin(r, s)
    print(f"hash_semijoin(r, s) = {result_hash_semijoin}")
    print(f"Expected: [(1, 2), (1, 4)]")
    print()
    
    # Test hash_antisemijoin
    result_hash_antisemijoin = hash_antisemijoin(r, s)
    print(f"hash_antisemijoin(r, s) = {result_hash_antisemijoin}")
    print(f"Expected: [(2, 5)]")
    print()
    
    # Test sort_merge_semijoin
    result_sort_merge_semijoin = sort_merge_semijoin(r, s)
    print(f"sort_merge_semijoin(r, s) = {result_sort_merge_semijoin}")
    print(f"Expected: [(1, 2), (1, 4)]")
    print()
    
    # Test sort_merge_antisemijoin
    result_sort_merge_antisemijoin = sort_merge_antisemijoin(r, s)
    print(f"sort_merge_antisemijoin(r, s) = {result_sort_merge_antisemijoin}")
    print(f"Expected: [(2, 5)]")
    print()
    
if __name__ == "__main__":
    test_part1()