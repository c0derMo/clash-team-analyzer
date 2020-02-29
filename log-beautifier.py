fn = input("Please enter the log path:")

f = open(fn, "r")
foutput = open(fn + "-beautified", "w")

for line in f.readlines():
    # Remove all PIP Outputs
    if not "Requirement" in line:
        if not "pip" in line:
            # Remove socket-io posts & gets
            if not "socket.io" in line:
                # Remove favicon requests
                if not "favicon.ico" in line:
                    # Remove logo requests
                    if not "clash.png" in line:
                        # Remove assets requests
                        if not "assets" in line:
                            # Line is fine, we can write it.
                            foutput.write(line)

f.close()
foutput.close()
print("Done!")