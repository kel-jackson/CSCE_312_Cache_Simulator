## @package cachesimulator
# File: cachesimulator.py;
# Author: Kelsey Jackson;
# Date: 12/8/2021;
# Section: 506 ;
# E-mail: jackson.kel1019@tamu.edu;
# Description: This file implements the Cache Simulator
  
# PART 1: INITIALIZE RAM
import sys, math, random

# take input for file name
## name of the file used to fill the RAM
nameInput = sys.argv[1]

## list of all addresses that could be available for later sorting
addressDigits = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]

# create empty variables for Doxygen
## holds name of command entered
command = ""

## string representation of the smallest RAM address to initialize
minAddress = ""

## string representation of the largest RAM address to initialize
maxAddress = ""

# Print header
command, minAddress, maxAddress = input("*** Welcome to the cache simulator ***\ninitialize the RAM:\n").split()

# split addresses into digits for later
## first digit in decimal form of the smallest RAM address to initialize
minFirst = int(minAddress[2], 16)

## second digit in decimal form of the smallest RAM address to initialize
minSecond = int(minAddress[3], 16)

## first digit in decimal form of the largest RAM address to initialize
maxFirst = int(maxAddress[2], 16)

## second digit in decimal form of the largest RAM address to initialize
maxSecond = int(maxAddress[3], 16)

# open file
## file to use for filling RAM
RAMFile = open(nameInput, 'r')

## list for holding input read in
inputContent = []

## list for holding data in RAM
RAMContent = []

## list for holding RAM addresses
RAMAddresses = []

# load code into input list
for line in RAMFile:
    inputContent += [line.strip()]

# using address digits and lists, build available RAM
for i in range(16):
    for j in range(16):
        RAMAddresses += ["0x" + addressDigits[i] + addressDigits[j]] # rebuild the address from the parts and add to list

        # only add if i is not on edge case or j is within the limits on edge cases
        if ((((i*16) + j) >= ((16 * minFirst) + minSecond)) and (((i*16) + j) <= ((16 * maxFirst) + maxSecond))):
            RAMContent += [inputContent[(i * 16) + j]] # add necessary content from input to RAM since may not need all
        
        # otherwise, add zeros
        else:
            RAMContent += ["00"]
            
# With all lists for RAM set up, done with RAM
print("RAM successfully initialized!")

# PART 2: CONFIGURE THE CACHE
print("configure the cache:")

## cache size
cSize = int(input("cache size: ")) # input cache size

## data block size
BSize = int(input("data block size: ")) # input block size

## number of lines per set
associativity = int(input("associativity: "))  # input associativity

## number of sets in cache
numSets = int(cSize / (BSize * associativity)) # calculate number of sets based on previous inputs

## numerical representation of replacement policy
repPolicy = int(input("replacement policy: ")) # input number for replacement policy

## numerical representation of write hit policy
hitPolicy = int(input("write hit policy: ")) # input number for hit policy

## numerical representation of write miss policy
missPolicy = int(input("write miss policy: ")) # input number for miss policy

# empty variables for Doxygen documentation
## written form of replacement policy
replacement = ""

## written form of write hit policy
writeHit = ""

## written form of write miss policy
writeMiss = ""

# based on number input, assign replacement policy's name for later
if repPolicy == 1:
    replacement = "random_replacement"
elif repPolicy == 2:
    replacement = "least_recently_used"
elif repPolicy == 3:
    replacement = "least_frequently_used"

# based on number input, assign hit policy's name for later    
if hitPolicy == 1:
    writeHit = "write_through"
elif hitPolicy == 2:
    writeHit = "write_back"

# based on number input, assign miss policy's name for later
if missPolicy == 1:
    writeMiss = "write_allocate"
elif missPolicy == 2:
    writeMiss = "no_write_allocate"

# create lists for cache and LRU policy
## list holding all data content for the cache
cache = [[["00"] * BSize for _ in range(associativity)] for _ in range(numSets)]

## list holding the flag bits for all lines in cache
allBits = [[[0, 0, "00"] for _ in range(associativity)] for _ in range(numSets)]

## list holding entries for lines used in order of least recently to to most recent
leastRecent = [[0] for _ in range(numSets)]

## list holding counters for how many times a line has been used
leastFrequent = [[0] * associativity for _ in range(numSets)]
  
# with cache set up, ready to simulate
print("cache successfully initialized!")

# PART 3: SIMULATE THE CACHE
# -----------------------------------------------------------------------------------
# function definitions for cache simulation
# -----------------------------------------------------------------------------------
## Parameters: address; 
# Returns: whether cache hits or misses; 
# Description:
# function takes in the address to read and
# either prints the data at the given address
# if the cache hits or goes to RAM and reads
# in data if cache misses

def cacheRead(address):
    binAddress = bin(int(address, 16))[2:].zfill(8) # convert address to binary
    setBits = int(math.log2(numSets)) # calculate number of bits for set number
    blockBits = int(math.log2(BSize)) # calculate number of bits for block offset
    tagBits = int(8 - (setBits + blockBits)) # calculate number of bits for tag

    tag = "0" + str(hex(int(binAddress[:tagBits], 2))[2:]) # calculate tag
    
    # if more than one set, calculate. Otherwise, only one possibility
    if numSets > 1:
        setNum = int(binAddress[tagBits:(tagBits + setBits)], 2)
    else:
        setNum = 0
    
    # if more than one byte, calculate. Otherwise, only one possibility
    if BSize > 1:
        byteNum = int(binAddress[(tagBits + setBits):], 2)
    else:
        byteNum = 0
    
    # boolean for cache hit or cache miss
    found = False
    
    # print set and tag
    print("set:" + str(setNum))
    print("tag:" + tag)
    
    # check for cache hit
    for i in range(associativity):
        if allBits[setNum][i][2] == tag: # if tag is found, check valid bit
            if allBits[setNum][i][0] == 1: # if valid, cache hit
                found = True # set boolean to "found"
                
                # increment frequency of line usage
                leastFrequent[setNum][i] += 1
                
                # print out format for cache hits
                print("hit:yes")
                print("eviction_line:-1")
                print("ram_address:-1")
                print("data:" + "0x" + cache[setNum][i][byteNum])                    
                return "hit" # return that cache had a hit
                
    # if tag was not found in set
    if found == False:
        print("hit:no") # indicate cache miss
        
        # if associativity == 1, only 1 option for eviction line
        if associativity == 1:
            eviction_line = 0
            
        # otherwise, check whether empty lines exist within the set
        else:
            emptyLines = False # boolean for empty line
            for i in range(associativity):
                if allBits[setNum][i][0] == 0: # if valid bit is 0, line should be empty
                    emptyLines = True # set flag
                    eviction_line = i # set eviction line to min eviction line
                    break
                
            # if set is full, determine eviction line based on policy
            if emptyLines == False:
                if repPolicy == 1: # random replacement
                    eviction_line = random.randint(0, associativity-1)
                    
                elif repPolicy == 2: # least recently used
                    eviction_line = leastRecent[setNum][0] # list pushes more recent lines to back, meaning least recent is in front
                    leastRecent[setNum] = leastRecent[setNum][1:] # remove least recent from front to push to back
                
                elif repPolicy == 3: # least frequently used
                    ## stores the value of the lowest counter for LFU policy
                    minimum = leastFrequent[setNum][0]
                    
                    ## stores the line number of the lowest counter for LFU policy
                    minLine = 0
                    
                    # iterate to find the first instance of the lowest counter since ties evict smaller line numbers
                    for i in range(associativity):
                        if leastFrequent[setNum][i] < minimum:
                            minLine = i
                            minimum = leastFrequent[setNum][i]
                            
                    # set eviction line to smallest line number
                    eviction_line = minLine
                    
                    # increment frequency of line usage
                    leastFrequent[setNum][minLine] += 1
                                
        # continue printing miss format
        print("eviction_line:" + str(eviction_line))
        print("ram_address:" + address)
        
        # if dirty bit is set, edit data from eviction line to RAM before deleting
        if allBits[setNum][eviction_line][1] == 1:
            # rebuild address of eviction line's orignal address to replace data  
            binAddress = str(bin(int(allBits[setNum][eviction_line][2]))[2:].zfill(tagBits)) + str(bin(setNum)[2:].zfill(setBits)) + str(bin(0)[2:].zfill(blockBits))
            binAddress = hex(int(binAddress, 2))
            
            # calculate addresses to write content to
            lowerAddress = int(binAddress, 16)
            higherAddress = int(binAddress, 16) + BSize
            currByte = 0 # counter for current byte for loop
            
            for i in range(lowerAddress, higherAddress):
                RAMContent[i] = cache[setNum][eviction_line][currByte] # read in each byte
                currByte += 1 # increment byte counter
            
        # reset flag bits
        allBits[setNum][eviction_line][0] = 1
        allBits[setNum][eviction_line][1] = 0
        allBits[setNum][eviction_line][2] = tag
        
        # calculate addresses to read in content from
        lowerAddress = int(address, 16) - (int(address, 16) % BSize)
        higherAddress = int(address, 16) + (BSize - (int(address, 16) % BSize))
        currByte = 0 # counter for current byte for loop
        for i in range(lowerAddress, higherAddress):
            cache[setNum][eviction_line][currByte] = RAMContent[i] # read in each byte
            currByte += 1 # increment byte counter
            
        print("data:" + "0x" + cache[setNum][eviction_line][byteNum]) # print data read
        
        # if no lines have been added to the least recent list yet, add current line
        if len(leastRecent[setNum]) == 0:
            leastRecent[setNum] += [eviction_line]
            
        # otherwise, replace current line to the end since just used
        else:
            lineInList = False # boolean for whether line is in list
            for i in range(len(leastRecent[setNum])):
                if leastRecent[setNum][i] == eviction_line: # if current index in the line
                    leastRecent[setNum] = leastRecent[setNum][:i] + leastRecent[setNum][i+1:] # remove current listing
                    leastRecent[setNum] += [eviction_line] # add to the end
                    lineInList = True # set flag to "found"
                    break
            # if line was not found, immediately add it to the list
            if lineInList == False:
                leastRecent[setNum] += [eviction_line]
        return "miss" # return that cache missed
    
# -----------------------------------------------------------------------------------

## Parameters: address, data; 
# Returns: whether cache hits or misses; 
# Description:
# function takes in the address to write content into and
# either writes the data direclty into the given cache/RAM address
# if the cache hits or goes to RAM, reads in data, then writes
# in the given data if cache misses

def cacheWrite(address, data):
    binAddress = bin(int(address, 16))[2:].zfill(8) # convert address to binary
    setBits = int(math.log2(numSets)) # calculate number of bits for set number
    blockBits = int(math.log2(BSize)) # calculate number of bits for block offset
    tagBits = int(8 - (setBits + blockBits)) # calculate number of bits for tag
    
    tag = "0" + str(hex(int(binAddress[:tagBits], 2))[2:]) # calculate tag
    
    # if more than one set, calculate. Otherwise, only one possibility
    if numSets > 1:
        setNum = int(binAddress[tagBits:(tagBits + setBits)], 2)
    else:
        setNum = 0
    
    # if more than one byte, calculate. Otherwise, only one possibility
    if BSize > 1:
        byteNum = int(binAddress[(tagBits + setBits):], 2)
    else:
        byteNum = 0
    
    # boolean for cache hit or cache miss
    found = False
    
    # print set and tag
    print("set:" + str(setNum))
    print("tag:" + tag)
    
    # check if line is already in cache
    for i in range(associativity):
        if allBits[setNum][i][2] == tag: # if tag matches, check valid bit
            if allBits[setNum][i][0] == 1: # if valid, cache hit
                found = True # set to "found"
                
                # increment frequency of line usage
                leastFrequent[setNum][i] += 1
                
                # write formatted output for data
                print("write_hit:yes")
                print("eviction_line:-1")
                print("ram_address:-1")
                
                # depending on hit policy, either write in RAM or set dirty bit
                if hitPolicy == 1:
                    RAMContent[int(address, 16)] = data
                elif hitPolicy == 2:
                    allBits[setNum][i][1] = 1
                    
                # set byte in cache to data and finish outputting
                cache[setNum][i][byteNum] = data
                print("data:" + "0x" + cache[setNum][i][byteNum])
                print("dirty_bit:" + str(allBits[setNum][i][1]))
                return "hit"
             
    # if cache miss
    if found == False:
        print("hit:no") # state it was a miss
        
        # if associativity is 1, only one option for eviction
        if associativity == 1:
            eviction_line = 0
            
        # otherwise, check which line to evict
        else:
            emptyLines = False # flag for checking if there are empty lines
            
            # iterate through set to find invalid/empty line
            for i in range(associativity):
                if allBits[setNum][i][0] == 0:
                    emptyLines = True
                    eviction_line = i
                    break
                
            # otherwise, generate line based on replacement policy
            if emptyLines == False:
                # either evict randomly or...
                if repPolicy == 1:
                    eviction_line = random.randint(0, associativity-1)
                
                # find least recent based on array entries
                elif repPolicy == 2:
                    eviction_line = leastRecent[setNum][0]
                    leastRecent[setNum] = leastRecent[setNum][1:]
                    
                elif repPolicy == 3: # least frequently used
                    ## stores the value of the lowest counter for LFU policy
                    minimum = leastFrequent[setNum][0]
                    
                    ## stores the line number of the lowest counter for LFU policy
                    minLine = 0
                    
                    # iterate to find the first instance of the lowest counter since ties evict smaller line numbers
                    for i in range(associativity):
                        if leastFrequent[setNum][i] < minimum:
                            minLine = i
                            minimum = leastFrequent[setNum][i]
                            
                    # set eviction line to smallest line number
                    eviction_line = minLine
                    
                    # increment frequency of line usage
                    leastFrequent[setNum][minLine] += 1
                        
        # continue printing output
        print("eviction_line:" + str(eviction_line))
        print("ram_address:" + address)
        
        # if dirty bit is set, edit data from eviction line to RAM before deleting
        if allBits[setNum][eviction_line][1] == 1:
            # rebuild address of eviction line's orignal address to replace data  
            binAddress = str(bin(int(tag))[2:].zfill(tagBits)) + str(bin(setNum)[2:].zfill(setBits)) + str(bin(byteNum)[2:].zfill(blockBits))
            binAddress = hex(int(binAddress, 2))
            
            # calculate addresses to write content to
            lowerAddress = int(binAddress, 16) - (int(binAddress, 16) % BSize)
            higherAddress = int(binAddress, 16) + (BSize - (int(binAddress, 16) % BSize))
            currByte = 0 # counter for current byte for loop
            
            for i in range(lowerAddress, higherAddress):
                RAMContent[i] = cache[setNum][eviction_line][currByte] # read in each byte
                currByte += 1 # increment byte counter
            
            # reset dirty bit to 0 after deleting data
            allBits[setNum][eviction_line][1] == 0
            
        # write into RAM only if not write back
        if hitPolicy != 2 or missPolicy == 2:
            RAMContent[int(address, 16)] = data
        
        # depending on hit policy, either write in RAM or move on to miss policy
        if missPolicy == 1:
            
            # reset eviction line's bits for new line
            allBits[setNum][eviction_line][0] = 1
            allBits[setNum][eviction_line][2] = tag
            
            # calculate addresses to read in to the cache
            lowerAddress = int(address, 16) - (int(address, 16) % BSize)
            higherAddress = int(address, 16) + (BSize - (int(address, 16) % BSize))
            currByte = 0 # counter for byte to set
            
            # iterate and replace bytes in line
            for i in range(lowerAddress, higherAddress):
                cache[setNum][eviction_line][currByte] = RAMContent[i]
                currByte += 1
                
            # if write back, write data into cache
            if hitPolicy == 2:
                allBits[setNum][eviction_line][1] = 1
                cache[setNum][eviction_line][byteNum] = data
                
            # add line to least recent array
            # if list is empty, just add
            if len(leastRecent[setNum]) == 0:
                leastRecent[setNum] += [eviction_line]
            
            # otherwise, check if it's already in the list first
            else:
                lineInList = False # flag for finding line
                
                # iterate through least recent array to try to find line entry
                for i in range(len(leastRecent[setNum])):
                    # if found, remove original entry and replace at the end
                    if leastRecent[setNum][i] == eviction_line:
                        leastRecent[setNum] = leastRecent[setNum][:i] + leastRecent[setNum][i+1:]
                        leastRecent[setNum] += [eviction_line]
                        lineInList = True # signify line was found
                        break
                    
                # if line wasn't found, add new entry
                if lineInList == False:
                    leastRecent[setNum] += [eviction_line]
            
        # finish outputting
        print("data:" + "0x" + cache[setNum][eviction_line][byteNum])
        print("dirty_bit:" + str(allBits[setNum][eviction_line][1]))
        return "miss"
    
# -----------------------------------------------------------------------------------
## Parameters: cache, allBits;
# Returns: void;
# Description:
# function clears the cache by deleting the original lists made and rebuilding
# them to make a new cold cache

def cacheFlush(cache, allBits):
    # clear lists for cache and cache flags    
    cache.clear()
    allBits.clear()
    print("cache_cleared")
        
# -----------------------------------------------------------------------------------
## Parameters: none;
# Returns: cache;
# Description:
# function rebuilds the cache to make a cold cache

def newCache():
    # rebuild a cold cache
    cache = [[["00"] * BSize for _ in range(associativity)] for _ in range(numSets)]
    return cache     
   
# -----------------------------------------------------------------------------------
## Parameters: none;
# Returns: allBits;
# Description:
# function resets the allBits flags to represent a cold cache

def newBits():
    # reset flag bits
    allBits = [[[0, 0, "00"] for _ in range(associativity)] for _ in range(numSets)]
    return allBits

# -----------------------------------------------------------------------------------
## Parameters: none;
# Returns: void;
# Description:
# function prints out a formatted version of the cache's settings and content

def cacheView():
    # output format for data from input for cache set up
    # print cache size and set up
    print("cache_size:" + str(cSize))
    print("data_block_size:" + str(BSize))
    print("associativity:" + str(associativity))
    
    # print wrod form of policies based on number input
    print("replacement_policy:" + replacement)
    print("write_hit_policy:" + writeHit)
    print("write_miss_policy:" + writeMiss)
    
    # print hits, misses, and content
    print("number_of_cache_hits:" + str(cacheHits))
    print("number_of_cache_misses:" + str(cacheMisses))
    print("cache_content:")
    
    # print cache line by line
    for i in range(numSets):
        for j in range(associativity):
            print(*allBits[i][j], *cache[i][j])
            
# -----------------------------------------------------------------------------------
## Parameters: none;
# Returns: void;
# Description:
# function prints out a formatted version of the RAM's settings and content

def memoryView():
    ## size of the RAM based on the addresses given
    ramSize = int(maxAddress, 16) - int(minAddress, 16) + 1 # calculate size based on init-ram settings
    
    # output format for memory-view
    print("memory_size:" + str(ramSize))
    print("memory_content:")
    print("address:data")
    
    # print out RAM in sets of 8 bytes
    for i in range(0, int(maxAddress, 16), 8):
        address = RAMAddresses[i] + ":" + RAMContent[i]
        print(address, RAMContent[i+1], RAMContent[i+2], RAMContent[i+3], RAMContent[i+4], RAMContent[i+5], RAMContent[i+6], RAMContent[i+7])
# -----------------------------------------------------------------------------------
## Parameters: none;
# Returns: void;
# Description:
# function writes the content of the cache to a text file called cache.txt

def cacheDump():
    ## text file used to write content of cache into
    cacheDump = open("cache.txt", "w") # open file
        
    # iterate through cache content
    for i in range(numSets):
        for j in range(associativity):
            for k in range(BSize):
                cacheDump.write(str(cache[i][j][k]) + " ") # write BSize bytes per line
            cacheDump.write("\n") # insert newline
    cacheDump.close() # close file
# -----------------------------------------------------------------------------------
## Parameters: none;
# Returns: void;
# Description:
# function writes the content of the RAM to a text file called ram.txt

def memoryDump():
    ## text file used to write content of RAM into
    RAMDump = open("ram.txt", "w") # open file
        
    # write each byte in RAM on a newline
    for i in range(len(RAMContent)):
        RAMDump.write(RAMContent[i])
        RAMDump.write("\n")
        
    RAMDump.close() # close file
# -----------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------

# counters for hits and misses
## counter for how many times the cache has made a hit
cacheHits = 0

## counter for how many times the cache has made a miss
cacheMisses = 0

# obtain commands in a loop
while command != "quit":
    command = input("*** Cache simulator menu ***\ntype one command:\n1. cache-read\n2. cache-write\n3. cache-flush\n4. cache-view\n5. memory-view\n6. cache-dump\n7. memory-dump\n8. quit\n****************************\n").split()
    
    ## string representation of hex address to operate on
    address = "" # default to empty
    
    ## string representation of hex value to write into cache/RAM
    data = "" # default to empty
    
    ## used for incrementing the cache hit and miss counters based on
    # whether functions return "hit" or "miss"
    outcome = "" # default to empty
    
    # command input is initially a list so different lengths of variables can be taken
    if len(command) == 3: # if length is 3 then input has a command, address, and data
        data = command[2][2:]
        address = command[1]
        
    elif len(command) == 2: # if length is 2, then most likely a command and an address
        address = command[1]
        
    command = command[0] # always have a command so don't need an if/else
        
    # with command obtained, execute
    if (command == "cache-read") and (address != ""): # need command AND address
        outcome = cacheRead(address)
        if outcome == "hit":
            cacheHits += 1
        elif outcome == "miss":
            cacheMisses += 1
        
    if (command == "cache-write") and (address != "") and (data != ""): # need command AND address AND data
        outcome = cacheWrite(address, data)
        if outcome == "hit":
            cacheHits += 1
        elif outcome == "miss":
            cacheMisses += 1
    
    if command == "cache-flush": # clear the cache
        cacheFlush(cache, allBits)
        cache = newCache()
        allBits = newBits()
    
    if command == "cache-view": # output the cache's set up and content
        cacheView()
        
    if command == "memory-view": # output the RAM's set up and content
        memoryView()
        
    if command == "cache-dump": # write cache content to separate file
        cacheDump()
        
    if command == "memory-dump": # write memory content to separate file
        memoryDump()