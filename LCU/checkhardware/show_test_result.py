#!/usr/bin/env python3
"""
# Show logfile
"""
import sys
import os
# import string
# import datetime
# import time

report_dir = ''
conf_file = r'/localhome/stationtest/config/check_hardware.conf'

def print_help():
    """ print help """
    print("possible option for this script")
    print("--------------------------------------------------")
    print("-h            print this help screen")
    print("-L2=2         show last 2 checks from L2 file")
    print("-S=2          show last 2 checks from S file")
    print("-f=filename   full_path_filename, L2 and S are ignored")
    print(" ")
    print(" if no option is given the last check done is used")
    print("--------------------------------------------------")
    sys.exit(0)

args = dict()
for argument in sys.argv[1:]:
    if argument.startswith('-'):
        if '=' in argument:
            option, value = argument.strip()[1:].split('=')
            args[option.strip().upper()] = value.strip()
        else:
            args[argument.strip()[1:].upper()] = '-'

if 'H' in args:
    print_help()
    sys.exit(0)

run_path = r'/opt/stationtest'
if 'P' in args:
    run_path = args.get('P')
lib_path = run_path+r'/lib'
sys.path.insert(0, lib_path)

from checkhardware_lib import *

hostname = get_hostname()
if hostname == 'Unknown':
    sys.exit('hostname unknown')

station_id = hostname.upper()

def main():
    global report_dir

    """ main function """
    conf = TestSettings(filename=conf_file)
    report_dir = conf().as_string('paths.local-report-dir')

    data_sets = []

    if 'F' in args:
        fullfilename = args.get('F')
    else:
        if 'L2' in args:
            testfilename = '%s_L2_StationTestHistory.csv' % station_id
            data_sets.append( ['L2', get_data(testfilename, int(args.get('L2', '1')))] )

        if 'S' in args:
            testfilename = '%s_S_StationTestHistory.csv' % station_id
            data_sets.append( ['S', get_data(testfilename, int(args.get('S', '1')))] )

        if not 'L2' in args and not 'S' in args:
            testfilename = '%s_station_test.csv' % station_id
            data_sets.append( ['', get_data(testfilename, 1)] )

    rcu_x = rcu_y = 0

    _part = ''
    _part_nr = -1

    # print data for all sets
    print("\n\n\n")
    for check_type, data in data_sets:
        message = "STATION-CHECK RESULTS %s for last %s checks" % (check_type, args.get('%s' % check_type, '1'))
        banner_len = 100
        msg_len = len(message)
        print("-" * banner_len)
        print(">" * ((banner_len - msg_len - 6) // 2) + "   %s   " % message + "<" * ((banner_len - msg_len - 6) // 2))
        print("-" * banner_len)

        check_nr = int(args.get('%s' % check_type, '1')) - 1
        for line in data:
            partnumber = -1
            if line[0] == '#':
                continue

            d = line.strip().split(',')
            if len(d) < 4:
                continue
            date = d[0]

            if 'STATION' in line:
                if check_nr:
                    message = "= csv -%s-  (last - %d) =" % (check_type, check_nr)
                else:
                    message = "= csv -%s-  (last) =" % check_type
                print('   ' + '=' * len(message))
                print('   ' + message)
                print('   ' + '=' * len(message))
                check_nr -= 1

            part = d[1]
            if d[2] != '---':
                partnumber = int(d[2])
                if part == 'LBL':
                    if partnumber < 48:
                        print("ERROR: LBL %d NOT a legal partnumber" % partnumber)
                        rcu_x = 0
                        rcu_y = 0
                    else:
                        rcu_x = (partnumber - 48) * 2
                        rcu_y = (partnumber - 48) * 2 + 1
                if part in ('LBH', 'HBA'):
                    rcu_x = partnumber * 2
                    rcu_y = partnumber * 2 + 1

            msg = d[3].strip()
            msg_info = " ".join(d[4:])
            keyvalue = dict()
            for i in range(4, len(d)):
                if d[i].find('=') != -1:
                    key, valstr = d[i].split('=')
                    vallist = valstr.split(' ')
                    if len(vallist) == 1:
                        keyvalue[key] = vallist[0]
                    elif len(vallist) > 1:
                        keyvalue[key] = vallist
                else:
                    keyvalue[d[i]] = '-'

            if part == 'NFO':
                print_info(msg, keyvalue, msg_info)

            if part == 'SPU':
                if part != _part:
                    _part = part
                    hdr = "\n== SPU "
                    print(hdr + "=" * (banner_len - len(hdr)))
                print_spu(partnumber, msg, keyvalue, msg_info)

            if part == 'RSP':
                if part != _part:
                    _part = part
                    hdr = "\n== RSP "
                    print(hdr + "=" * (banner_len - len(hdr)))
                print_rsp(partnumber, msg, keyvalue)

            if part == 'TBB':
                if part != _part:
                    _part = part
                    hdr = "\n== TBB "
                    print(hdr + "="*(banner_len - len(hdr)))
                print_tbb(partnumber, msg, keyvalue)

            if part == 'RCU':
                if part != _part:
                    _part = part
                    hdr = "\n== RCU "
                    print(hdr + "=" * (banner_len - len(hdr)))
                print_rcu(partnumber, msg, keyvalue)

            if part in ('LBL', 'LBH'):
                if part != _part:
                    _part = part
                    if part == 'LBL':
                        hdr = "\n== LBA Low "
                    else:
                        hdr = "\n== LBA High "
                    print(hdr + "=" * (banner_len - len(hdr)))
                print_lba(partnumber, msg, keyvalue, rcu_x, rcu_y)

            if part == 'HBA':
                if part != _part:
                    _part = part
                    hdr = "\n== HBA "
                    print(hdr + "=" * (banner_len - len(hdr)))

                if partnumber != -1 and partnumber != _part_nr:
                    _part_nr = partnumber
                    header = "Tile %d (RCU %d/%d)" % (partnumber, rcu_x, rcu_y)
                    print("\n-- %s %s" % (header, '-' * (banner_len - len(header))))

                print_hba(partnumber, msg, keyvalue, rcu_x, rcu_y)

    #print '\n' + '#' * banner_len


def get_data(filename, n_checks):
    if not filename.startswith('/'):
        if os.path.exists(report_dir):
                fullfilename = os.path.join(report_dir, filename)
        else:
            print("not a valid log dir")
            sys.exit(-1)
    try:
        fd = open(fullfilename, 'r')
        data = fd.readlines()
        fd.close()
    except:
        print("%s not found in %s" % (filename, report_dir))
        sys.exit(-1)

    first_line = 0
    check_cnt  = 0
    for i in range(len(data) - 1, -1, -1):
        line = data[i]
        if line[0] == '#':
            continue
        if 'STATION' in line:
            first_line = i
            check_cnt += 1
        if check_cnt == n_checks:
            break
    return data[first_line:]

def print_info(msg, keyvalue, msg_info):
    """
    print NFO line
    """
    if msg == 'VERSIONS':
        print("Used script versions: checkHardware=%s, test_db=%s, test_lib=%s, search_lib=%s\n" % (
            keyvalue.get('CHECK'), keyvalue.get('DB'), keyvalue.get('TEST'), keyvalue.get('SEARCH')))

    if msg == 'STATION':
        print("-- Station name     : %s" % keyvalue.get('NAME'))

    if msg == 'RUNTIME':
        print("-- Check runtime    : %s .. %s" % (
            keyvalue.get('START').replace('T', ' '), keyvalue.get('STOP'). replace('T', ' ')))

    if msg == 'DRIVER':
        if 'RSPDRIVER' in keyvalue:
            print("-- RSPDriver        : DOWN")
        if 'TBBDRIVER' in keyvalue:
            print("-- TBBDriver        : DOWN")
    if msg == 'BOARD':
        boardstr = ""
        for i in range(24):
            if 'RSP-%d' % i in keyvalue:
                boardstr += "%d, " % i
        print("-- RSP board DOWN   : %s" % boardstr[:-2])
    if msg == 'CHECKS':
        """E5"""
        checks = msg_info.split()
        info1 = []
        info2 = []
        if 'RV' in checks:
            info1.append('RSP-firmware-version')
        if 'TV' in checks:
            info1.append('TB-firmware-version')
        if 'TM' in checks:
            info1.append('TB-memory-check')
        if 'SPU' in checks:
            info2.append('SPU-board-check')
        if 'RBC' in checks:
            info2.append('RSP-board-checks')
        if 'TBC' in checks:
            info2.append('TB-board-checks')
        if len(info1) or len(info2):
            print("-- Checks done      : %s" % ", ".join(info1))
        if len(info2):
            print("                    : %s" % ", ".join(info2))
        info = []
        for mode in '1234567':
            if 'M%s' % mode in checks:
                info.append('Modem')
            if 'SH%s' % mode in checks:
                info.append('Short')
            if 'F%s' % mode in checks:
                info.append('Flat')
            if 'D%s' % mode in checks:
                info.append('Down')
            if 'S%s' % mode in checks:
                info.append('RF')
            if 'O%s' % mode in checks:
                info.append('Oscillation')
            if 'SP%s' % mode in checks:
                info.append('Spurious')
            if 'SN%s' % mode in checks:
                info.append('Summator-noise')
            for check in checks:
                if 'NS%s' % mode in check.split('='):
                    info.append('Noise[%ssec]' % check.split('=')[1])
            if 'E%s' % mode in checks:
                info.append('Elements')
            if len(info):
                print("-- Checks done M%s   : %s" % (mode, ", ".join(info)))
            info = []

    if msg == 'STATISTICS':
        print("-- Bad antennas     :", end=' ')
        if keyvalue.get('BAD_LBL') != '-1':
            print("LBL=%s  " % keyvalue.get('BAD_LBL'), end=' ')
        if keyvalue.get('BAD_LBH') != '-1':
            print("LBH=%s  " % keyvalue.get('BAD_LBH'), end=' ')
        if keyvalue.get('BAD_HBA') != '-1':
            print("HBA=%s  " % keyvalue.get('BAD_HBA'), end=' ')
        if keyvalue.get('BAD_HBA0') != '-1':
            print("HBA0=%s  " % keyvalue.get('BAD_HBA0'), end=' ')
        if keyvalue.get('BAD_HBA1') != '-1':
            print("HBA1=%s  " % keyvalue.get('BAD_HBA1'), end=' ')
        print()

    if msg == 'BADLIST':
        # 20150723,NFO,---,BADLIST,LBL=83 84 94 95
        bad_ant_str = msg_info.replace('=', '(').replace(' ', ',').replace(';', ')   ') + ')'
        print("-- bad-antenna-list : %s" % bad_ant_str)
    return


def print_spu(partnumber, msg, keyvalue, msg_info):
    """
    print SPU line
    """
    if msg == 'VOLTAGE':
        print("    Subrack %1d wrong voltage: %s" % (partnumber, msg_info))
    if msg == 'TEMPERATURE':
        print("    Subrack %1d high temperature: PCB=%s" % (
              partnumber, keyvalue.get('PCB')))
    return


def print_rsp(partnumber, msg, keyvalue):
    """
    print RSP line
    """
    if msg == 'VERSION':
        if 'RSPDRIVER' in keyvalue:
            print("    Wrong RSPDriver version, %s" % keyvalue.get('RSPDRIVER'))
        if 'RSPCTL' in keyvalue:
            print("    Wrong rspctl version, %s" % keyvalue.get('RSPCTL'))
        if 'AP' in keyvalue or 'BP' in keyvalue:
            print("    Board %2d wrong firmware version: AP=%s BP=%s" % (
                partnumber, keyvalue.get('AP'), keyvalue.get('BP')))
    if msg == 'VOLTAGE':
        print("    Board %2d wrong voltage: 1.2V=%s 2.5V=%s 3.3V=%s" % (
              partnumber, keyvalue.get('1.2V'), keyvalue.get('2.5V'), keyvalue.get('3.3V')))
    if msg == 'TEMPERATURE':
        print("    Board %2d high temperature: PCB=%s BP=%s AP0=%s AP1=%s AP2=%s AP3=%s" % (
              partnumber, keyvalue.get('PCB'), keyvalue.get('BP'), keyvalue.get('AP0'), keyvalue.get('AP1'),
              keyvalue.get('AP2'), keyvalue.get('AP3')))
    return


def print_tbb(partnumber, msg, keyvalue):
    """
    print TBB line
    """
    if msg == 'VERSION':
        if 'TBBDRIVER' in keyvalue:
            print("    Wrong TBBDriver version, %s" % keyvalue.get('TBBDRIVER'))
        if 'TBBCTL' in keyvalue:
            print("    Wrong tbbctl version, %s" % keyvalue.get('TBBCTL'))
        if 'TP' in keyvalue or 'MP' in keyvalue:
            print("    Board %2d wrong firmware version: TP=%s MP=%s" % (
                partnumber, keyvalue.get('TP'), keyvalue.get('MP')))
    if msg == 'VOLTAGE':
        print("    Board %2d wrong voltage: 1.2V=%s 2.5V=%s 3.3V=%s" % (
              partnumber, keyvalue.get('1.2V'), keyvalue.get('2.5V'), keyvalue.get('3.3V')))
    if msg == 'TEMPERATURE':
        print("    Board %2d high temperature: PCB=%s TP=%s MP0=%s MP1=%s MP2=%s MP3=%s" % (
              partnumber, keyvalue.get('PCB'), keyvalue.get('TP'), keyvalue.get('MP0'), keyvalue.get('MP1'),
              keyvalue.get('MP2'), keyvalue.get('MP3')))
    if msg == 'MEMORY':
        print("    Board %2d Memory address or dataline error" % partnumber)
    return


def print_rcu(partnumber, msg, keyvalue):
    """
    print RCU line
    """
    if msg == 'BROKEN':
        print("    RCU %d Broken" % partnumber)
    return


def print_lba(partnumber, msg, keyvalue, rcu_x, rcu_y):
    """
    print LBA line
    """
    lba_number = partnumber

    if msg == 'NOSIGNAL':
        print("   NO test signal found")

    if msg == 'TESTSIGNAL':
        print()
        print(" X test done with subband=%s and ref.signal=%sdB" % (
            keyvalue.get('SUBBANDX'), keyvalue.get('SIGNALX')))
        print(" Y test done with subband=%s and ref.signal=%sdB" % (
            keyvalue.get('SUBBANDY'), keyvalue.get('SIGNALY')))

    if msg == 'TOOLOW':
        print("   Average signal strenght Too Low  AVG %sdB" % keyvalue.get('AVG'))

    if msg == 'DOWN':
        print("   Antenna %2d, %-11s, Down: X=%sdB Xoffset=%s  Y=%sdB Yoffset=%s" % (
            lba_number, 'RCU %d/%d' % (rcu_x, rcu_y),
            keyvalue.get('X', ('?',)), keyvalue.get('Xoff', ('?',)),
            keyvalue.get('Y', ('?',)), keyvalue.get('Yoff', ('?',))))

    if msg == 'SHORT':
        if 'Xmean' in keyvalue:
            print("   Antenna %2d, %-7s, X Short: value=%s" % (
                lba_number, 'RCU %d' % rcu_x, keyvalue.get('Xmean')))
        if 'Ymean' in keyvalue:
            print("   Antenna %2d, %-7s, Y Short: value=%s" % (
                lba_number, 'RCU %d' % rcu_y, keyvalue.get('Ymean')))

    if msg == 'FLAT':
        if 'Xmean' in keyvalue:
            print("   Antenna %2d, %-7s, X Flat: value=%s" % (
                lba_number, 'RCU %d' % rcu_x, keyvalue.get('Xmean')))
        if 'Ymean' in keyvalue:
            print("   Antenna %2d, %-7s, Y Flat: value=%s" % (
                lba_number, 'RCU %d' % rcu_y, keyvalue.get('Ymean')))

    if msg == 'OSCILLATION':
        if 'X' in keyvalue or 'Xbands' in keyvalue:
            print("   Antenna %2d, %-7s, X Oscillation" % (lba_number, 'RCU %d' % rcu_x))
        if 'Y' in keyvalue or 'Ybands' in keyvalue:
            print("   Antenna %2d, %-7s, Y Oscillation" % (lba_number, 'RCU %d' % rcu_y))

    if msg == 'LOW_NOISE':
        if 'Xproc' in keyvalue:
            print("   Antenna %2d, %-7s, X Low Noise:  %s%% bad, signal=%sdB, fluctuation=%sdB, limit=%sdB" % (
                lba_number, 'RCU %d' % rcu_x, keyvalue.get('Xproc'), keyvalue.get('Xval'),
                keyvalue.get('Xdiff', '-'), keyvalue.get('Xref')))
        if 'Yproc' in keyvalue:
            print("   Antenna %2d, %-7s, Y Low Noise:  %s%% bad, signal=%sdB, fluctuation=%sdB, limit=%sdB" % (
                lba_number, 'RCU %d' % rcu_y, keyvalue.get('Yproc'), keyvalue.get('Yval'),
                keyvalue.get('Ydiff', '-'), keyvalue.get('Yref')))

    if msg == 'HIGH_NOISE':
        if 'Xproc' in keyvalue:
            print("   Antenna %2d, %-7s, X High Noise: %s%% bad, signal=%sdB, fluctuation=%sdB, limit=%sdB" % (
                lba_number, 'RCU %d' % rcu_x, keyvalue.get('Xproc'), keyvalue.get('Xval'),
                keyvalue.get('Xdiff', '-'), keyvalue.get('Xref')))
        if 'Yproc' in keyvalue:
            print("   Antenna %2d, %-7s, Y High Noise: %s%% bad, signal=%sdB, fluctuation=%sdB, limit=%sdB" % (
                lba_number, 'RCU %d' % rcu_y, keyvalue.get('Yproc'), keyvalue.get('Yval'),
                keyvalue.get('Ydiff', '-'), keyvalue.get('Yref')))

    if msg == 'JITTER':
        if 'Xdiff' in keyvalue:
            print("   Antenna %2d, %-7s, X Jitter:     %s%% bad, fluctuation=%sdB, normal=%sdB" % (
                lba_number, 'RCU %d' % rcu_x, keyvalue.get('Xproc', '-'),
                keyvalue.get('Xdiff'), keyvalue.get('Xref')))
        if 'Ydiff' in keyvalue:
            print("   Antenna %2d, %-7s, Y Jitter:     %s%% bad, fluctuation=%sdB, normal=%sdB" % (
                lba_number, 'RCU %d' % rcu_y, keyvalue.get('Yproc', '-'),
                keyvalue.get('Ydiff'), keyvalue.get('Yref')))

    if msg == 'SPURIOUS':
        if 'X' in keyvalue:
            print("   Antenna %2d, %-7s, X Spurious signals" % (lba_number, 'RCU %d' % rcu_x))
        if 'Y' in keyvalue:
            print("   Antenna %2d, %-7s, Y Spurious signals" % (lba_number, 'RCU %d' % rcu_y))

    if msg == 'FAIL' or msg == 'RF_FAIL':
        if 'X' in keyvalue:
            print("   Antenna %2d, %-7s, X RF fail:    signal=%sdB" % (
                lba_number, 'RCU %d' % rcu_x, keyvalue.get('X')))
        if 'Y' in keyvalue:
            print("   Antenna %2d, %-7s, Y RF fail:    signal=%sdB" % (
                lba_number, 'RCU %d' % rcu_y, keyvalue.get('Y')))


def print_hba(partnumber, msg, keyvalue, rcu_x, rcu_y):
    """
    print HBA line
    """
    _c_summator_defect = 0
    if msg == 'NOSIGNAL':
        print("   NO test signal found")

    if msg == 'MODEM':
        for i in range(1, 17, 1):
            key = "E%02d" % i
            if key in keyvalue:
                print("   E%02d modem fault (%s)" % (i, keyvalue[key]))

    if msg == 'OSCILLATION':
        if 'X' in keyvalue or 'Xbands' in keyvalue:
            print("   X Oscillation")
        if 'Y' in keyvalue or 'Ybands' in keyvalue:
            print("   Y Oscillation")

    if msg == 'C_SUMMATOR':
        _c_summator_defect = 1
        print("   Modem errors (all elements)")

    if msg == 'P_SUMMATOR':
        print("   No RF all elements")

    if msg == 'SUMMATOR_NOISE':
        if 'X' in keyvalue:
            print("   X Summator noise")
        if 'Y' in keyvalue:
            print("   Y Summator noise")

    if msg == 'SPURIOUS':
        if 'X' in keyvalue:
            print("   X Spurious signals")
        if 'Y' in keyvalue:
            print("   Y Spurious signals")

    if msg == 'LOW_NOISE':
        if 'Xproc' in keyvalue:
            print("   X Low Noise:  %s%% bad, signal=%sdB, fluctuation=%sdB, limit=%sdB" % (
                keyvalue.get('Xproc'), keyvalue.get('Xval'), keyvalue.get('Xdiff', '-'), keyvalue.get('Xref')))
        if 'Yproc' in keyvalue:
            print("   Y Low Noise:  %s%% bad, signal=%sdB, fluctuation=%sdB, limit=%sdB" % (
                keyvalue.get('Yproc'), keyvalue.get('Yval'), keyvalue.get('Ydiff', '-'), keyvalue.get('Yref')))

    if msg == 'HIGH_NOISE':
        if 'Xproc' in keyvalue:
            print("   X High Noise: %s%% bad, signal=%sdB, fluctuation=%sdB, limit=%sdB" % (
                keyvalue.get('Xproc'), keyvalue.get('Xval'), keyvalue.get('Xdiff', '-'), keyvalue.get('Xref')))
        if 'Yproc' in keyvalue:
            print("   Y High Noise: %s%% bad, signal=%sdB, fluctuation=%sdB, limit=%sdB" % (
                keyvalue.get('Yproc'), keyvalue.get('Yval'), keyvalue.get('Ydiff', '-'), keyvalue.get('Yref')))

    if msg == 'JITTER':
        if 'Xdiff' in keyvalue:
            print("   X Jitter:     %s%% bad, fluctuation=%sdB, normal=%sdB" % (
                keyvalue.get('Xproc'), keyvalue.get('Xdiff'), keyvalue.get('Xref')))
        if 'Ydiff' in keyvalue:
            print("   Y Jitter:     %s%% bad, fluctuation=%sdB, normal=%sdB" % (
                keyvalue.get('Yproc'), keyvalue.get('Ydiff'), keyvalue.get('Yref')))

    if msg == 'RF_FAIL' or msg == 'RF_TILE_FAIL':
        if 'X' in keyvalue:
            signal_128, sb_128, ref_128, signal_253, sb_253, ref_253 = keyvalue.get('X')
            print("   X RF Fail:    ", end=' ')
            print("no-delay(test=%5.1fdB ref=%5.1fdB sb=%d)  " % (
                float(signal_128), float(ref_128), int(sb_128)), end=' ')
            print("full-delay(test=%5.1fdB ref=%5.1fdB sb=%d)" % (
                float(signal_253), float(ref_253), int(sb_253)))
        if 'Y' in keyvalue:
            signal_128, sb_128, ref_128, signal_253, sb_253, ref_253 = keyvalue.get('Y')
            print("   Y RF Fail:    ", end=' ')
            print("no-delay(test=%5.1fdB ref=%5.1fdB sb=%d)  " % (
                float(signal_128), float(ref_128), int(sb_128)), end=' ')
            print("full-delay(test=%5.1fdB ref=%5.1fdB sb=%d)" % (
                float(signal_253), float(ref_253), int(sb_253)))

    if msg == 'E_FAIL':
        # loop over number of elements
        for i in range(1, 17, 1):
            if _c_summator_defect:
                continue

            if 'M%d' % i in keyvalue or 'X%d' % i in keyvalue or 'Y%d' % i in keyvalue \
                    or 'OX%d' % i in keyvalue or 'OY%d' % i in keyvalue \
                    or 'SPX%d' % i in keyvalue or 'SPY%d' % i in keyvalue \
                    or 'LNX%d' % i in keyvalue or 'HNX%d' % i in keyvalue or 'JX%d' % i in keyvalue \
                    or 'LNY%d' % i in keyvalue or 'HNY%d' % i in keyvalue or 'JY%d' % i in keyvalue:
                print("   Element %d" % i)

            if 'M%d' % i in keyvalue:
                info = keyvalue.get('M%d' % i)
                if info == 'error':
                    print("       Modem error")
                if info == '??':
                    print("       No modem communication")
            else:
                if 'OX%d' % i in keyvalue:
                    print("      X Oscillating")

                if 'OY%d' % i in keyvalue:
                    print("      Y Oscillating")

                if 'SPX%d' % i in keyvalue:
                    print("      X Spurious")

                if 'SPY%d' % i in keyvalue:
                    print("      Y Spurious")

                if 'LNX%d' % i in keyvalue:
                    print("      X Low Noise, signal=%sdB fluctuation=%sdB" % (
                        keyvalue.get('LNX%d' % i)[0], keyvalue.get('LNX%d' % i)[1]))

                if 'HNX%d' % i in keyvalue:
                    print("      X High Noise, signal=%sdB fluctuation=%sdB" % (
                        keyvalue.get('HNX%d' % i)[0], keyvalue.get('HNX%d' % i)[1]))

                if 'JX%d' % i in keyvalue:
                    print("      X Jitter, fluctuation=%sdB" % keyvalue.get('JX%d' % i))

                if 'LNY%d' % i in keyvalue:
                    print("      Y Low Noise, signal=%sdB fluctuation=%sdB" % (
                        keyvalue.get('LNY%d' % i)[0], keyvalue.get('LNY%d' % i)[1]))

                if 'HNY%d' % i in keyvalue:
                    print("      Y High Noise, signal=%sdB fluctuation=%sdB" % (
                        keyvalue.get('HNY%d' % i)[0], keyvalue.get('HNY%d' % i)[1]))

                if 'JY%d' % i in keyvalue:
                    print("      Y Jitter, fluctuation=%sdB" % keyvalue.get('JY%d' % i))

                if 'X%d' % i in keyvalue:
                    signal_128, sb_128, ref_128, signal_253, sb_253, ref_253 = keyvalue.get('X%d' % i)
                    print("      X RF Fail:  ", end=' ')
                    print("no-delay(test=%5.1fdB ref=%5.1fdB sb=%d)  " % (
                        float(signal_128), float(ref_128), int(sb_128)), end=' ')
                    print("full-delay(test=%5.1fdB ref=%5.1fdB sb=%d)" % (
                        float(signal_253), float(ref_253), int(sb_253)))

                if 'Y%d' % i in keyvalue:
                    signal_128, sb_128, ref_128, signal_253, sb_253, ref_253 = keyvalue.get('Y%d' % i)
                    print("      Y RF Fail:  ", end=' ')
                    print("no-delay(test=%5.1fdB ref=%5.1fdB sb=%d)  " % (
                        float(signal_128), float(ref_128), int(sb_128)), end=' ')
                    print("full-delay(test=%5.1fdB ref=%5.1fdB sb=%d)" % (
                        float(signal_253), float(ref_253), int(sb_253)))


if __name__ == '__main__':
    main()
