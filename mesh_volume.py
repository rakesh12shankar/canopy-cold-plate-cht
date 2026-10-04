workflow.TaskObject['Add Boundary Layers'].Arguments.update_dict({'NumberOfLayers':LAYERS,'Rate':1.2,'BLRegionList':['fluid_water'],'FaceScope':{'GrowOn':'only-walls','RegionsType':'fluid-regions'}})
workflow.TaskObject['Add Boundary Layers'].InsertCompoundChildTask();workflow.TaskObject['smooth-transition_1'].Execute()
workflow.TaskObject['Generate the Volume Mesh'].Arguments.update_dict({'VolumeFill':'polyhedra'})
workflow.TaskObject['Generate the Volume Mesh'].Execute();meshing.tui.mesh.check_mesh()
(ROOT/f'{CASE}_workflow.json').write_text(json.dumps(workflow.get_state(),indent=2))
time.sleep(.5)
trn=(ROOT/f'{CASE}_meshing.trn').read_text(errors='replace');counts={};quality={}
for zone in ['fluid_water','solid_alsi10mg']:
    matches=re.findall(r'\b'+zone+r'\s+\d+\s+\d+\s+([\d.]+)\s+(\d+)',trn)
    assert matches,'Zone quality missing '+zone
    quality[zone]=float(matches[-1][0]);counts[zone]=int(matches[-1][1])
assert min(quality.values())>.1 and sum(counts.values())<2000000
assert workflow.TaskObject['smooth-transition_1'].Arguments.get_state()['NumberOfLayers']==LAYERS
(ROOT/f'{CASE}_mesh_checks.json').write_text(json.dumps({'cells':counts,'minimum_orthogonal_quality':quality,'layers':LAYERS},indent=2))
meshing.tui.file.write_mesh('"'+str(ROOT/f'{CASE}_mm.msh.h5').replace('\\','/')+'"')
solver=meshing.switch_to_solver();solver.transcript.start(str(ROOT/f'{CASE}_meshcheck.trn'))
solver.tui.mesh.check();solver.file.write_case(file_name=str(ROOT/f'{CASE}_Mesh_SI.cas.h5'))
solver.exit();del solver
print('MESH_SAVED',CASE,counts,quality,flush=True)
