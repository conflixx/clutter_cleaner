#! /usr/bin/env python3

desc="""This program provides suggestions on how to optimize disk space. You must select a directory and at least one option."""

# TODO: generate pre-canned email showing files that will be deleted
# TODO: add delete option LAST



import os.path
import math
import sys
import hashlib
import time
import optparse
from operator import itemgetter

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


parser = optparse.OptionParser(description=desc)
parser.add_option('-p', '--directory', help='parent directory to start recurisive check <REQUIRED>', action="store", dest='parent_dir')
parser.add_option('-d', '--duplicates', help='find duplicate files', action="store_true", dest='dupe_file')
parser.add_option('-l', '--larger', help='find files larger than [x] bytes', action="store", dest='large_file')
parser.add_option('-o', '--oldfiles', help='find files older than [x] days', action="store", dest='old_file')

(options, args) = parser.parse_args()

if (options.large_file == None and options.dupe_file == None and options.old_file == None):
    print(bcolors.FAIL + "[!] Invalid usage" + bcolors.ENDC)
    parser.print_help()
    sys.exit(-1)

if os.path.isdir(options.parent_dir) == False:
    print(bcolors.FAIL + "[!] Directory doesn't exist or is a file" + bcolors.ENDC)
    parser.print_help()
    sys.exit(-1)

#used to make fileSize readable
def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

def fileLister(dir):

    print('')
    bigData = []
    for folderName, subFolders, fileNames in os.walk(dir):

        print(bcolors.OKBLUE + bcolors.BOLD + '[*]SEARCHING:  ' + folderName + bcolors.ENDC)

        #for subFolder in subFolders:
            #print('SUBFOLDER OF ' + folderName + ': ' + subFolder)

        for fileName in fileNames:
            try:

                filePath = os.path.join(folderName, fileName)
                fileSize = os.path.getsize(filePath)
                fileTime = os.path.getmtime(filePath)
                print(bcolors.WARNING + '[-]PROCESSING: ' + bcolors.ENDC + '%s' % (filePath))
            except Exception as err:
                print(bcolors.FAIL + '[!]FILE ERROR: ' + str(err) + bcolors.ENDC)
            #get file hash
            BLOCKSIZE = 65536
            hasher = hashlib.md5()
            try:

                with open(filePath, 'rb') as afile:
                    buf = afile.read(BLOCKSIZE)

                    while len(buf) > 0 :
                        hasher.update(buf)
                        buf = afile.read(BLOCKSIZE)
                fileHash = hasher.hexdigest()

                #put file info in list
                littleData = [filePath, fileHash, fileSize, fileTime]
                bigData.append(littleData)
            except Exception as err:
                print(bcolors.FAIL + '[!]FILE ERROR: ' + str(err) + bcolors.ENDC)


        #print('')
    #print(bigData[:])
    return(bigData[:])


def findDupes(lists):
    hashList = []
    dupeList = []
    count = 0
    for i in range(0, len(lists)):
        hashList.append(lists[i][1])


    for p in range(0, len(lists)):
        dupes = [i for i, x in enumerate(hashList) if x==hashList[p]]
        if len(dupes) > 1:
            if hashList[dupes[0]] not in dupeList:
                count += 1
                print(bcolors.OKBLUE + bcolors.BOLD + '[+]FOUND DUPLICATES:' + bcolors.ENDC)
                for i in dupes:
                    if hashList[i] not in dupeList:
                        dupeList.append(hashList[dupes[0]])
                    print(bcolors.OKGREEN + '[+]FILE MATCH: ' + bcolors.ENDC + lists[i][0])

    if count == 0:
        print(bcolors.FAIL + '[!]NO FILES MEET CRITERIA' + bcolors.ENDC)
    print('')


def findLarge(lists, number):
    sizeList = []
    finalList = []
    for i in range(0, len(lists)):
        sizeList.append(lists[i][2])
    print(bcolors.OKBLUE + bcolors.BOLD + '[+]FOUND FILES LARGER THAN %s bytes:' % number + bcolors.ENDC)
    for i in range(0, len(sizeList)):
        if sizeList[i] > int(number):
            newLists = lists[i]
            finalList.append(newLists)
    if len(finalList) != 0:
        finalList = sorted(finalList, key=itemgetter(2), reverse=True)
        for file in finalList:
            something = bcolors.OKGREEN + '[+]FILE MATCH: ' + bcolors.ENDC + file[0]
            print(something.ljust(120, '.')  + convert_size(file[2]).rjust(13) + bcolors.ENDC)
    else:
        print(bcolors.FAIL + '[!]NO FILES MEET CRITERIA' + bcolors.ENDC)

        print('')



def findOld(lists, date):
    epochList = []
    finalList = []
    epochAgo = time.time() - float(date) * 86400
    for i in range(0, len(lists)):
        epochList.append(lists[i][3])
    print(bcolors.OKBLUE + bcolors.BOLD + '[+]FOUND FILES OLDER THAN %s days:' % date + bcolors.ENDC)
    for i in range(0, len(epochList)):
        if epochList[i] < int(epochAgo):
            newLists = lists[i]
            newLists[3] = time.strftime("%b %d %H:%M",time.gmtime(newLists[3]))
            finalList.append(newLists)
    if len(finalList) != 0:
        finalList = sorted(finalList, key=itemgetter(3), reverse=True)

        for file in finalList:
            something = bcolors.OKGREEN + '[+]FILE MATCH: ' + bcolors.ENDC + file[0]
            print(something.ljust(120, '.')  + str(file[3]).rjust(13))
    else:
        print(bcolors.FAIL + '[!]NO FILES MEET CRITERIA' + bcolors.ENDC)

    print('')



fileInfo = fileLister(options.parent_dir)
print()
if not options.dupe_file == False:
    if not options.large_file == None:
        if not options.old_file == None:
            print(bcolors.HEADER + ' RESULTS '.center(120 + 4, '=') + bcolors.ENDC + '\n')
            findDupes(fileInfo)
            findOld(fileInfo, options.old_file)
            findLarge(fileInfo, options.large_file)
        else:
            print(bcolors.HEADER + ' RESULTS '.center(120 + 4, '=') + bcolors.ENDC + '\n')
            findDupes(fileInfo)
            findLarge(fileInfo, options.large_file)
    elif not options.old_file == None:
        print(bcolors.HEADER + ' RESULTS '.center(120 + 4, '=') + bcolors.ENDC + '\n')
        findDupes(fileInfo)
        findOld(fileInfo, options.old_file)
    else:
        print(bcolors.HEADER + ' RESULTS '.center(120 + 4, '=') + bcolors.ENDC + '\n')
        findDupes(fileInfo)
elif not options.large_file == None:
    if not options.old_file == None:
        print(bcolors.HEADER + ' RESULTS '.center(120 + 4, '=') + bcolors.ENDC + '\n')
        findOld(fileInfo, options.old_file)
        findLarge(fileInfo, options.large_file)
    else:
        print(bcolors.HEADER + ' RESULTS '.center(120 + 4, '=') + bcolors.ENDC + '\n')
        findLarge(fileInfo, options.large_file)
else:
    print(bcolors.HEADER + ' RESULTS '.center(120 + 4, '=') + bcolors.ENDC + '\n')
    findOld(fileInfo, options.old_file)
