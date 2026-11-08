import subprocess

res = subprocess.run(['gh', 'api', 'search/code?q=repo:torvalds/linux+lv1_gpu_context_attribute'], capture_output=True, text=True)
print(res.stdout[:1000])
