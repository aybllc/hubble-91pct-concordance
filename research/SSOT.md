# SSOT — 91% Concordance: Hubble Tension Resolution
**Repo:** abba-01/hubble-91pct-concordance
**Author:** Eric D. Martin / All Your Baseline LLC
**DOI:** 10.5281/zenodo.17322471
**Status:** Published — UHA references restored post patent filing (US 63/902,536)
**Last Updated:** 2026-03-24

---

## What This Is

The **primary published result** for N/U Algebra + Observer Tensor Hubble tension resolution. Published to Zenodo with UHA references intentionally obfuscated for patent protection. 91% tension reduction using 6 H₀ probes.

---

## Core Result

| Probe class | H₀ (km/s/Mpc) | Interval |
|-------------|---------------|---------|
| Early (CMB + BAO) | 67.30 ± 0.58 | [66.93, 67.72] |
| Late (Distance Ladder + Geometric) | 72.72 ± 2.63 | [71.81, 73.63] |
| Merged | 69.79 ± 3.36 | — |

**Tension reduction: 91%** (5.40 → 0.48 km/s/Mpc gap)
**Systematic needed for full concordance:** 0.24 km/s/Mpc (budget available: 2.99 km/s/Mpc)

---

## 6 Probes

Planck18, DES-IDL, SH0ES, TRGB, TDCOSMO, Megamaser; 3,988 objects encoded; 15 pairwise comparisons; 5 critical tensions (δ* > 1.0)

---

## Framework

- N/U Algebra (conservative uncertainty propagation)
- Observer domain tensors (OMMP epistemic distance)
- UHA ξ coordinate encoding (ξ = d_c/d_H, Patent US 63/902,536)
- Seven-Layer provenance (USO)

---

## UHA Encoding (post patent filing)

Patent US 63/902,536 now filed. UHA work restored:
- **`07_code/uha_xi_encoding.py`** — ξ = d_c/d_H for all 6 probes at z_eff; UHA addresses (a, ξ, CosmoID); NGC 4258 anchor |Δξ| = 7.53×10⁻⁸
- **`03_data/anchor_catalog_uha.csv`** — 52 NGC 4258 HII objects with ξ_SH0ES, ξ_Planck, delta_xi
- **`CLARIFICATION.md`** — full term mapping (75 obfuscated refs), N/U formula, Zenodo freeze rationale

Key ξ result: ξ_CMB ≈ 3.13 vs ξ_local ≈ 0.002 — factor ~620 frame separation. This is the geometric root of the H₀ tension. Zenodo record (10.5281/zenodo.17322471) preserved as-is; this repo is the de-obfuscated living version.
