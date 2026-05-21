# Method-instability and between-method disagreement

All denominators below are over **pairs that at least one of the 9 runs put in the same group** (`pair_count_with_any_yes`). Pairs no run ever co-grouped are excluded from the denominator.

`pair_count_with_any_yes`: 1034

## 1. Within-method instability

For each method M (3 runs), a pair is *instable within M* if M's 3 runs disagree (count ∈ {1,2}). Stable = unanimous {0, 3}.

| method | within-method instability |
|---|---:|
| m1_cluster_anchored | 0.191 |
| m2_blind | 0.144 |
| m3_focal_anchored | 0.456 |

## 2. Between-method disagreement

For each pair, `cross_method_spread = max(m1_count, m2_count, m3_count) - min(...)` over the per-method counts (each ∈ {0..3}). Spread ≥ 2 = a method strongly differs from another.

- pairs with cross_method_spread ≥ 2: 695 (0.672)
- pairs with cross_method_spread ≥ 3 (strong): 393 (0.380)
