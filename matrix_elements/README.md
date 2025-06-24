
## Setup


1. Logging In

We will be working on whatever server you want that **supports CMSSW** in Jupyter Notebooks. This is ideally either lxplus or Fermilab computing.

To that end, we will also initiate them in the server. Login using the following command:

```bash
ssh -L localhost:8888:localhost:8888 <username>@<servername>
```

2. Setting Things Up

Run the following command:

```bash
source setup.sh
```

From there, navigate to this folder, and run the following:

```bash
jupyter notebook --no-browser --port 8888
```

## FAQ

Q: My port isn't forwarding!
A: The port is probably already in use. Try again

Q: My MELA is stuck on a loading screen!
A: Check your symbolic links to see if they match to something by calling `ls -l`. If they don't wipe them away and try again.

Q: My MELA is stuck on calculations!
A: Try just re-initializing your MELA object. If that doesn't work, contact me!

