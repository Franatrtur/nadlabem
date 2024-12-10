import psutil

# Get the available memory in bytes
available_memory = psutil.virtual_memory().available

# Convert bytes to MB or GB for easier readability
available_memory_mb = available_memory / (1024 * 1024)  # In MB
available_memory_gb = available_memory / (1024 * 1024 * 1024)  # In GB

print(f"Available Memory: {available_memory_mb:.2f} MB")
print(f"Available Memory: {available_memory_gb:.2f} GB")

logical_cpus = psutil.cpu_count(logical=True)
physical_cpus = psutil.cpu_count(logical=False)

# Get the CPU frequency
cpu_freq = psutil.cpu_freq()

print(f"Logical CPUs: {logical_cpus}")
print(f"Physical CPUs: {physical_cpus}")
print(f"CPU Frequency: {cpu_freq.current:.2f} MHz")