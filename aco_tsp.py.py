"""
Traveling Salesman Problem - Ant Colony Optimization
Graph: H -> D (must pass through #)
Author: Generated for Assignment
"""

import random
import math
import copy

# ============================================================
# GRAPH DEFINITION (dari gambar)
# Nodes: #(hash), A, B, C, D, E, F, G, H
# ============================================================

# Adjacency list dengan bobot
GRAPH = {
    '#': {'A': 3, 'C': 2, 'G': 5},
    'A': {'#': 3, 'C': 6, 'B': 9},
    'B': {'A': 9, 'C': 9, 'H': 8},
    'C': {'#': 2, 'A': 6, 'B': 9, 'D': 4},
    'D': {'C': 4, 'E': 7, 'H': 9},
    'E': {'D': 7, 'F': 2, 'G': 1, 'H': 1},
    'F': {'#': 5, 'E': 2},   # F - # via edge di atas (edge G-# = 5, tapi F terhubung ke E)
    'G': {'#': 5, 'E': 1, 'H': 3},
    'H': {'B': 8, 'D': 9, 'E': 1, 'G': 3}
}

# Semua node
ALL_NODES = list(GRAPH.keys())

# ============================================================
# SHORTEST PATH (Dijkstra) - untuk membangun path antar node
# ============================================================

def dijkstra(graph, start, end):
    """Cari shortest path antara start dan end"""
    import heapq
    dist = {node: float('inf') for node in graph}
    dist[start] = 0
    prev = {node: None for node in graph}
    pq = [(0, start)]
    
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        if u == end:
            break
        for v, w in graph[u].items():
            alt = dist[u] + w
            if alt < dist[v]:
                dist[v] = alt
                prev[v] = u
                heapq.heappush(pq, (alt, v))
    
    # Rekonstruksi path
    path = []
    curr = end
    while curr is not None:
        path.append(curr)
        curr = prev[curr]
    path.reverse()
    
    if path[0] != start:
        return None, float('inf')
    return path, dist[end]

def path_cost(graph, path):
    """Hitung total cost dari sebuah path"""
    total = 0
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        if v in graph[u]:
            total += graph[u][v]
        else:
            return float('inf')
    return total

# ============================================================
# BUILD COMPLETE GRAPH (untuk TSP antar waypoints)
# Waypoints yang WAJIB dikunjungi: H (start), #, D (end)
# Tapi kita ingin visit ALL nodes (TSP)
# 
# Problem: H -> semua node -> D, WAJIB lewat #
# ============================================================

def build_distance_matrix(graph, nodes):
    """Bangun matriks jarak antar semua node menggunakan Dijkstra"""
    n = len(nodes)
    dist_matrix = {}
    path_matrix = {}
    
    for i, src in enumerate(nodes):
        dist_matrix[src] = {}
        path_matrix[src] = {}
        for j, dst in enumerate(nodes):
            if src == dst:
                dist_matrix[src][dst] = 0
                path_matrix[src][dst] = [src]
            else:
                path, cost = dijkstra(graph, src, dst)
                dist_matrix[src][dst] = cost
                path_matrix[src][dst] = path
    
    return dist_matrix, path_matrix

# ============================================================
# ANT COLONY OPTIMIZATION
# ============================================================

class AntColonyOptimization:
    def __init__(self, nodes, dist_matrix, start, end, required_node,
                 n_ants=20, n_iterations=100, alpha=1.0, beta=2.0,
                 evaporation=0.5, Q=100):
        """
        Parameters:
        -----------
        nodes          : list of nodes to visit
        dist_matrix    : dict of dict, distance between nodes
        start          : starting node (H)
        end            : ending node (D)
        required_node  : node yang WAJIB dilewati (#)
        n_ants         : jumlah semut
        n_iterations   : iterasi maksimum
        alpha          : bobot pheromone
        beta           : bobot heuristic (1/distance)
        evaporation    : laju evaporasi pheromone
        Q              : konstanta deposit pheromone
        """
        self.nodes = nodes
        self.dist_matrix = dist_matrix
        self.start = start
        self.end = end
        self.required = required_node
        self.n_ants = n_ants
        self.n_iterations = n_iterations
        self.alpha = alpha
        self.beta = beta
        self.evaporation = evaporation
        self.Q = Q
        
        # Inisialisasi pheromone
        self.pheromone = {}
        for i in nodes:
            self.pheromone[i] = {}
            for j in nodes:
                self.pheromone[i][j] = 1.0
        
        self.best_tour = None
        self.best_cost = float('inf')
        self.iteration_bests = []
    
    def heuristic(self, i, j):
        """Heuristic: 1 / distance"""
        d = self.dist_matrix[i][j]
        if d == 0:
            return float('inf')
        return 1.0 / d
    
    def select_next(self, current, visited, must_visit_required):
        """
        Pilih node berikutnya berdasarkan probabilitas ACO.
        must_visit_required: True jika '#' belum dikunjungi dan ini
                             adalah kesempatan terakhir sebelum end.
        """
        unvisited = [n for n in self.nodes if n not in visited and n != self.end]
        
        # Jika tidak ada unvisited lagi, pergi ke end
        if not unvisited:
            return self.end
        
        # Jika '#' belum dikunjungi dan sudah tidak ada unvisited selain end,
        # paksa kunjungi '#' dulu (jika '#' masih unvisited)
        if self.required not in visited and self.required in unvisited:
            # Cek apakah semua node lain sudah dikunjungi (tinggal # dan end)
            remaining = [n for n in unvisited if n != self.required]
            if not remaining:
                return self.required
        
        # Hitung probabilitas
        numerators = {}
        total = 0.0
        
        for next_node in unvisited:
            tau = self.pheromone[current][next_node] ** self.alpha
            eta = self.heuristic(current, next_node) ** self.beta
            numerators[next_node] = tau * eta
            total += tau * eta
        
        if total == 0:
            return random.choice(unvisited)
        
        # Roulette wheel selection
        r = random.random()
        cumulative = 0.0
        for node, num in numerators.items():
            cumulative += num / total
            if r <= cumulative:
                return node
        
        return list(numerators.keys())[-1]
    
    def construct_tour(self):
        """Satu semut membangun tour lengkap"""
        tour = [self.start]
        visited = {self.start}
        current = self.start
        
        # Node yang harus dikunjungi (selain start dan end)
        middle_nodes = [n for n in self.nodes if n != self.start and n != self.end]
        
        # Kunjungi semua middle nodes
        while len(visited) < len(self.nodes) - 1:  # belum sampai end
            unvisited_middle = [n for n in middle_nodes if n not in visited]
            
            if not unvisited_middle:
                break
            
            # Pilih next node
            next_node = self.select_next(current, visited, 
                                          self.required not in visited)
            
            if next_node == self.end:
                # Belum wajib selesai kalau '#' belum dikunjungi
                if self.required not in visited and self.required in unvisited_middle:
                    # Paksa kunjungi '#' lebih dulu
                    next_node = self.required
                else:
                    break
            
            tour.append(next_node)
            visited.add(next_node)
            current = next_node
        
        # Tambahkan end node
        tour.append(self.end)
        
        # Validasi: # harus ada di tour
        if self.required not in tour[:-1]:  # # tidak ada (selain di end)
            # Insert # di posisi terbaik
            best_pos = 1
            best_cost = float('inf')
            for pos in range(1, len(tour)):
                new_tour = tour[:pos] + [self.required] + tour[pos:]
                c = self.calculate_tour_cost(new_tour)
                if c < best_cost:
                    best_cost = c
                    best_pos = pos
            tour = tour[:best_pos] + [self.required] + tour[best_pos:]
        
        return tour
    
    def calculate_tour_cost(self, tour):
        """Hitung total cost tour"""
        total = 0
        for i in range(len(tour) - 1):
            total += self.dist_matrix[tour[i]][tour[i+1]]
        return total
    
    def update_pheromone(self, all_tours):
        """Update pheromone: evaporasi + deposit"""
        # Evaporasi
        for i in self.nodes:
            for j in self.nodes:
                self.pheromone[i][j] *= (1 - self.evaporation)
                if self.pheromone[i][j] < 0.001:
                    self.pheromone[i][j] = 0.001
        
        # Deposit
        for tour, cost in all_tours:
            if cost == float('inf'):
                continue
            delta = self.Q / cost
            for i in range(len(tour) - 1):
                u, v = tour[i], tour[i+1]
                self.pheromone[u][v] += delta
                self.pheromone[v][u] += delta
    
    def run(self):
        """Jalankan ACO"""
        print("=" * 60)
        print("  ANT COLONY OPTIMIZATION - TSP")
        print(f"  Start: {self.start} | End: {self.end} | Must pass: {self.required}")
        print("=" * 60)
        print(f"  Parameters: ants={self.n_ants}, iter={self.n_iterations}")
        print(f"               alpha={self.alpha}, beta={self.beta}")
        print(f"               evaporation={self.evaporation}, Q={self.Q}")
        print("=" * 60)
        
        for iteration in range(self.n_iterations):
            all_tours = []
            
            for ant in range(self.n_ants):
                tour = self.construct_tour()
                cost = self.calculate_tour_cost(tour)
                all_tours.append((tour, cost))
                
                if cost < self.best_cost:
                    self.best_cost = cost
                    self.best_tour = copy.deepcopy(tour)
            
            self.update_pheromone(all_tours)
            
            iter_best = min(all_tours, key=lambda x: x[1])
            self.iteration_bests.append(iter_best[1])
            
            if (iteration + 1) % 10 == 0:
                print(f"  Iterasi {iteration+1:3d}/{self.n_iterations} | "
                      f"Best iter: {iter_best[1]:6.1f} | "
                      f"Global best: {self.best_cost:6.1f}")
        
        return self.best_tour, self.best_cost

# ============================================================
# EXPAND PATH (node virtual -> node fisik di graph)
# ============================================================

def expand_tour(tour, path_matrix):
    """
    Ubah tour node-level menjadi path nyata di graph
    (karena beberapa edge tidak langsung ada, perlu sub-path)
    """
    full_path = []
    for i in range(len(tour) - 1):
        sub = path_matrix[tour[i]][tour[i+1]]
        if i == 0:
            full_path.extend(sub)
        else:
            full_path.extend(sub[1:])  # hindari duplikat
    return full_path

# ============================================================
# MAIN
# ============================================================

def main():
    print("\n" + "=" * 60)
    print("  TSP dengan ANT COLONY OPTIMIZATION")
    print("  Graph: H -> (semua node) -> D, WAJIB lewat #")
    print("=" * 60)
    
    # Semua node
    nodes = list(GRAPH.keys())
    
    print("\n[1] Membangun distance matrix (Dijkstra)...")
    dist_matrix, path_matrix = build_distance_matrix(GRAPH, nodes)
    
    print("\n  Distance Matrix:")
    print(f"  {'':4}", end="")
    for n in nodes:
        print(f"  {n:4}", end="")
    print()
    for src in nodes:
        print(f"  {src:4}", end="")
        for dst in nodes:
            d = dist_matrix[src][dst]
            if d == float('inf'):
                print(f"  {'inf':4}", end="")
            else:
                print(f"  {d:4.0f}", end="")
        print()
    
    # Validasi: cek apakah H -> # -> D bisa dicapai
    print(f"\n[2] Validasi path:")
    p1, c1 = dijkstra(GRAPH, 'H', '#')
    p2, c2 = dijkstra(GRAPH, '#', 'D')
    print(f"  H -> #: {p1} (cost={c1})")
    print(f"  # -> D: {p2} (cost={c2})")
    
    # Jalankan ACO
    print("\n[3] Menjalankan ACO...")
    aco = AntColonyOptimization(
        nodes=nodes,
        dist_matrix=dist_matrix,
        start='H',
        end='D',
        required_node='#',
        n_ants=30,
        n_iterations=150,
        alpha=1.0,
        beta=3.0,
        evaporation=0.4,
        Q=200
    )
    
    best_tour, best_cost = aco.run()
    
    # Expand ke path fisik
    full_path = expand_tour(best_tour, path_matrix)
    full_cost = path_cost(GRAPH, full_path)
    
    print("\n" + "=" * 60)
    print("  HASIL AKHIR")
    print("=" * 60)
    print(f"\n  Best Tour (node level)  : {' -> '.join(best_tour)}")
    print(f"  Tour Cost (approx)      : {best_cost}")
    print(f"\n  Full Physical Path      : {' -> '.join(full_path)}")
    print(f"  Full Path Cost (actual) : {full_cost}")
    
    # Validasi constraint
    has_hash = '#' in best_tour
    starts_H = best_tour[0] == 'H'
    ends_D = best_tour[-1] == 'D'
    all_visited = set(best_tour) == set(nodes)
    
    print(f"\n  Validasi Constraint:")
    print(f"  ✓ Mulai dari H      : {'Ya' if starts_H else 'TIDAK'}")
    print(f"  ✓ Berakhir di D     : {'Ya' if ends_D else 'TIDAK'}")
    print(f"  ✓ Melewati #        : {'Ya' if has_hash else 'TIDAK'}")
    print(f"  ✓ Semua node visited: {'Ya' if all_visited else 'Tidak (TSP parsial)'}")
    
    # Tampilkan statistik pheromone
    print(f"\n  Top Pheromone Edges:")
    edges = []
    for i in nodes:
        for j in nodes:
            if i < j:
                edges.append((i, j, aco.pheromone[i][j]))
    edges.sort(key=lambda x: -x[2])
    for i, j, p in edges[:5]:
        print(f"    {i} <-> {j}: {p:.4f}")
    
    print("\n" + "=" * 60)
    print("  Iterasi Best Cost per 10 iterasi:")
    for idx, cost in enumerate(aco.iteration_bests):
        if (idx + 1) % 10 == 0:
            bar = '#' * int(200 / cost * 10) if cost < float('inf') else ''
            print(f"  Iter {idx+1:3d}: {cost:6.1f} |{bar}")
    print("=" * 60)
    
    return best_tour, best_cost, full_path, full_cost

if __name__ == '__main__':
    # Set random seed untuk reproducibility
    random.seed(42)
    main()
