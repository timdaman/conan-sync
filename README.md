# conan-sync

This is a utility for sending all the contents of one conan(https://conan.io/) server to another. 
This is helpful when migrating to a new conan server or to create and maintain
a replica of a conan server.

This code is a quick and dirty solution I used to perform a server migration. 
Once that was done I stopped improving the code. The code does not perform
any deletions on any of the remotes and all modifications/uploads are
limited to the destination. 
 
I am offering this in the hopes it will save someone else time doing a 
similar task. I will accept patches to improve it.

## Usage Requirements
* Locally installed conan (old versions my not work)
* Conan remotes configured for the source and destination
* Active log-ins into the remotes with appropriate privileges
* Enough disks-pace, where the script runs, to hold your largest package
* You must use a python3/pip3 conan install


## Limitations
* Recipes are synced even when already present on dest.
* Recipes + Packages are NOT removed to dest if not present on on source.
* This MAY REMOVE DATA from machine it is run on. It uses the local 
computer as a scratch space to move data and cleans up after itself
blindly. Data present before starting may be removed. That being said the 
data can be downloaded from either remote when done syncing.
* This code was not heavily tested nor does it have a test suite. 
I stopped when it worked for me. That being said this should not result 
in data loss (minus previous warning)
* Sometimes `conanfiles` may enforce dependencies on the transfer agent 
causing copies to fail until they are installed on the machine used to
run this script.


## How to use

Ignore upload failures. That way you can get more of the uploads done and
review the logs for the fixes needed.
 
    python3 conan-sync.py --source <source remote> --dest <dest remote> --ignore_failures

Apply the fixes needed. then sync again.
On you second second sync previously uploaded packages will be skipped 
allowing you to redo your previous failures

    python3 conan-sync.py --source <source remote> --dest <dest remote>
    
If your conan command is not in your search path you can specify where to 
find it

    python3 conan-sync.py --source <source remote> --dest <dest remote> --exec $HOME/.bin/conan

