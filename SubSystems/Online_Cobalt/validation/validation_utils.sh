#
# Useful functions/constants for the validate test scripts
#

#
# special exit codes
#
NEED_ROOT_EXIT_CODE=42
NEED_NON_ROOT_EXIT_CODE=43
INVALID_CLUSTER_EXIT_CODE=44
INVALID_NODE_EXIT_CODE=45
NO_GPU_EXIT_CODE=46
NOT_ON_HEAD_EXIT_CODE=47

check_root_privileges()
{
    # we need to be root! exit with special code $NEED_ROOT_EXIT_CODE otherwise (see validate script).
    if [[ `id -u` -ne 0 ]]; then
        exit $NEED_ROOT_EXIT_CODE
    fi
}

check_non_root_privileges()
{
    # we need not to be root! exit with special code $NEED_NON_ROOT_EXIT_CODE otherwise (see validate script).
    if [[ `id -u` -eq 0 ]]; then
        exit $NEED_NON_ROOT_EXIT_CODE
    fi
}

check_running_on_cep4()
{
    if [[ `hostname -f` != *"cep4.control.lofar" ]]; then
        exit $INVALID_CLUSTER_EXIT_CODE
    fi
}

check_running_on_cobalt2()
{
    if [[ `hostname -f` != "cbm2"* ]]; then
        exit $INVALID_CLUSTER_EXIT_CODE
    fi
}

check_running_on_cobalt2_head()
{
    # early exit if not on cobalt2 cluster
    check_running_on_cobalt2

    if [[ `hostname -f` != "cbm299."* ]]; then
        exit $NOT_ON_HEAD_EXIT_CODE
    fi
}

check_has_nvidia_gpu()
{
    lspci | grep -i nvidia
    if [[ $? -ne 0 ]]; then
        exit $NO_GPU_EXIT_CODE
    fi
}

