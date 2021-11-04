from __future__ import print_function
import sys
import subprocess
import time
import os.path as osp
import os
import csv
from dataformatter import DataFormatter

    
def main() :
    if len(sys.argv) < 3:
        print( 'Arguments missing: Temperature and Path to folder holding fw-test.exe')
        exit(0)
    T = int(sys.argv[1])
    exeDir = sys.argv[2]
    if not osp.exists( osp.join( exeDir, 'fw-test.exe')) :
        print( 'fw-test.exe not found in', exeDir)
        exit(0)

    versionOut = subprocess.check_output([osp.join(exeDir, 'fw-test.exe'), '--get_version'], stderr=subprocess.STDOUT)
    tankless = None
    for line in versionOut.splitlines():
        pieces = line.split(':')
        if len(pieces) < 4 : continue
        if pieces[3].strip() == 'FW' :
            tankless = int(pieces[4].strip()[0]) > 3
            break
    if not tankless :
        print( 'No FW version found.')
        exit(1)
    datetime_stamp  = '{}-{:02d}-{:02d}_{:02d}{:02d}{:02d}'.format(*time.localtime())
    outFile = open( 'fd_test_{0:+d}C_{1:s}.csv'.format( T, datetime_stamp), 'w')
    formatter = DataFormatter( tankless, outFile, time.time())
    formatter.writeHeader()
    while True :
        s = raw_input( 'Press Enter when ready with the next sensor or "q" to quit: ')
        if s == 'Q' or s == 'q' :
            break

        versionOut = subprocess.check_output([osp.join(exeDir, 'fw-test.exe'), '--get_version'], stderr=subprocess.STDOUT)
        uniqueName = None
        for line in versionOut.splitlines():
            pieces = line.split(':')
            if len(pieces) < 4 : continue
            if pieces[3].strip() == 'substrate uuid' :
                uniqueName = pieces[4].strip()
                break
        if not uniqueName :
            print( 'No substrate uuid found.')
            exit(1)

        print( 'Keep your finger off the sensor.')
        scanOutput = subprocess.check_output(
            [
                osp.join(exeDir, 'fw-test.exe'), 
                '--scan', 
                '{0:s}_{1:+d}C_air_default'.format(uniqueName, T), 
                'stats={0:s}_{1:+d}C_air_default_stats.csv'.format(uniqueName,T), 
                'csv=yes'
            ], 
            stderr=subprocess.STDOUT)
        fdDataBuffer = subprocess.check_output([osp.join(exeDir, 'fw-test.exe'), '--fd_test'], stderr=subprocess.STDOUT)
        formatter.writeData( fdDataBuffer, uniqueName, 'air\n')
        scanOutput = subprocess.check_output(
            [
                osp.join(exeDir, 'fw-test.exe'), 
                '--scan', 
                '{0:s}_{1:+d}C_air_scan_mode=0x000'.format(uniqueName, T), 
                'stats={0:s}_{1:+d}C_air_scan_mode=0x000_stats.csv'.format(uniqueName, T), 
                'csv=yes', 
                'scan_mode=0x0'
            ], 
            stderr=subprocess.STDOUT)
        scanOutput = subprocess.check_output(
            [
                osp.join(exeDir, 'fw-test.exe'), 
                '--scan', 
                '{0:s}_{1:+d}C_air_scan_mode=0x200'.format(uniqueName, T), 
                'stats={0:s}_{1:+d}C_air_scan_mode=0x200_stats.csv'.format(uniqueName, T), 
                'csv=yes', 
                'scan_mode=0x200'
            ], 
            stderr=subprocess.STDOUT)
        
        raw_input( '\nPress Enter, pause for a second or two and then touch the sensor with 100% coverage.')
        try:
            scanOutput = subprocess.check_output(
                [
                    osp.join(exeDir, 'fw-test.exe'), 
                    '--scan', 
                    '{0:s}_{1:+d}C_full_default'.format(uniqueName, T), 
                    'finger_on', 
                    'stats={0:s}_{1:+d}C_full_default_stats.csv'.format(uniqueName, T), 
                    'csv=yes', 
                    'timeout=8000'
                ], 
                stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as error:
            if error.returncode == 1:
                print( error.output)
                print('Keep your finger in place a little longer.')
                scanOutput = subprocess.check_output(
                    [
                        osp.join(exeDir, 'fw-test.exe'), 
                        '--scan', 
                        '{0:s}_{1:+d}C_full_live_default'.format(uniqueName, T), 
                        'live', 
                        'stats={0:s}_{1:+d}C_full_live_default_stats.csv'.format(uniqueName, T), 
                        'csv=yes'
                    ], 
                    stderr=subprocess.STDOUT)
                fdDataBuffer = subprocess.check_output([osp.join(exeDir, 'fw-test.exe'), '--fd_test'], stderr=subprocess.STDOUT)
                formatter.writeData( fdDataBuffer, uniqueName, 'full\n')
                scanOutput = subprocess.check_output(
                    [
                        osp.join(exeDir, 'fw-test.exe'), 
                        '--scan', 
                        '{0:s}_{1:+d}C_full_live_scan_mode=0x000'.format(uniqueName, T), 
                        'live', 
                        'stats={0:s}_{1:+d}C_full_live_scan_mode=0x000_stats.csv'.format(uniqueName, T), 
                        'csv=yes', 
                        'scan_mode=0x0'
                    ], 
                    stderr=subprocess.STDOUT)
                scanOutput = subprocess.check_output(
                    [
                        osp.join(exeDir, 'fw-test.exe'), 
                        '--scan', 
                        '{0:s}_{1:+d}C_full_live_scan_mode=0x200'.format(uniqueName, T), 
                        'live', 
                        'stats={0:s}_{1:+d}C_full_live_scan_mode=0x200_stats.csv'.format(uniqueName, T), 
                        'csv=yes', 
                        'scan_mode=0x200'
                    ], 
                    stderr=subprocess.STDOUT)
            else:
                print('Unexpected error in fw-test --scan. Exiting.')
                exit(1)
        else :
            fdDataBuffer = subprocess.check_output([osp.join(exeDir, 'fw-test.exe'), '--fd_test'], stderr=subprocess.STDOUT)
            formatter.writeData( fdDataBuffer, uniqueName, 'full\n')
            scanOutput = subprocess.check_output(
                [
                    osp.join(exeDir, 'fw-test.exe'), 
                    '--scan', 
                    '{0:s}_{1:+d}C_full_scan_mode=0x000'.format(uniqueName, T), 
                    'finger_on', 
                    'stats={0:s}_{1:+d}C_full_scan_mode=0x000_stats.csv'.format(uniqueName, T), 
                    'csv=yes', 
                    'scan_mode=0x0',
                    'timeout=3000'
                ], 
                stderr=subprocess.STDOUT)
            scanOutput = subprocess.check_output(
                [
                    osp.join(exeDir, 'fw-test.exe'), 
                    '--scan', 
                    '{0:s}_{1:+d}C_full_scan_mode=0x200'.format(uniqueName, T), 
                    'finger_on', 
                    'stats={0:s}_{1:+d}C_full_scan_mode=0x200_stats.csv'.format(uniqueName, T), 
                    'csv=yes', 
                    'scan_mode=0x200',
                    'timeout=3000'
                ], 
                stderr=subprocess.STDOUT)
        print('Remove your finger.')

        raw_input( 'Press Enter, pause for a second or two and then touch the sensor with 50% coverage.')
        try:
            scanOutput = subprocess.check_output(
                [
                    osp.join(exeDir, 'fw-test.exe'), 
                    '--scan', 
                    '{0:s}_{1:+d}C_partial_default'.format(uniqueName, T), 
                    'finger_on', 
                    'stats={0:s}_{1:+d}C_partial_default_stats.csv'.format(uniqueName, T), 
                    'csv=yes', 
                    'timeout=8000'
                ], 
                stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as error:
            if error.returncode == 1:
                print( error.output)
                print('Keep your finger in place a little longer.')
                scanOutput = subprocess.check_output(
                    [
                        osp.join(exeDir, 'fw-test.exe'), 
                        '--scan', 
                        '{0:s}_{1:+d}C_partial_live_default'.format(uniqueName, T), 
                        'live', 
                        'stats={0:s}_{1:+d}C_partial_live_default_stats.csv'.format(uniqueName, T), 
                        'csv=yes'
                    ], 
                    stderr=subprocess.STDOUT)
                fdDataBuffer = subprocess.check_output([osp.join(exeDir, 'fw-test.exe'), '--fd_test'], stderr=subprocess.STDOUT)
                formatter.writeData( fdDataBuffer, uniqueName, 'partial\n')
                scanOutput = subprocess.check_output(
                    [
                        osp.join(exeDir, 'fw-test.exe'), 
                        '--scan', 
                        '{0:s}_{1:+d}C_partial_live_scan_mode=0x000'.format(uniqueName, T), 
                        'live', 
                        'stats={0:s}_{1:+d}C_partial_live_scan_mode=0x000_stats.csv'.format(uniqueName, T), 
                        'csv=yes', 
                        'scan_mode=0x0'
                    ], 
                    stderr=subprocess.STDOUT)
                scanOutput = subprocess.check_output(
                    [
                        osp.join(exeDir, 'fw-test.exe'), 
                        '--scan', 
                        '{0:s}_{1:+d}C_partial_live_scan_mode=0x200'.format(uniqueName, T), 
                        'live', 
                        'stats={0:s}_{1:+d}C_partial_live_scan_mode=0x200_stats.csv'.format(uniqueName, T), 
                        'csv=yes', 
                        'scan_mode=0x200'
                    ], 
                    stderr=subprocess.STDOUT)
            else:
                print('Unexpected error in fw-test --scan. Exiting.')
                exit(1)
        else :
            fdDataBuffer = subprocess.check_output([osp.join(exeDir, 'fw-test.exe'), '--fd_test'], stderr=subprocess.STDOUT)
            formatter.writeData( fdDataBuffer, uniqueName, 'partial\n')
            scanOutput = subprocess.check_output(
                [
                    osp.join(exeDir, 'fw-test.exe'), 
                    '--scan', 
                    '{0:s}_{1:+d}C_partial_scan_mode=0x000'.format(uniqueName, T), 
                    'finger_on', 
                    'stats={0:s}_{1:+d}C_partial_scan_mode=0x000_stats.csv'.format(uniqueName, T), 
                    'csv=yes', 
                    'scan_mode=0x0',
                    'timeout=3000'
                ], 
                stderr=subprocess.STDOUT)
            scanOutput = subprocess.check_output(
                [
                    osp.join(exeDir, 'fw-test.exe'), 
                    '--scan', 
                    '{0:s}_{1:+d}C_partial_scan_mode=0x200'.format(uniqueName, T), 
                    'finger_on', 
                    'stats={0:s}_{1:+d}C_partial_scan_mode=0x200_stats.csv'.format(uniqueName, T), 
                    'csv=yes', 
                    'scan_mode=0x200',
                    'timeout=3000'
                ], 
                stderr=subprocess.STDOUT)
        print( 'Remove your finger.')
    outFile.close()
        

if __name__ == '__main__':
    main()
