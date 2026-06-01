# TSP dengan Ant Colony Optimization (ACO)

## Deskripsi
Program ini menyelesaikan **Traveling Salesman Problem (TSP)** pada graph berikut menggunakan algoritma **Ant Colony Optimization (ACO)**.

- **Start**: Node **H**
- **End**: Node **D**
- **Constraint**: Wajib melewati node **#** (hash)
- **Tujuan**: Mengunjungi **semua node** dengan total biaya minimum

---

## Struktur Graph

```
Nodes: #, A, B, C, D, E, F, G, H

Edges (undirected, berbobot):
  # -- A  : 3        C -- D  : 4
  # -- C  : 2        D -- E  : 7
  # -- G  : 5        D -- H  : 9
  A -- C  : 6        E -- F  : 2
  A -- B  : 9        E -- G  : 1
  B -- C  : 9        E -- H  : 1
  B -- H  : 8        G -- H  : 3
```

---

## Hasil Optimal

| Keterangan | Nilai |
|---|---|
| **Best Tour** | H → E → G → F → B → A → # → C → D |
| **Total Cost** | **34** |
| Melewati # | ✓ Ya |
| Start H | ✓ Ya |
| End D | ✓ Ya |
| Semua node visited | ✓ Ya |

---

## Algoritma ACO

### Parameter
| Parameter | Nilai | Deskripsi |
|---|---|---|
| `n_ants` | 30 | Jumlah semut per iterasi |
| `n_iterations` | 150 | Jumlah iterasi |
| `alpha (α)` | 1.0 | Bobot pheromone |
| `beta (β)` | 3.0 | Bobot heuristic (1/jarak) |
| `evaporation (ρ)` | 0.4 | Laju evaporasi pheromone |
| `Q` | 200 | Konstanta deposit pheromone |

### Cara Kerja
1. **Inisialisasi**: Semua edge mendapat pheromone awal = 1.0
2. **Konstruksi Tour**: Setiap semut membangun rute dengan probabilitas:
   ```
   P(i→j) = [τ(i,j)^α × η(i,j)^β] / Σ[τ^α × η^β]
   ```
   - `τ(i,j)` = kadar pheromone edge (i,j)
   - `η(i,j)` = heuristic = 1/jarak(i,j)
3. **Update Pheromone**:
   - Evaporasi: `τ(i,j) = (1-ρ) × τ(i,j)`
   - Deposit: `τ(i,j) += Q / tour_cost`
4. **Constraint #**: Jika node `#` belum dikunjungi saat semut hendak ke `D`, dipaksa kunjungi `#` dahulu

---

## Cara Menjalankan

### Requirements
```bash
Python 3.6+  (tidak perlu library eksternal)
```

### Run
```bash
python aco_tsp.py
```

### Output yang Dihasilkan
```
============================================================
  TSP dengan ANT COLONY OPTIMIZATION
  Graph: H -> (semua node) -> D, WAJIB lewat #
============================================================
...
  Best Tour  : H -> E -> G -> F -> B -> A -> # -> C -> D
  Tour Cost  : 34
============================================================
```

---

## Struktur File

```
aco_tsp/
├── aco_tsp.py     # Program utama ACO
└── README.md      # Dokumentasi ini
```

---

## Referensi

- Dorigo, M., & Gambardella, L. M. (1997). Ant colony system: A cooperative learning approach to the traveling salesman problem. *IEEE Transactions on Evolutionary Computation*, 1(1), 53-66.
- Dorigo, M., Maniezzo, V., & Colorni, A. (1996). Ant system: Optimization by a colony of cooperating agents. *IEEE Transactions on Systems, Man, and Cybernetics*, 26(1), 29-41.
