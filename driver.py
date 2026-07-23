import os
import subprocess
import sys
import shutil

def main():

    latency_script = "my_echolocation.c"
    latency_executable = "my_echolocation"
    clean_script = "clean.py"
    plot_script = "plot.py"
    model_script = "model.py"
    infer_script = "infer.py"
    test_script = "test_persistence.c"
    test_executable = "test_persistence"

    # === Delete old data, model and plots ===
    if os.path.exists("data/"):
        shutil.rmtree("data") # Delete old data folder along with any data
        os.mkdir("data") # Create new empty data folder

    if os.path.exists("models/"):
        shutil.rmtree("models") # Delete old models folder along with any models
        os.mkdir("models") # Create new empty models folder

    if os.path.exists("plots/"):
        shutil.rmtree("plots") # Delete old plots folder along with any plots
        os.mkdir("plots") # Create new empty plots folder

    # === Compile and run my_echolocation.c to generate new latencies ===
    print(f"\nCompiling '{latency_script}'...")
    compile_result = subprocess.run(
        ["gcc", latency_script, "-o", latency_executable], 
        capture_output=True, 
        text=True
    )
    
    if compile_result.returncode != 0:
        print(f"Compilation failed:\n{compile_result.stderr}")
        sys.exit(1)
    
    print(f"Running '{latency_executable}'...")
    c_output = subprocess.run([f"./{latency_executable}"], capture_output=True, text=True)
    
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
    model_result = subprocess.run([sys.executable, model_script], capture_output=True, text=True)
    #if model_result.stdout: print(model_result.stdout)
    if model_result.stderr: print(f"Model Script Stderr:\n{model_result.stderr}")

    # === Compile and run test_persistence.c ===
    print(f"Compiling '{test_script}'...")
    subprocess.run(["gcc", test_script, "-o", test_executable])
    
    print(f"Running '{test_executable}' to simulate writes...")
    subprocess.run([f"./{test_executable}"])

    # === Run infer.py to check accuracy ===
    print(f"\nRunning '{infer_script}'...")
    infer_result = subprocess.run([sys.executable, infer_script], capture_output=True, text=True)
    if infer_result.stdout: print(infer_result.stdout)
    if infer_result.stderr: print(f"Infer Script Stderr:\n{infer_result.stderr}")

    print("\nWorkflow completed successfully!")

if __name__ == "__main__":
    main()