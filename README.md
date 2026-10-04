# Canopy Cold Plate CHT — SolidWorks and ANSYS Fluent

A numerical reconstruction of a four-branch liquid cold plate, with analytical verification, mesh/material sensitivity studies and a controlled manifold-design extension.

**Status:** The refined equal-flow and equal-power comparisons are complete.

**Screening result:** the enlarged outlet manifold reduces hydraulic power 10.497% and maximum heated-base temperature by 1.075 K at 22.3 kg/h on the screening mesh. This adds approximately 9.6% coolant volume and reduces minimum cover from 2 to 1.5 mm. At equal flow, the refined outlet variant changes hydraulic power by -10.252% and maximum heated-base temperature by -1.0103 K. At the refined baseline hydraulic power, achieved flow is 23.2010 kg/h; heated-base mean/max change by -0.5921 / -1.4146 K. These are numerical comparisons with volume/cover tradeoffs, rather than experimentally validated hardware improvements.

## Read the project

- [Technical report](docs/technical_report.md): question, methods, results and limitations.
- [Results overview](docs/results_overview.md) and [controlled design study](docs/design_study.md).
- [Reproduction instructions](docs/reproducibility.md): dependencies, commands and evidence map.
- [Portfolio and resume summary](docs/portfolio_summary.md).
- [Milestone status](docs/milestone_status.md).

![Refined manifold comparison](results/reference/figures/manifold_refined.png)

## What is implemented

- Connected SolidWorks solid/fluid CAD, including D7 inlet/outlet manifold variants and supplied Parasolid exports.
- Steady 3D laminar conjugate heat transfer with anisotropic solid conductivity and variable water viscosity/conductivity.
- Prior mesh/prism-layer, property and pressure–velocity algorithm sensitivities.
- Branch-flow and total-pressure diagnostics with section interpolation/closure checks.
- Three-mesh analytical heated-pipe verification: finest pressure/bulk-energy errors below 0.04%.
- Matched-flow geometry screening, refined confirmation and an equal-hydraulic-power continuation, with actual completion status documented above.

## Run

Compact-record analysis requires no Fluent or SolidWorks:

```sh
python -m pip install -r requirements.txt
python run_validation.py
python run_analysis.py
```

New calculations require licensed Fluent 2024 R1 on the recorded Windows workflow:

```sh
python -m pip install -r requirements-simulation.txt
python run_fluent.py --case baseline_screen
```

New outputs go to `.generated/`; archived evidence remains in `results/reference/`. SolidWorks is needed only to regenerate CAD. Consult the reproduction guide before executing the additional cases.

## Evidence and limits

The refined baseline differs from the paper: static pressure difference +11.98%, top mean +1.583 K, top maximum +1.283 K. Exact original CAD, water-property functions and temperature-averaging definitions remain unavailable. Numerical verification does not establish experimental validation. Overall cold-plate mesh independence and a cold-plate GCI are not claimed. The 200 W footprint load is 0.889 W/cm²; it is not a demonstrated high-heat-flux electronics cooling case.

## Source and repository scope

Guil-Pedrosa et al., International Journal of Thermal Sciences 214 (2025), 109918. [DOI](https://doi.org/10.1016/j.ijthermalsci.2025.109918). Water transport tables use [CoolProp](https://coolprop.org/fluid_properties/fluids/Water.html).

`config/` holds assumptions and recorded numerical settings; `data/` holds CAD and the parameter workbook; `docs/` holds methods and interpretation; `results/reference/` holds compact records and figures. Scripts live at the root, following the organization of the companion JT and microchannel repositories. Publisher PDFs, correspondence, temporary files, native solver binaries and license settings are excluded. No open-source license has yet been selected; public visibility does not itself grant general reuse rights.
