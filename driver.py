import os
import subprocess
import sys
import shutil

def main():

    # C script names
    latency_script = "my_echolocation.c"
    test_script = "test_persistence.c"
    # C executable names
    latency_executable = "my_echolocation"
    test_executable = "test_persistence"
    # Python script names
    clean_script = "clean.py"
    plot_script = "plot.py"
    model_script = "model.py"
    infer_script = "infer.py"
    # Folder names
    data_folder = "data"
    model_folder = "models"
    plots_folder = "plots"

    # Delete old data, model and plots
    if os.path.exists(f"{data_folder}/"):
        shutil.rmtree(f"{data_folder}")
    os.mkdir("data") # Create new empty data folder
    if os.path.exists(f"{model_folder}/"):
        shutil.rmtree(f"{model_folder}")
    os.mkdir("models") # Create new empty models folder
    if os.path.exists(f"{plots_folder}/"):
        shutil.rmtree(f"{plots_folder}")
    os.mkdir("plots") # Create new empty plots folder
    
    # Compile latency gathering script
    print(f"\nCompiling '{latency_script}'...")
    compile_result = subprocess.run(
        ["gcc", latency_script, "-o", latency_executable], 
        capture_output=True, 
        text=True
    )
    if compile_result.returncode != 0:
        print(f"Compilation failed:\n{compile_result.stderr}")
        sys.exit(1)
    # Run latency gathering script
    print(f"Running '{latency_executable}'...")
    c_output = subprocess.run([f"./{latency_executable}"], capture_output=True, text=True)
    if c_output.returncode != 0:
            print(f"\nC program exited with error code {c_output.returncode}")
            sys.exit(1)
    # Print output from the latency gathering script
    if c_output.stdout: print("\n", c_output.stdout)
    if c_output.stderr: print(f"\nC Program Stderr:\n{c_output.stderr}")

    # Run cleaning script to remove outliers
    print(f"Running '{clean_script}'...")
    clean_result = subprocess.run(
        [sys.executable, clean_script], 
        capture_output=True, 
        text=True
    )
    # Print output from the cleaning script
    if clean_result.stdout: print("\n", clean_result.stdout)
    if clean_result.stderr: print(f"Clean Script Stderr:\n{clean_result.stderr}")

    # Run plotting script to generate plots
    print(f"\nRunning '{plot_script}'...\n")
    plot_result = subprocess.run(
        [sys.executable, plot_script], 
        capture_output=True, 
        text=True
    )
    # Print output from the plotting script
    if plot_result.stdout: print("\n", plot_result.stdout)
    if plot_result.stderr: print(f"\nPlot Script Stderr:\n{plot_result.stderr}")

    # Run model training script
    print(f"\nRunning '{model_script}'...")
    model_result = subprocess.run([sys.executable, model_script], capture_output=True, text=True)
    # Print outputs from the training script
    if model_result.stdout: print("\n", model_result.stdout)
    if model_result.stderr: print(f"\nModel Script Stderr:\n{model_result.stderr}")

    # Compile test sample generating script
    print(f"\nCompiling '{test_script}'...")
    subprocess.run(["gcc", test_script, "-o", test_executable])
    # Run test sample generating script
    print(f"Running '{test_executable}'...")
    test_samples = subprocess.run([f"./{test_executable}"])
    # Print output from the test sample generating script
    if test_samples.stdout: print("\n", test_samples.stdout)
    if test_samples.stderr: print(f"\nTest Samples Script Stderr:\n{test_samples.stderr}")

    # Run model evaluation script
    print(f"\nRunning '{infer_script}'...")
    infer_result = subprocess.run([sys.executable, infer_script], capture_output=True, text=True)
    # Print output from the evaluation script
    if infer_result.stdout: print("\n", infer_result.stdout)
    if infer_result.stderr: print(f"\nInfer Script Stderr:\n{infer_result.stderr}")

    print("\nWorkflow completed.")

if __name__ == "__main__":
    main()