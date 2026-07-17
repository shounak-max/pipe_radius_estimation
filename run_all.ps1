$ErrorActionPreference = "Stop"

Write-Host "=========================================================="
Write-Host " Running Complete Pipe Radius Estimation Pipeline"
Write-Host "=========================================================="

$python_exe = ".\.venv\Scripts\python.exe"

if (-not (Test-Path $python_exe)) {
    Write-Host "Virtual environment python executable not found at $python_exe!" -ForegroundColor Red
    Write-Host "Please ensure your virtual environment is properly set up."
    exit 1
}

Write-Host "`n[1/3] Running Simulation Ablation Pipeline..." -ForegroundColor Cyan
& $python_exe src/pipe_estimation/run_pipeline.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Pipeline failed!" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "`n[2/3] Running Monte Carlo Experiments and Generating Plots..." -ForegroundColor Cyan
& $python_exe src/pipe_estimation/plot_results.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Plot generation failed!" -ForegroundColor Red
    exit $LASTEXITCODE
}
Write-Host "Plots generated successfully in output/plots/" -ForegroundColor Green

Write-Host "`n[3/3] Running Blender Dataset Generation..." -ForegroundColor Cyan
try {
    # Try to find Blender executable
    $blender_exe = $null
    if (Get-Command blender -ErrorAction SilentlyContinue) {
        $blender_exe = "blender"
    } elseif (Test-Path "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe") {
        $blender_exe = "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
    } elseif (Test-Path "C:\Program Files\Blender Foundation\Blender 4.3\blender.exe") {
        $blender_exe = "C:\Program Files\Blender Foundation\Blender 4.3\blender.exe"
    }

    if ($null -ne $blender_exe) {
        Write-Host "Found Blender at: $blender_exe" -ForegroundColor Green
        

        Write-Host "`n  -> Running complete PipeGenBench dataset generation..."
        & $blender_exe --background --python-exit-code 1 --python PipeGenBench/run_benchmark.py
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  [!] PipeGenBench generation failed!" -ForegroundColor Red
        } else {
            Write-Host "  [+] PipeGenBench dataset generated successfully!" -ForegroundColor Green
        }
    } else {
        Write-Host "Skipping Blender step: 'blender' could not be found." -ForegroundColor Yellow
        Write-Host "Please add it to PATH or install it in the default Program Files directory."
    }
} catch {
    Write-Host "Skipping Blender step: $_" -ForegroundColor Yellow
}

Write-Host "`n=========================================================="
Write-Host " Pipeline Execution Complete."
Write-Host "=========================================================="
