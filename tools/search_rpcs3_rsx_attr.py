import subprocess

res = subprocess.run(['gh', 'api', 'search/code?q=repo:RPCS3/rpcs3+sys_rsx_context_attribute'], capture_output=True, text=True)
print(res.stdout[:1000])
