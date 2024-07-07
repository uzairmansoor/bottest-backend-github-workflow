import subprocess

rsp = subprocess.run(["netstat", "-ano", "|", "findstr", ":8000"], stdout=subprocess.PIPE)
rsp = rsp.stdout.split()

print(rsp)

rsp = subprocess.run(["taskkill", "/PID", rsp[-1], "/F"])
