import subprocess

res = subprocess.run(['gh', 'api', 'search/code?q=repo:RPCS3/rpcs3+L1GPU_CONTEXT_ATTRIBUTE'], capture_output=True, text=True)
print(res.stdout[:1000])
