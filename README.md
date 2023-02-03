# azuAntiCheatUpdater

This python srypt needs the following modules to function:  requests, zipfile, json, io, re, os

This simple script does the following:
1. Requests list of mods in a target Modpack on Thunderstore
2. Reads in from a JSON file or asks for input for the user if a given mod should be whitelisted or greylisted
3. Once it has the full set of what is need, it reaches out to Thunderstore and downloads all DLL files for every mod
4. It places the mods in appropriate whitelist or greylist folders
5. It then makes a local JSON file containing the history of the mod, so thgat the user does not need to input on next run

For a clean run you MUST delete the whitelist/greylist folders before running
