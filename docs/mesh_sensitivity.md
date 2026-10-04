# Follow-up mesh diagnostics

All cases use constant water properties at 23°C, 22.3 kg/h flow, 200 W bottom heating, 24°C ambient and the same nominal CAD. These mesh comparisons are separate from the earlier temperature-dependent-property sensitivity.

| Case | Fluid cells | Solid cells | Pressure drop (Pa) | Mean top (°C) | Maximum top (°C) |
|---|---:|---:|---:|---:|---:|
| Five layers, 12 degrees | 340,030 | 322,837 | 100.9957 | 40.2502 | 45.2041 |
| Eight layers, 12 degrees | 480,728 | 322,716 | 102.9814 | 40.2977 | 45.3216 |
| Eight layers, 9 degrees | 887,130 | 503,402 | 101.4506 | 40.0531 | 45.0491 |
| Paper Table 2, Mesh 5 | — | — | 81.3 | 37.7 | 42.9 |

## Changes between successive tests

- Five layers, 12 degrees → Eight layers, 12 degrees: pressure +1.9857 Pa (+1.966%); mean top +0.0475 K; maximum top +0.1175 K.
- Eight layers, 12 degrees → Eight layers, 9 degrees: pressure -1.5308 Pa (-1.487%); mean top -0.2446 K; maximum top -0.2725 K.

The layer and surface refinements change pressure in opposite directions. Close agreement between the first and last cases can therefore reflect partial cancellation, and does not demonstrate mesh independence.

The final constant-property case differs from the paper by +24.79% in pressure, +2.353 K in mean top temperature and +2.149 K in maximum top temperature.

## Conservation and convergence

| Case | Mass imbalance (%) | Heat imbalance (%) |
|---|---:|---:|
| Five layers, 12 degrees | 2.7925e-08 | 1.1007e-07 |
| Eight layers, 12 degrees | 1.3751e-06 | 4.2583e-06 |
| Eight layers, 9 degrees | 1.2867e-07 | 2.1439e-06 |

Baseline_simplec: final iteration 248, continuity 9.84e-07, maximum velocity residual 6.43e-10, energy 1.9e-12.

Prism: final iteration 400, continuity 9.83e-07, maximum velocity residual 2.66e-08, energy 3.94e-11.

Finer: final iteration 629, continuity 9.99e-07, maximum velocity residual 8.75e-09, energy 7.72e-12.

## Solver-algorithm control

The converged five-layer mesh was also continued with SIMPLEC. Relative to its original coupled solution, pressure changed by +0.000002 Pa (+0.000002%), mean top by -0.000000 K, and maximum top by +0.000000 K.
The table above uses this SIMPLEC baseline so all mesh comparisons use the same final coupling algorithm. The original coupled files remain unchanged.

## Scope and limitations

The first test increases the fluid smooth-transition layer count from five to eight at the same surface controls (12-degree curvature, 0.12/1.2 mm minimum/maximum). The second keeps eight layers and refines surface controls to 9 degrees and 0.09/1.2 mm. Prism growth rate stays 1.2. Smooth-transition first-cell heights and layer coverage depend on local geometry and meshing controls; these are controlled sensitivity tests, not a uniform three-grid family for formal GCI.

New meshes are initialized by separate fluid/solid interpolation from a converged case and then solved to the same residual and conservation criteria. Interpolation is only an initialization procedure.

The follow-up cases finish with SIMPLEC pressure–velocity coupling because the coupled solver caused heavy memory paging. Spatial discretization stays second order. Relaxation settings affect iterative convergence, not the specified physical steady-state model; the saved method/control JSON files record the final values.

The authors’ exact CAD, heated-model material functions and outlet averaging remain unresolved. The university repository API lists only the paper PDF in the ORIGINAL bundle, with separate license, text and thumbnail bundles; no CAD/model bundle was listed. Metadata snapshots are saved in `01_Reference`. A request draft is saved but has not been sent. The journal full-text endpoint returned HTTP 403, so publisher supplements remain unverified.

Source: Guil-Pedrosa et al. (2025), DOI https://doi.org/10.1016/j.ijthermalsci.2025.109918, Table 2. University record: https://vivo.uc3m.es/display/act576536.

## Saved artifacts

- `Followup_Mesh_Comparison.png`: comparison chart.
- `../03_ANSYS/Canopy_Convergence_Study.wbpj`: three-case Workbench study.
- `../03_ANSYS/Convergence/Canopy_T2_*`: converged case/data files and verification records.
- `../05_Notes/Author_Data_Request_Draft.md`: unsent request for missing reproduction data.
