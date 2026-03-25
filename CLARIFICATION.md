# CLARIFICATION — UHA Reference Obfuscation

**Author:** Eric D. Martin / All Your Baseline LLC
**Date:** 2026-03-24
**Patent:** US 63/902,536 (filed 2025-10-21)

---

## What Was Obfuscated and Why

This repository was published (DOI: 10.5281/zenodo.17322471) with Universal
Horizon Address (UHA) references systematically removed for patent protection.
The patent has now been filed. This document restores the record.

---

## Term Mapping

| Published term | Actual term | Where |
|----------------|-------------|-------|
| "high-precision coordinate" | UHA coordinate system | README.md, RESULTS_SUMMARY.md |
| "object-level indexing" | UHA localization | README.md, FRAMEWORK_CLAIM.md |
| "object identifiers" | UHA identifiers | anchor_catalog.csv |
| `OBJECT_ID` column | `UHA_ID` column | anchor_catalog.csv |
| `03_data/` directory | `03_uha_framework/` | repo structure |
| `aggregate_pair()` | `nu_merge()` | hubble_analysis.py |
| `aggregate_sequential()` | `nu_cumulative_merge()` | hubble_analysis.py |
| `compute_interval()` | `nu_interval()` | hubble_analysis.py |
| "conservative aggregation" | N/U Algebra merge | hubble_analysis.py |

**75 references** were replaced across all files. See `OBFUSCATION_COMPLETE.md`
for the full record of what was changed.

---

## The UHA Work That Was Claimed But Not Shown

The published README states: *"3,988 objects encoded with object identifiers"*.
The actual encoding uses UHA ξ coordinates:

    ξ = d_c(z_eff) / d_H(H₀)

where d_c is the comoving distance to the object and d_H = c/H₀ is the
Hubble distance. ξ is dimensionless and H₀-independent for redshift-derived
distances (both numerator and denominator scale as 1/H₀ and cancel).

**The actual UHA encoding demonstration is now in:**
`07_code/uha_xi_encoding.py`

This script shows:
- ξ values for all 6 H₀ probes at their effective redshifts
- UHA addresses (a, ξ, CosmoID) for each probe
- ξ encoding of the 52 NGC 4258 anchor objects (|Δξ| = 7.53×10⁻⁸)
- The physical interpretation: the early/late H₀ split is a frame-mixing
  artifact between probes at vastly different ξ positions (ξ_CMB ≈ 3.3
  vs ξ_local ≈ 0.002)

---

## The N/U Algebra Work That Was Obfuscated

The merge formula hidden by obfuscation:

    H_NU = ((n₁+n₂)/2,  (u₁+u₂)/2 + |n₁-n₂|/2)

This is N/U Algebra (DOI: 10.5281/zenodo.17172694). The uncertainty term
inflates by |n₁−n₂|/2 — it captures the disagreement between measurements
as irreducible uncertainty rather than forcing a weighted mean.

---

## Repository Status

- **Zenodo record** (10.5281/zenodo.17322471): obfuscated version preserved as-is
- **GitHub (this repo)**: de-obfuscated via this CLARIFICATION.md + uha_xi_encoding.py
- **Manuscript** (10.5281/zenodo.19154280): full UHA + ξ methodology documented
- **Patent:** US 63/902,536 — filed, pending grant

The Zenodo record is not updated because the published DOI represents the
state of the work at publication time. This repo is the living version.
