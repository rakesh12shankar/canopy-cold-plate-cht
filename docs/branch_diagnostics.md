# Finer-mesh water-property sensitivity and branch diagnostics

Both finer cases use the same 1,390,532-cell mesh, 22.3 kg/h inlet flow at 23°C, 200 W bottom heating, 24°C ambient and anisotropic aluminum conductivity. The sensitivity changes only water viscosity and thermal conductivity to temperature-dependent CoolProp HEOS functions at 101325 Pa. Density and heat capacity stay at the baseline 23°C values. The authors’ heated-model property functions remain unconfirmed.

| Case | Pressure drop (Pa) | Mean top (°C) | Maximum top (°C) | Bulk outlet (°C) |
|---|---:|---:|---:|---:|
| Finer, constant properties | 101.4506 | 40.0531 | 45.0491 | 30.6513 |
| Finer, variable viscosity/conductivity | 91.0363 | 39.2829 | 44.1829 | 30.6553 |
| Earlier fine mesh, variable viscosity/conductivity | 89.8891 | 39.5372 | 44.3993 | 30.6546 |
| Paper Table 2, Mesh 5 | 81.3 | 37.7 | 42.9 | 31.2* |

*The paper does not establish the outlet averaging definition; its value should not be treated as a confirmed bulk-temperature target.

On the finer mesh, variable viscosity/conductivity changes pressure by -10.4143 Pa (-10.27%), mean top by -0.7702 K and maximum top by -0.8661 K.
The finer transport case remains +11.98% from the paper pressure, +1.583 K from its mean top temperature and +1.283 K from its maximum.

## Branch flow distribution and sampled branch losses

B1–B4 correspond to y=25, 58.333333, 91.666667 and 125 mm; nominal diameters are 3.1, 3.7, 4.4 and 4.9 mm. Flow travels from x=125 mm toward x=25 mm. Flow fractions use the x=75 mm cuts. Pressure losses cover x=115 to x=35 mm: 80 mm of each branch, including possible developing flow, with junction regions and branch ends excluded.

| Properties | Branch | Flow (kg/h) | Inlet-flow share (%) | Static Δp, 80 mm (Pa) | Total Δp, 80 mm (Pa) |
|---|---|---:|---:|---:|---:|
| Constant | B1 | 3.6819 | 16.511 | 42.7167 | 42.0658 |
| Constant | B2 | 5.0484 | 22.639 | 21.6817 | 36.8447 |
| Constant | B3 | 6.4568 | 28.954 | 10.7949 | 26.8625 |
| Constant | B4 | 7.0556 | 31.639 | 15.2766 | 15.1134 |
| Variable μ/k | B1 | 3.7049 | 16.614 | 35.4203 | 35.7295 |
| Variable μ/k | B2 | 5.0365 | 22.585 | 16.2880 | 33.3589 |
| Variable μ/k | B3 | 6.4350 | 28.856 | 6.9889 | 24.2876 |
| Variable μ/k | B4 | 7.0690 | 31.699 | 12.7354 | 13.0485 |

## Approximate total-pressure loss budget

| Properties | Whole plate (Pa) | Inlet region (Pa) | Sampled branch portions (Pa) | Outlet region (Pa) | Branch portion (%) |
|---|---:|---:|---:|---:|---:|
| Constant | 114.9638 | 45.8987 | 27.9179 | 41.1473 | 24.28 |
| Variable μ/k | 105.8563 | 44.2729 | 24.6755 | 36.9079 | 23.31 |

Total pressure is mass-flow weighted and includes kinetic-energy effects. It differs from the area-averaged static pressure drop used for the paper comparison. Branch weights for the loss budget are normalized by their measured sum, making the regional split independent of pressure reference despite small cut-flow closure errors. The inlet region includes the inlet manifold, splitting junctions and branch portions before x=115 mm; the outlet region includes collecting junctions, the outlet manifold and branch portions after x=35 mm. This budget cannot isolate pure junction losses. Interior cut surfaces are interpolated, so the budget is diagnostic rather than an exact cell-face energy balance.

## Verification and interpretation limits

- constant: sum of branch flows at x=75 mm differs from inlet flow by -0.2570%; maximum within-branch variation across the five cuts is 0.3041%; maximum cut-area difference from nominal circular area is 1.800%.
- transport: sum of branch flows at x=75 mm differs from inlet flow by -0.2452%; maximum within-branch variation across the five cuts is 0.2901%; maximum cut-area difference from nominal circular area is 1.800%.

Transport solve: final iteration 1087, continuity 9.843e-07, energy 6.63e-11; mass imbalance 2.304e-06%, heat imbalance 5.493e-06%.

From the preceding saved checkpoint to the final solution, pressure changed by +0.000098 Pa, mean top by +0.000005 K and maximum top by +0.000000 K.

The fluid temperature range is 23.000 to 41.621°C, within the 15–60°C material tables. A recursive setup comparison confirms that only viscosity and thermal conductivity changed from the baseline.

Cut-area differences reveal the meshed cross-section rather than an exact analytic circle. Flow normalization preserves the imposed total inlet mass flow; it does not remove cross-section discretization effects. These diagnostics do not prove mesh independence or validate the geometry. No geometry or material values were fitted to the paper.

The user reports sending the author-data request. Original CAD, unrounded dimensions, heated-model property functions and report definitions are still awaited.

## Files and sources

- `Finer_Transport_Branch_Diagnostics.json`: compact numeric results and checks.
- `Finer_Transport_Sections.csv`: every sampled section, including manifold stations, pressures, flow and temperature; units appear in column names. Signed flow follows each surface normal, while branch tables use magnitudes.
- `Finer_Transport_Diagnostics.png`: branch-flow and pressure-loss comparison.
- `../03_ANSYS/Canopy_Finer_Transport_Study.wbpj`: Workbench comparison with diagnostic surfaces.
- `../03_ANSYS/Transport_Finer`: solver files, property tables and raw diagnostic records.

Paper: Guil-Pedrosa et al. (2025), https://doi.org/10.1016/j.ijthermalsci.2025.109918, Table 2. Surface integration definitions: https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_th/flu_th_sec_compute_surfint.html
