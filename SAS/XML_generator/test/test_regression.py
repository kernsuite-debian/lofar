#!/usr/bin/env python3
import sys, os, subprocess, difflib, shutil

# Copied from LCS/PyCommon/subprocess_utils
def _convert_bytes_tuple_to_strings(bytes_tuple):
    """Helper function for subprocess.communicate() and/or subprocess.check_output which changed from python2 to python3.
    This function returns the bytes in the bytes_tuple_tuple to utf-8 strings.
    You can use this to get the "normal" python2 subprocess behaviour back for functions like check_output and/or communicate."""
    return tuple('' if x is None
                 else x.decode('UTF-8') if isinstance(x, bytes)
                 else x
                 for x in bytes_tuple)

def communicate_returning_strings(proc, input=None):
    """Helper function for subprocess.communicate() which changed from python2 to python3.
    This function waits for the subprocess to finish and returns the stdout and stderr as utf-8 strings, just like python2 did."""
    return _convert_bytes_tuple_to_strings(proc.communicate(input=input))


# diff should only be something like:
# 3,5c3,5
# <           <version>2.10.3</version>
# <           <template version="2.10.3" author="Alwin de Jong" changedBy="Alwin de Jong">
# <           <description>XML Template generator version 2.10.3</description>
# ---
# >   <version>2.12.0</version>
# >   <template version="2.12.0" author="Alwin de Jong,Adriaan Renting" changedBy="Adriaan Renting">
# >   <description>XML Template generator version 2.12.0</description>
def checkDiff(diff):
    if len(diff) == 8 or len(diff) == 0:
        return True
    return False


def main(verbose_tests=False, regenerate_golden_output=False):
    '''
    :param verbose_tests: print stdout and stderr of the generator when return code non-zero
    :param regenerate_golden_output: overwrite the golden output files with the current generator output
    '''
    os.chdir('test_regression.in_data')
    infiles = os.listdir("txt")
    results = []
    for infile in infiles:
        if infile.startswith("old") or infile.startswith("."):
            continue  # pre 2.6 files that no longer have valid syntax
        name, ext = os.path.splitext(infile)
        outfile = name + ".xml"
        print("\n")
        print("*** Processing %s ***" % infile)
        cmd = ["xmlgen", "-i", "./txt/%s" % infile, "-o", "test.xml"]
        p = subprocess.Popen(cmd, stdin=open('/dev/null'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = communicate_returning_strings(p)
        if verbose_tests and p.returncode == 1:
            print(out)
            print(err)
        logs = out.splitlines()  # stdout
        print("xmlgen ran with return code: %s" % p.returncode)
        xmlgen = p.returncode
        if p.returncode:
            for l in logs: print(l)
            results.append((infile, xmlgen, -1, False))
            continue
        else:
            cmd = ["diff", "-w", "-I", r"^[[:space:]]*$", "./xml/%s.xml" % name, "test.xml"]
            ## -w ignores differences in whitespace
            ## -I '^[[:space:]]*$' because -B doesn't work for blank lines (on OSX?)
            p = subprocess.Popen(cmd, stdin=open('/dev/null'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logs = communicate_returning_strings(p)
            diffs = logs[0].splitlines()  # stdout
            print("diff reply was %i lines long" % len(diffs))
            check = checkDiff(diffs) and len(logs[1]) == 0
            if not check:
                for l in diffs: print(l)
                print(logs[1])
            results.append((infile, xmlgen, p.returncode, check))

            if regenerate_golden_output:
                testdir = os.environ.get('srcdir', os.path.dirname(os.path.abspath(__file__)))
                outfile = "%s/test_regression.in_data/xml/%s.xml" % (testdir, name)
                print('Overwriting golden XML:', os.path.abspath(outfile))
                shutil.copy('test.xml', outfile)

        os.remove("test.xml")
    print("\nResults:")
    success = True
    for r in results:
        print("%s: xmlgen: %i diff: %i, %s" % r)
        success = success and r[3]
    if success:
        print("success")
        return 0
    else:
        print("failure")
        return 1


if __name__ == "__main__":
    sys.exit(main())
