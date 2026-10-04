# Reproduction instructions

## Archived evidence versus new calculations

`results/reference/design_results.json` contains only completed, converged cases. Per-case records contain the raw report definitions, convergence checks, numerical controls, boundary classifications, mesh quality/layers and volumes. `physics_audit.json` checks that the screening cases use identical physics and methods. The older refined baseline uses saved native port reports and an explicitly labeled offline heated-base extraction cross-checked against its native top reports.

`run_validation.py` audits residuals, conservation, physical metric definitions and analytical pipe errors. `run_analysis.py` regenerates a CSV comparison and scientific figures into `.generated/analysis`, without changing the archived records. These are compact-record audits, not new solver runs or experimental validation.

```sh
python -m pip install -r requirements.txt
python run_validation.py
python run_analysis.py
python build_report.py
```

`build_report.py` rewrites the repository's generated narrative documentation and manifest from the archived completed records. Its incomplete-state handling must be retained if results are missing.

## New Fluent simulations

Recorded environment: Windows, Fluent 2024 R1, PyFluent 0.26.0, double precision, one process. Install `requirements-simulation.txt`, ensure Fluent is installed and licensed, and use one Fluent invocation at a time. The resource guard waits for other Fluent workers and sufficient Windows commit capacity without closing applications. Refined jobs can take hours on machines with limited physical RAM.

```sh
python -m pip install -r requirements-simulation.txt
python run_fluent.py --case baseline_screen
python run_fluent.py --case inlet7_screen
python run_fluent.py --case outlet7_screen
python run_fluent.py --case outlet7_refined
python run_fluent.py --case outlet7_refined --equal-power
```

Only the two candidate geometries are screened. The lowest equal-flow hydraulic-power variant is selected for refinement; the recorded winner is Outlet7. No global optimum is asserted. Supplied baseline-refined records supply the equal-power reference, 0.65733685 mW. New results remain in `.generated/fluent`; they do not overwrite `results/reference`.

Mesh generation reads the supplied two-body Parasolid CAD, shares topology, discovers the region labels dynamically, assigns plate/fluid regions and checks named boundary bounds. Fluid/solid volumes and total plate volume are checked before solving. Region identification depends on this two-region plate geometry and the larger exterior surface count of the solid. It is not a general-purpose arbitrary-CAD classifier.

The runtime helpers preserve the numerical workflow used in the local study. Relocated full-run validation is not yet complete. A saved generated case is retained on repeated invocation; deleting or moving generated outputs is a deliberate user action. No restart of a partially converged solve is currently exposed by the public CLI; inspect saved checkpoints before rerunning a failed calculation.

## CAD and pipe mesh

`data/cad/baseline`, `inlet7` and `outlet7` contain native SolidWorks and Parasolid fluid/solid/combined bodies. To regenerate, run the corresponding `build_*_geometry.ps1` with an explicit `-OutputDirectory` pointing inside `.generated/cad`. These scripts target SolidWorks 2019 COM interop/template locations. Adjust installation paths for a different SolidWorks installation. A SolidWorks session may become visible during CAD construction.

`build_pipe_mesh.py` contains the independently constructed axisymmetric Fluent ASCII mesh writer. The complete pipe setup, analytical equations and three-mesh records are documented in `docs/pipe_verification.md`. It is a separate elementary numerical check, not an electronics experiment.

With licensed Fluent and no concurrent Fluent worker, regenerate the independent check using `python run_pipe_verification.py`. Use `--mesh coarse` for a short single-mesh check. Outputs go to `.generated/pipe`. This runner uses the recorded pipe setup and freshly initialized solver; it does not read cold-plate results or fit properties to the reference errors.

## Publication exclusions

The source package includes project-owned CAD, scripts, derived numerical records, the parameter workbook, and original scientific figures. It excludes publisher PDF copies/full-text extracts, author-email drafts, machine/server/license settings, development transcripts, temporary workflow folders, and full native Fluent case/data binaries. Archived binaries remain in the original local study; regenerating them requires licensed Fluent and the documented inputs. No dataset gaps are filled with simulated or guessed measurements.
