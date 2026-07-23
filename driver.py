import os
import subprocess
import sys
import shutil

def main():
    raw_latencies = "data/access_times.csv"
    cleaned_latencies = "data/cleaned_access_times.csv"

    latency_gathering_script = "my_echolocation.c"
    c_executable = "my_echolocation"
    run_command = [f"./{c_executable}"]

    clean_script = "clean.py"
    plot_script = "plot.py"
    model_script = "model.py"

    # === Delete old data and plots ===
    shutil.rmtree("data") # Delete old data folder along with any data
    os.mkdir("data") # Create new empty data folder

    shutil.rmtree("plots") # Delete old plots folder along with any plots
    os.mkdir("plots") # Create new empty plots folder

    # === Compile and run my_echolocation.c to generate new latencies ===
    print(f"\nCompiling '{latency_gathering_script}'...")
    compile_result = subprocess.run(
        ["gcc", latency_gathering_script, "-o", c_executable], 
        capture_output=True, 
        text=True
    )
    
    if compile_result.returncode != 0:
        print(f"Compilation failed:\n{compile_result.stderr}")
        sys.exit(1)
    
    print(f"Running '{c_executable}'...")
    c_output = subprocess.run(run_command, capture_output=True, text=True)
    
    # Print outputs from the C program if there are any
    if c_output.stdout:
        print("\n", c_output.stdout)
    if c_output.stderr:
        print(f"\n C Program Stderr:\n{c_output.stderr}")

    if c_output.returncode != 0:
        print(f"\n C program exited with error code {c_output.returncode}")
        sys.exit(1)

    # === Run clean.py to generate cleaned latency data ===
    print(f"Running '{clean_script}'...")
    clean_result = subprocess.run(
        [sys.executable, clean_script], 
        capture_output=True, 
        text=True
    )

    if clean_result.stdout:
        print(clean_result.stdout)
    if clean_result.stderr:
        print(f"Clean Script Stderr:\n{clean_result.stderr}")

    # === Run plot.py to generate data plots ===
    print(f"Running '{plot_script}'...")
    plot_result = subprocess.run(
        [sys.executable, plot_script], 
        capture_output=True, 
        text=True
    )
    
    if plot_result.stdout:
        print(plot_result.stdout)
    if plot_result.stderr:
        print(f"Plot Script Stderr:\n{plot_result.stderr}")

    # === Run model.py to determine clusters ===
    print(f"Running '{model_script}'...")
    model_result = subprocess.run(
        [sys.executable, model_script], 
        capture_output=True, 
        text=True
    )

    if model_result.stdout:
        print(model_result.stdout)
    if model_result.stderr:
        print(f"Model Script Stderr:\n{model_result.stderr}")

    if compile_result.returncode == 0 & c_output.returncode == 0 & clean_result.returncode == 0 & plot_result.returncode == 0 & model_result.returncode == 0:
        print("Workflow completed successfully!")
    else:
        print(f"Plot script exited with error code {plot_result.returncode}")

if __name__ == "__main__":
    main()