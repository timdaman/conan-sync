import argparse
import json
import subprocess
import sys

# Parse args
import tempfile

parser = argparse.ArgumentParser()
parser.add_argument('--source', type=str, required=True,
                    help="Name of conan remote from which recipes and packages are being copied to --dest")
parser.add_argument('--dest', type=str, required=True,
                    help="Name of conan remote receiving all of the contents of --source")
parser.add_argument('--exec', type=str, required=False, default='conan', help="Locations of 'conan' command")
parser.add_argument('--ignore_failures', action='store_true', required=False, help="Ignore failures")

args = parser.parse_args(sys.argv[1:])

source_remote = args.source
dest_remote = args.dest
conan_cmd = args.exec
ignore_failures = args.ignore_failures

CONAN_CMD_TIMEOUT_SECS = 300


def run_conan(args, reraise_error=False):
    try:
        return subprocess.check_output(args=[conan_cmd] + args, timeout=CONAN_CMD_TIMEOUT_SECS)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print("Command failed")
        print(repr(e))
        if hasattr(e, 'returncode'):
            rc = "rc=" + e.returncode
        else:
            rc = "Command timed out"
        print("{} output={}".format(rc, e.output))
        if reraise_error and not ignore_failures:
            raise e


# Check if conan is installed
run_conan([], reraise_error=True)

# get list of recipes on source
raw_source_recipes = run_conan(['search', '-r', source_remote, '*'])
source_recipes = raw_source_recipes.decode('utf8').splitlines()[2:]  # Skip the header lines

package_json = tempfile.NamedTemporaryFile(mode='r', encoding='utf8')

for source_recipe in source_recipes:
    print(source_recipe)
    # Sync recipe over
    run_conan(['download', '-r', source_remote, '--recipe', source_recipe])
    run_conan(['upload', '-r', dest_remote, source_recipe], reraise_error=True)

    # For each recipe get list of packages
    run_conan(['search', '-r', source_remote, '-j', package_json.name, source_recipe])
    package_json.seek(0)
    source_packages = set(package['id'] for package in json.load(package_json)['results'][0]['items'][0]['packages'])

    run_conan(['search', '-r', dest_remote, '-j', package_json.name, source_recipe])
    package_json.seek(0)
    dest_packages = set(package['id'] for package in json.load(package_json)['results'][0]['items'][0]['packages'])

    for source_package in source_packages:
        print(source_package, end='')
        if source_package in dest_packages:  # Already present on dest
            print(": Already present on dest, skipping")
            continue

        # Sync package over
        print(": Syncing to remote")
        run_conan(['download', '-r', source_remote, '-p', source_package, source_recipe])
        run_conan(['upload', '-r', dest_remote, '-p', source_package, source_recipe], reraise_error=True)
        dest_packages.add(source_package)  # prevent double uploads
        # Clean up so we don't fill the drive
        run_conan(['remove', '-p', source_package, '-f', source_recipe])

    run_conan(['remove', '-f', source_recipe])
