# Complex Data Management: Indexing, Joins & Similarity Search 🗄️🚀

A repository containing three advanced database projects focusing on **Query Optimization**, **Spatial Indexing (R-Trees)**, and **High-Dimensional Vector Search (iDistance)**.
Developed for the *Complex Data Management (MYE041)* course at the **University of Ioannina**.

![Python](https://img.shields.io/badge/Language-Python-3776AB)
![Databases](https://img.shields.io/badge/Domain-Database%20Systems-005571)
![Algorithms](https://img.shields.io/badge/Concept-Advanced%20Algorithms-success)

## 📂 Project 1: Query Estimation & Join Algorithms

An exploration of query selectivity estimation using histograms and a performance evaluation of various Join operators on real-world aviation data.

### 🎯 Objective
To build statistical summaries (histograms) for query result estimation and to implement and optimize Relational Algebra join operators (Semi-joins, Anti-semijoins).

### 🛠️ Methodology
* **Histograms:** Implemented both Equi-Width and Equi-Depth histograms to estimate the selectivity of range queries on an age dataset.
* **Join Operators:** Developed Hash-based and Sort-Merge algorithms for Semi-joins and Anti-semijoins. 
* **Pipelining & 3-Way Joins:** Implemented a concurrent 3-way Sort-Merge join and a Pipelined Merge Join to avoid writing intermediate results to the disk.

### 📊 Key Findings
* **Equi-Depth Superiority:** The Equi-Depth histogram proved more resilient to skewed data distributions compared to Equi-Width, providing consistently lower estimation errors.
* **Filter Push-Down:** Applying selection filters (e.g., aircraft type) before executing the join drastically reduced the input size and optimized execution time.
* **I/O Optimization:** Pipelining successfully prevented I/O bottlenecks by establishing a continuous stream of tuples between operators.

---

## 🌍 Project 2: Spatial Data Indexing with R-Trees

Development of a main-memory spatial index to efficiently evaluate geographic queries on a dataset containing 51,970 restaurant locations in Beijing.

### 🎯 Objective
To construct an R-Tree using the Sort-Tile-Recursive (STR) bulk-loading algorithm and utilize it for fast spatial query evaluation.

### ⚙️ Implementation Details
* **STR Construction:** Sorted the raw points by X-axis into vertical slices, and then by Y-axis into tiles to group geographically proximate points into Minimum Bounding Rectangles (MBRs).
* **Window & Distance Queries:** Implemented recursive depth-first search (DFS) algorithms to find points within specific bounding boxes or Euclidean radii.
* **k-Nearest Neighbors (kNN):** Utilized a Priority Queue (Min-Heap) for an incremental nearest neighbor search, evaluating MBR distances dynamically.

### 📊 Key Findings
* The STR bulk-loading approach yielded an optimally packed R-Tree with zero node underflow and minimized MBR overlap.
* MBR pruning allowed the algorithm to discard massive portions of the dataset instantly, significantly outperforming linear coordinate scanning.

### 📸 Spatial Results
*(Add your own screenshot here)*
![R-Tree Architecture](screenshots/rtree_structure.png)

---

## 🔍 Project 3: High-Dimensional Vector Search & iDistance

A comparative study on defeating the "curse of dimensionality" using metric space indexing for 10D vectors.

### 🎯 Objective
To perform Range and kNN similarity queries on 10,000 dense 10-dimensional vectors, evaluating three different algorithmic approaches: Linear Scan, Pivot-based, and iDistance.

### 🛠️ Methodology
* **Baseline:** Implemented a Naive Linear Scan computing exact Euclidean distances for all points.
* **Pivot-Based Search:** Utilized a Max-Sum heuristic to select reference points (pivots) and applied the Triangle Inequality to mathematically prune invalid vectors without computing exact distances.
* **iDistance:** Mapped the 10D space into a 1-Dimensional B+-Tree-like array. Queries were transformed into 1D bounds and searched in $O(\log N)$ time using Binary Search (`bisect`).

### 📊 Key Findings
* **iDistance Dominance:** The iDistance method was by far the fastest and most scalable solution for both Range and kNN queries, leveraging binary search to completely bypass evaluating irrelevant partitions.
* **The Pivot Paradox:** While the Pivot-based method executed the absolute minimum number of mathematical distance computations, it suffered in total execution time due to the iterative overhead of checking multiple Triangle Inequalities in Python.
* **Dynamic Pruning in kNN:** Utilizing a Max-Heap to track the $k$-th best distance allowed the search radius ($\epsilon$) to dynamically shrink, dramatically accelerating the pruning process in later stages of the dataset.

### 📸 Performance Metrics
*(Add your own screenshot of the plots from the report here)*
![iDistance Performance Plot](screenshots/vector_search_plot.png)

---

## 🚀 How to Run

### HW1 (Histograms & Joins)
```bash
# Generate Histograms
python set_1/1.1_histograms.py
# Evaluate Join Algorithms
python set_1/askisi2_1.py