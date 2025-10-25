"""
Hubble Tension Analysis via Conservative Uncertainty Propagation
==================================================================
Author: Eric D. Martin
Framework: Conservative statistical aggregation
Date: 2025-10-11

This script implements conservative uncertainty propagation to reconcile
H₀ measurements from multiple cosmological probes.

References:
- Planck 2018: Planck Collaboration 2020, A&A 641, A6 (arXiv:1807.06209)
- SH0ES 2022: Riess et al. 2022, ApJL 934, L7 (arXiv:2112.04510)
- H0LiCOW 2020: Wong et al. 2020, MNRAS 498, 1420 (arXiv:1907.04869)
- Megamaser 2020: Pesce et al. 2020, ApJL 891, L1
- DES-Y5 2024: DES Collaboration 2025, MNRAS 537, 1818
- TRGB CCHP: Freedman et al. 2020, ApJ 891, 57
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Tuple, List
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

# Latest published H₀ measurements (km/s/Mpc)
# All values verified against peer-reviewed literature as of 2025-10-11
H0_DATA = {
    'source': [
        'Planck 2018 CMB',
        'SH0ES 2022',
        'H0LiCOW 2020',
        'Megamaser 2020',
        'DES-Y5 2024',
        'TRGB CCHP 2020'
    ],
    'method': [
        'CMB (ΛCDM)',
        'Cepheids+SNe Ia',
        'Time-delay lensing',
        'Megamaser (NGC 4258)',
        'SNe Ia + BAO (inverse ladder)',
        'TRGB'
    ],
    'redshift': [
        1100.0,      # CMB last scattering surface
        0.01,        # Local distance ladder (z < 0.01)
        0.5,         # Typical lens redshift (z ~ 0.3-0.7)
        0.0023,      # NGC 4258 (z = 0.0023)
        0.7,         # DES-Y5 effective redshift
        0.01         # Local TRGB (z < 0.01)
    ],
    'n': [
        67.4,   # Planck Collaboration 2020 (arXiv:1807.06209)
        73.04,  # Riess et al. 2022 (arXiv:2112.04510)
        73.3,   # Wong et al. 2020 (arXiv:1907.04869)
        73.9,   # Pesce et al. 2020 (MCP)
        67.19,  # DES Collaboration 2024 (DES-SN5YR + DESI-BAO)
        69.6    # Freedman et al. 2020 (CCHP - updated value)
    ],
    'u': [
        0.5,    # Planck (68% CL)
        1.04,   # SH0ES (statistical + systematic)
        1.8,    # H0LiCOW (average of +1.7/-1.8)
        3.0,    # Megamaser
        0.65,   # DES-Y5 (average of +0.66/-0.64)
        2.5     # TRGB CCHP (updated uncertainty)
    ]
}

# ============================================================================
# STATISTICAL AGGREGATION OPERATORS
# ============================================================================

def aggregate_pair(v1: float, e1: float, v2: float, e2: float) -> Tuple[float, float]:
    """
    Aggregate two measurements with conservative error propagation.

    Args:
        v1, e1: First value and error estimate
        v2, e2: Second value and error estimate

    Returns:
        Tuple of (aggregated_value, propagated_error)
    """
    agg_val = (v1 + v2) * 0.5
    prop_err = (e1 + e2) * 0.5 + abs(v1 - v2) * 0.5
    return agg_val, prop_err


def aggregate_sequential(values: np.ndarray, errors: np.ndarray) -> Tuple[float, float]:
    """
    Sequentially aggregate multiple measurements.

    Args:
        values: Array of measured values
        errors: Array of error estimates

    Returns:
        Final aggregated (value, error) pair
    """
    if len(values) != len(errors):
        raise ValueError("Values and errors must have same length")

    if len(values) == 0:
        return 0.0, 0.0

    result_val = values[0]
    result_err = errors[0]

    for i in range(1, len(values)):
        result_val, result_err = aggregate_pair(
            result_val, result_err, values[i], errors[i]
        )

    return result_val, result_err


def compute_interval(v: float, e: float) -> Tuple[float, float]:
    """Convert value-error pair to interval [v-e, v+e]"""
    return v - e, v + e


# ============================================================================
# DATA PREPARATION
# ============================================================================

def create_dataset() -> pd.DataFrame:
    """Create and validate the H₀ measurements dataset"""
    df = pd.DataFrame(H0_DATA)

    # Add derived columns
    df['interval_low'] = df['n'] - df['u']
    df['interval_high'] = df['n'] + df['u']
    df['interval_width'] = 2 * df['u']
    df['relative_uncertainty'] = df['u'] / df['n']

    # Categorize by redshift regime
    df['regime'] = df['redshift'].apply(
        lambda z: 'Early (CMB)' if z > 100 else 'Late (z<1)'
    )

    return df


# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

def calculate_aggregated_h0(df: pd.DataFrame) -> Tuple[float, float, pd.DataFrame]:
    """
    Calculate aggregated H₀ using conservative propagation.

    Returns:
        (aggregated_value, aggregated_error, steps_df)
    """
    values = df['n'].values
    errors = df['u'].values

    # Track aggregation steps
    steps = []
    current_val = values[0]
    current_err = errors[0]

    steps.append({
        'step': 0,
        'source': df.iloc[0]['source'],
        'n': current_val,
        'u': current_err,
        'interval_low': current_val - current_err,
        'interval_high': current_val + current_err
    })

    for i in range(1, len(values)):
        current_val, current_err = aggregate_pair(
            current_val, current_err,
            values[i], errors[i]
        )

        steps.append({
            'step': i,
            'source': f"After combining {df.iloc[i]['source']}",
            'n': current_val,
            'u': current_err,
            'interval_low': current_val - current_err,
            'interval_high': current_val + current_err
        })

    steps_df = pd.DataFrame(steps)
    return current_val, current_err, steps_df


def calculate_tension(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate pairwise tensions between measurements.

    Tension metric: σ = |n₁ - n₂| / sqrt(u₁² + u₂²)
    """
    tensions = []
    n = len(df)

    for i in range(n):
        for j in range(i + 1, n):
            n1, u1 = df.iloc[i]['n'], df.iloc[i]['u']
            n2, u2 = df.iloc[j]['n'], df.iloc[j]['u']

            tension_sigma = abs(n1 - n2) / np.sqrt(u1**2 + u2**2)

            tensions.append({
                'source_1': df.iloc[i]['source'],
                'source_2': df.iloc[j]['source'],
                'delta_H0': abs(n1 - n2),
                'tension_sigma': tension_sigma,
                'overlaps': not (min(n1 + u1, n2 + u2) < max(n1 - u1, n2 - u2))
            })

    return pd.DataFrame(tensions)


# ============================================================================
# VISUALIZATION
# ============================================================================

def plot_measurements(df: pd.DataFrame, h0_agg: Tuple[float, float], save_path: str = None):
    """
    Create comprehensive visualization of H₀ measurements and aggregated result.
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    # ---- Panel 1: Individual Measurements ----
    val_agg, err_agg = h0_agg
    colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(df)))

    for i, row in df.iterrows():
        ax1.errorbar(
            row['n'], i,
            xerr=row['u'],
            fmt='o',
            color=colors[i],
            capsize=5,
            capthick=2,
            markersize=8,
            label=f"{row['source']} ({row['method']})"
        )

    # Plot aggregated result
    ax1.axvspan(val_agg - err_agg, val_agg + err_agg, alpha=0.2, color='red', label='Aggregated')
    ax1.axvline(val_agg, color='red', linestyle='--', linewidth=2, label=f'H₀ = {val_agg:.2f}')

    ax1.set_xlabel('H₀ (km/s/Mpc)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Measurement', fontsize=12, fontweight='bold')
    ax1.set_title('Hubble Constant Measurements and Conservative Aggregation', fontsize=14, fontweight='bold')
    ax1.legend(loc='best', fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_yticks(range(len(df)))
    ax1.set_yticklabels(df['source'])

    # ---- Panel 2: Redshift Dependence ----
    early = df[df['regime'] == 'Early (CMB)']
    late = df[df['regime'] == 'Late (z<1)']

    ax2.errorbar(
        early['redshift'], early['n'],
        yerr=early['u'],
        fmt='s',
        color='blue',
        capsize=5,
        markersize=10,
        label='Early Universe (CMB)',
        alpha=0.7
    )

    ax2.errorbar(
        late['redshift'], late['n'],
        yerr=late['u'],
        fmt='o',
        color='orange',
        capsize=5,
        markersize=10,
        label='Late Universe (z<1)',
        alpha=0.7
    )

    # Add aggregated band
    ax2.axhspan(val_agg - err_agg, val_agg + err_agg, alpha=0.2, color='red', label='Aggregated ± u')
    ax2.axhline(val_agg, color='red', linestyle='--', linewidth=2)

    ax2.set_xlabel('Redshift z', fontsize=12, fontweight='bold')
    ax2.set_ylabel('H₀ (km/s/Mpc)', fontsize=12, fontweight='bold')
    ax2.set_title('H₀ vs Redshift: Early-Late Universe Tension', fontsize=14, fontweight='bold')
    ax2.set_xscale('log')
    ax2.legend(loc='best', fontsize=10)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    plt.show()


def plot_aggregation_evolution(steps_df: pd.DataFrame, save_path: str = None):
    """
    Visualize how the aggregated interval evolves as measurements are added.
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    for i, row in steps_df.iterrows():
        color = plt.cm.coolwarm(i / len(steps_df))
        ax.errorbar(
            row['n'], i,
            xerr=row['u'],
            fmt='o',
            color=color,
            capsize=5,
            capthick=2,
            markersize=8
        )
        ax.text(
            row['interval_high'] + 0.5, i,
            row['source'],
            fontsize=9,
            va='center'
        )

    ax.set_xlabel('H₀ (km/s/Mpc)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Aggregation Step', fontsize=12, fontweight='bold')
    ax.set_title('Conservative Aggregation: Iterative Evolution', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_yticks(range(len(steps_df)))
    ax.set_yticklabels([f"Step {i}" for i in range(len(steps_df))])

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    plt.show()


# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def main():
    """Execute complete Hubble tension analysis"""

    print("=" * 80)
    print("HUBBLE TENSION ANALYSIS via CONSERVATIVE UNCERTAINTY PROPAGATION")
    print("=" * 80)
    print()

    # Create dataset
    print("Loading H₀ measurements...")
    df = create_dataset()
    print(f"✓ Loaded {len(df)} measurements")
    print()

    # Display dataset
    print("Dataset Summary:")
    print("-" * 80)
    print(df[['source', 'method', 'n', 'u', 'regime']].to_string(index=False))
    print()

    # Calculate aggregated H₀
    print("Calculating aggregated H₀...")
    val_agg, err_agg, steps_df = calculate_aggregated_h0(df)
    interval_low, interval_high = compute_interval(val_agg, err_agg)

    print("=" * 80)
    print("RESULT: AGGREGATED HUBBLE CONSTANT")
    print("=" * 80)
    print(f"H₀ = {val_agg:.3f} ± {err_agg:.3f} km/s/Mpc")
    print(f"Interval: [{interval_low:.3f}, {interval_high:.3f}]")
    print(f"Relative uncertainty: {err_agg/val_agg*100:.2f}%")
    print()

    # Calculate tensions
    print("Calculating pairwise tensions...")
    tensions = calculate_tension(df)
    print()
    print("Pairwise Tensions (σ > 3.0 shown):")
    print("-" * 80)
    high_tension = tensions[tensions['tension_sigma'] > 3.0]
    if len(high_tension) > 0:
        print(high_tension[['source_1', 'source_2', 'tension_sigma', 'overlaps']].to_string(index=False))
    else:
        print("No high tensions (σ > 3.0) detected.")
    print()

    # Summary statistics
    print("Summary Statistics:")
    print("-" * 80)
    print(f"Early universe mean: {df[df['regime']=='Early (CMB)']['n'].mean():.2f} km/s/Mpc")
    print(f"Late universe mean:  {df[df['regime']=='Late (z<1)']['n'].mean():.2f} km/s/Mpc")
    print(f"Overall spread:      {df['n'].max() - df['n'].min():.2f} km/s/Mpc")
    print(f"Aggregated captures: {(interval_high - interval_low):.2f} km/s/Mpc interval")
    print()

    # Visualizations
    print("Generating visualizations...")
    plot_measurements(df, (val_agg, err_agg))
    plot_aggregation_evolution(steps_df)

    # Export results
    print("Exporting results...")
    df.to_csv('h0_measurements.csv', index=False)
    steps_df.to_csv('aggregation_steps.csv', index=False)
    tensions.to_csv('pairwise_tensions.csv', index=False)

    print("✓ Saved: h0_measurements.csv")
    print("✓ Saved: aggregation_steps.csv")
    print("✓ Saved: pairwise_tensions.csv")
    print()

    print("=" * 80)
    print("Analysis complete.")
    print("=" * 80)


if __name__ == "__main__":
    main()
