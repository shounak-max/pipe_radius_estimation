# Pipe Radius Estimation Pipeline

## PipeGenBench Tests and Binary Artifacts

The `PipeGenBench` test suite (`pytest`) relies on the existence of locally generated binary rendering artifacts (.exr depth maps, .png images, and .ply point clouds) within the `PipeGenBench/output` directories.

These files are ignored in source control (via `.gitignore`) because they are extremely large and change based on the Blender engine settings.

**Before running `pytest` on a fresh clone**, you MUST execute the overarching orchestrator script to regenerate these binary fixtures locally:

```powershell
powershell.exe -File run_all.ps1
```

Or you can regenerate just the `PipeGenBench` benchmark datasets:
```powershell
blender --background --python-exit-code 1 --python PipeGenBench/run_benchmark.py
```
