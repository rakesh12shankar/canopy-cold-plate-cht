"""Build repository documentation from completed records, without filling gaps."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parent
def load(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
def write(name,text):(ROOT/name).write_text(text,encoding='utf-8')

def main():
    records=load('results/reference/design_results.json');lookup={r['case']:r for r in records}
    complete='outlet7_refined_equal_power' in lookup and 'outlet7_refined' in lookup
    baseline=lookup['baseline_screen'];screen=lookup['outlet7_screen']
    power_reduction=100*(1-screen['hydraulic_power_W']/baseline['hydraulic_power_W'])
    screen_max=screen['base_max_C']-baseline['base_max_C']
    status=('The refined equal-flow and equal-power comparisons are complete.' if complete else 'Refined equal-flow confirmation is complete; the equal-power comparison is still running.' if 'outlet7_refined' in lookup else 'The refined equal-flow and equal-power comparisons are still running. No refined design benefit is claimed yet.')
    final=''
    if complete:
        ref=lookup['baseline_refined'];var=lookup['outlet7_refined'];eq=lookup['outlet7_refined_equal_power']
        final=f"At equal flow, the refined outlet variant changes hydraulic power by {100*(var['hydraulic_power_W']/ref['hydraulic_power_W']-1):+.3f}% and maximum heated-base temperature by {var['base_max_C']-ref['base_max_C']:+.4f} K. At the refined baseline hydraulic power, achieved flow is {eq['mass_flow_kg_h']:.4f} kg/h; heated-base mean/max change by {eq['base_mean_C']-ref['base_mean_C']:+.4f} / {eq['base_max_C']-ref['base_max_C']:+.4f} K. These are numerical comparisons with volume/cover tradeoffs, rather than experimentally validated hardware improvements."
    uncertainty=''
    if complete:
        uncertainty=f"The outlet's equal-flow mean/max temperature benefit changes from {screen['base_mean_C']-baseline['base_mean_C']:+.4f}/{screen_max:+.4f} K on screening meshes to {var['base_mean_C']-ref['base_mean_C']:+.4f}/{var['base_max_C']-ref['base_max_C']:+.4f} K on refined meshes. Hydraulic-power reduction changes from {power_reduction:.3f}% to {100*(1-var['hydraulic_power_W']/ref['hydraulic_power_W']):.3f}%. The maximum-temperature and power benefits persist across these two resolutions; the smaller mean-temperature benefit is more sensitive. This comparison mixes mesh and algorithm changes, so it is sensitivity evidence, not a formal discretization-error estimate or confidence interval."
    table='\n'.join(f"| {r['case']} | {r.get('cells','')} | {r['mass_flow_kg_h']:.4f} | {r['base_mean_C']:.4f} | {r['base_max_C']:.4f} | {r['static_dp_Pa']:.4f} | {r['total_pressure_loss_Pa']:.4f} | {r['hydraulic_power_W']*1000:.5f} |" for r in records)
    write('docs/results_overview.md',f'''# Results overview

{status}

The matched screening comparison selects the enlarged outlet manifold: hydraulic power falls {power_reduction:.3f}% and maximum heated-base temperature changes {screen_max:+.4f} K. The inlet enlargement has a different mean-temperature tradeoff. These are screening findings, not proof of mesh-independent optimization.

| Case | Cells | Flow (kg/h) | Base mean (°C) | Base max (°C) | Static Δp (Pa) | Total loss (Pa) | Hydraulic power (mW) |
|---|---:|---:|---:|---:|---:|---:|---:|
{table}

{final}

{uncertainty}

![Refined comparison](../results/reference/figures/manifold_refined.png)

![Screening comparison](../results/reference/figures/manifold_screening.png)

The finest independent pipe check gives 0.01985% pressure-drop error and 0.03482% bulk-temperature-rise error. Its pressure resistance has observed order 1.952. Thermal errors are nonmonotonic; a thermal GCI is not claimed.

See [design study](design_study.md), [pipe verification](pipe_verification.md), [mesh sensitivity](mesh_sensitivity.md), and [branch diagnostics](branch_diagnostics.md). Compact solver records and the physics audit accompany these findings.
''')
    write('docs/technical_report.md',f'''# Canopy cold-plate conjugate heat-transfer study

## Research question

Can increasing one internal manifold diameter reduce resistance and heated-base temperature at fixed flow, and can the resistance benefit improve cooling at fixed hydraulic power? The independent numerical design study can proceed without the paper authors' exact CAD. Its literature comparison remains a reconstruction with explicitly missing inputs.

## Geometry and source separation

The reference is Guil-Pedrosa et al., International Journal of Thermal Sciences 214 (2025), 109918, [DOI](https://doi.org/10.1016/j.ijthermalsci.2025.109918). Table 2's Mesh 5 N4 case supplies rounded comparison values: 22.3 kg/h, inlet 23 °C, 200 W, ambient 24 °C; static pressure difference 81.3 Pa, top mean/max 37.7/42.9 °C and outlet 31.2 °C. The outlet averaging method is unspecified. These numbers do not prescribe all geometry and solver implementation details.

Reconstructed plate: 150 × 150 × 10 mm, D6 trunks at x=25/125 mm and z=5 mm. Four branches connect the trunks at y=25,58.333333,91.666667,125 mm, with diameters 3.1,3.7,4.4,4.9 mm. Sharp unions and flat terminal faces are retained. Exact original fillets, unrounded dimensions and material functions are unavailable.

Inlet7/Outlet7 enlarge the selected internal trunk to D7 over y=10–125 mm, retaining the D6 external port. Plate dimensions and branches are fixed. Coolant CAD volume rises approximately 9.6%; minimum nominal cover decreases from 2 to 1.5 mm. The sharp diameter step is a design assumption. No structural or manufacturing qualification is performed.

## Physical model

Steady 3D pressure-based laminar CHT, double precision, no gravity. Fluid/solid interfaces are coupled and conformal; walls are no-slip. Water viscosity and conductivity use CoolProp HEOS tables at atmospheric pressure over 15–60 °C. Density and cp remain fixed at 23 °C. Anisotropic solid k is 123.4/123.4/131 W/(m K), density 2590 kg/m³ and cp 915 J/(kg K).

The inlet has a parabolic circular profile calibrated to integrated 22.3 kg/h; inlet/backflow temperatures are 296.15 K. Outlet gauge pressure is zero. Bottom heat flux is 8888.8889 W/m², giving 200 W on 0.0225 m². Top ambient is 297.15 K with the source's piecewise natural-convection correlation and fixed 304 K air properties; remaining external surfaces are adiabatic. `config/physics.json` and `water_transport.json` contain executable inputs, including assumptions.

## Numerical verification and definitions

Screening: polyhedral mesh, 0.16–1.2 mm size, curvature 18°, five prism layers at growth 1.2. Confirmation: 0.09–1.2 mm, curvature 9°, eight layers, matching the prior refined baseline's settings. Discretization is second-order pressure/momentum/temperature, least-square gradients, with warped-face correction. Screening uses Coupled; confirmation uses SIMPLEC with tighter active-equation AMG termination. The earlier algorithm comparison showed negligible physical changes at checked converged conditions.

New cases require continuity/momentum residuals ≤1e-6, energy ≤1e-9, mass and heat imbalances <0.01%, and three saved checkpoints with base mean/max ranges ≤0.0001 K and total-pressure-loss range ≤0.01%. The equal-power procedure adjusts flow, freezes the inlet, then reconverges with these checks and ≤0.5% power mismatch. Saved checkpoints may be separated by fewer iterations when Fluent meets its stopping criteria.

Hydraulic power is `abs(mdot)/rho × (mass-weighted inlet total pressure − mass-weighted outlet total pressure)`. It excludes external loop losses and pump efficiency. Static pressure difference is a separate area-average metric. Heated-base resistance is `(base temperature − inlet temperature)/200 W`, using area mean or face maximum as labeled. The paper's top temperatures remain separate.

The analytical pipe case uses an axisymmetric R3 mm, L100 mm pipe, nominal mean U0.1 m/s, inlet 23 °C and wall heat flux 5000 W/m². Three meshes verify interior Poiseuille pressure loss and bulk energy, using each mesh's actual integrated flow. Finest errors are below 0.04%; the energy comparison neglects axial conduction while Fluent retains it. This does not experimentally validate the CHT plate.

## Findings and remaining uncertainty

{status}

The screening outlet enlargement reduces hydraulic power {power_reduction:.3f}% and changes maximum base temperature {screen_max:+.4f} K. {final}

{uncertainty}

The refined reconstruction gives static Δp91.0363 Pa and top mean/max39.2829/44.1829 °C: +11.98% pressure, +1.583 K mean and +1.283 K maximum relative to the rounded source values. This discrepancy is preserved. No parameter fitting is used to claim source reproduction.

The prior layer/surface sensitivity changes oppose one another. No cold-plate GCI or overall mesh-independence claim is made. Screening curved-wall faceting lowers baseline mesh coolant volume roughly 5% versus CAD. Section diagnostics retain area, flow-closure and within-branch interpolation checks. Refined baseline midbranch Reynolds numbers are 507–618, consistent with laminar branches but insufficient to exclude junction recirculation or unsteadiness. Exact source CAD/material functions and raw data remain unavailable.

The load is 0.889 W/cm² over the footprint. This is a thermal-fluid portfolio study, not a demonstrated high-heat-flux compute-hardware cooling product.

## Reproducibility

See [commands and evidence map](reproducibility.md). Original geometry, numerical records and regenerated plots are included. Publisher PDFs, author correspondence, development transcripts, machine/license settings and full native solver binaries are excluded from this source package. Ansys licensing is required for new CFD runs. Source automation and documentation were prepared with AI assistance and checked against saved numerical evidence. No open-source reuse license is selected.
''')
    write('docs/portfolio_summary.md',f'''# Portfolio and resume summary

**Project:** canopy cold-plate conjugate heat-transfer study in SolidWorks, ANSYS Fluent and Python.

Supported resume bullet:

> Developed a SolidWorks–ANSYS Fluent conjugate heat-transfer model of a four-branch liquid cold plate; assessed mesh and water-property sensitivities, quantified branch flow and pressure losses, and independently verified pipe pressure and bulk-energy predictions to within 0.04%.

{status}

{final}

Interview evidence: distinguish numerical verification from experimental validation; explain total versus static pressure loss; show the equal-flow mean/maximum tradeoff and increased coolant-volume/reduced-cover cost; discuss the remaining grid and source-geometry uncertainty. Do not claim exact paper reproduction, fully mesh-independent optimization, or demonstrated high-heat-flux hardware cooling.
''')
    write('docs/milestone_status.md',f'''# Milestone status — 2026-10-04

Completed: reconstructed CAD and two controlled manifold variants; analytical pipe verification on three meshes; prior mesh, material and algorithm sensitivities; refined baseline heated-base and branch diagnostics; matched-flow screening of all three geometries with identical-physics audit.

{status}

Repository preparation: curated config/data/docs/results layout, portable relative inputs, compact-record validation, regenerated screening figure, and an isolated licensed CFD runner. The CLI and helper syntax are checked; the relocated full CFD runner has not yet been executed end to end. Existing numerical records were produced using the same numerical helpers in the original local project.

All six required CHT records and three analytical pipe records are present. Final convergence, balance, stability and branch diagnostics were reviewed; compact-record validation passes. The publication package excludes publisher PDFs, correspondence, license settings and development logs.
''')
    write('README.md',f'''# Canopy Cold Plate CHT — SolidWorks and ANSYS Fluent

A numerical reconstruction of a four-branch liquid cold plate, with analytical verification, mesh/material sensitivity studies and a controlled manifold-design extension.

**Status:** {status}

**Screening result:** the enlarged outlet manifold reduces hydraulic power {power_reduction:.3f}% and maximum heated-base temperature by {-screen_max:.3f} K at 22.3 kg/h on the screening mesh. This adds approximately 9.6% coolant volume and reduces minimum cover from 2 to 1.5 mm. {final}

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
''')
    manifest=[]
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file() or '.generated' in p.parts or '.git' in p.parts or '__pycache__' in p.parts or p.name=='UPLOAD_MANIFEST.json':continue
        manifest.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    write('UPLOAD_MANIFEST.json',json.dumps({'package':'canopy-cold-plate-cht','date':'2026-10-04','comparison_complete':complete,'files':manifest},indent=2)+'\n')
    print('Documentation and manifest refreshed; comparison_complete =',complete)

if __name__=='__main__':main()
