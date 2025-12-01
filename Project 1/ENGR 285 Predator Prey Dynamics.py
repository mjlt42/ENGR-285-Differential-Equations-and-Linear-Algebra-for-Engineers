#A program implementing and measuring a Wa-Tor Simulation (outputs to a "temp" folder)

from matplotlib.pyplot import * #Library needed to plot results
from numpy import * #Library needed for some numerical functions
from random import * #Library needed to generate random numbers for movement
import sys, glob, shutil, os #Libraries needed to read/write files/folders and other system operations
from pathlib import Path #Library to determine the file paths to images
import imageio.v2 as io #Library for converting a collection of image files to a gif

#Main parameters of the simulation
breed_time = 3 #Number of steps before a fish is capable of duplicating
energy_gain = 4 #Additional steps granted to a shark after eating a fish
breed_energy = 10 #Number of stored steps before a shark is capable of duplicating

#Other simulation parameters
dims = [80,100] #Size of the simulation window
initial_fish = 2000
initial_sharks = 1400
steps = 500 #Time duration of the simulation
start_energy = 9 #Maximum number of stored steps a shark begins with
basicSetup = 1 # Set distribution to 0 for random, 1 for tile pattern, and 2 for polar ends

#Create a list of the row indexes of the game array
ilist = []
for i in range(dims[0]):
    ilist.append(i)
#Create a list of the column indexes of the game array
jlist = []
for j in range(dims[1]):
    jlist.append(j)

#Function to determine available empty spaces to move into
def removeoccupied(locs): #Input a list of lists of locations and values (should be four adjacent locations)
    rlocs = [] #Create an empty list of locations
    for k in range(4):
        if locs[k][1] == 0: #If the value shows the space is empty...
            rlocs.append(locs[k][0]) #...add the corresponding location to the list of locations
    return rlocs
  
#Function to determine if there are adjacent fish that a shark can feed on
def findfishoccupied(locs):
    rlocs = [] #Create an empty list of locations
    for k in range(4): #Input a list of lists of locations and values (should be four adjacent locations)
        if locs[k][1] > 0: #If the value shows the space has a fish there...
            rlocs.append(locs[k][0]) #...add the corresponding location to the list of locations
    return rlocs

#Function to determine the common elements in two lists of lists (with no repeats)
def nestintersection(list1, list2):
    return list(map(list, set(map(tuple, list1)) & set(map(tuple, list2))))
  
#Function to combine all elements in two lists of lists (with no repeats)
def nestunion(list1, list2):
    return list(map(list, set(map(tuple, list1)) | set(map(tuple, list2))))

#Main function of the simulation, updates the game array including all movements, hunts, breedings, and deaths
def stepgame(old_array):
    global ilist, jlist
    new_array = zeros((dims[0],dims[1]), dtype=int) #Creates the next game array
    shuffle(ilist) #Randomize the order of the row indices each time (helps keep the processes uniformly random)
    for i in ilist: #Cycle over all row indices in the previous game array
        shuffle(jlist) #Randomize the order of the column indices each time (helps keep the processes uniformly random)
        for j in jlist: #Cycle over all column indices in the previous game array
            if 0 < old_array[i][j]: #Check if a fish occupies the space
                oldlocs = removeoccupied([[[i,(j+1)%dims[1]],old_array[i][(j+1)%dims[1]]],[[(i+1)%dims[0],j],old_array[(i+1)%dims[0]][j]],[[i,(j-1)%dims[1]],old_array[i][(j-1)%dims[1]]],[[(i-1)%dims[0],j],old_array[(i-1)%dims[0]][j]]])
                newlocs = removeoccupied([[[i,(j+1)%dims[1]],new_array[i][(j+1)%dims[1]]],[[(i+1)%dims[0],j],new_array[(i+1)%dims[0]][j]],[[i,(j-1)%dims[1]],new_array[i][(j-1)%dims[1]]],[[(i-1)%dims[0],j],new_array[(i-1)%dims[0]][j]]])
                availlocs = nestintersection(oldlocs, newlocs) #Determines which adjacent spaces are free in both arrays
                if len(availlocs) != 0: #Check if there are any options
                    chosenloc = availlocs[randint(0, len(availlocs)-1)] #Randomly choose one of the options
                    if breed_time < old_array[i][j]: #Check if the fish is elligible to breed
                        new_array[chosenloc[0]][chosenloc[1]] = 1 #Place a new fish in that location
                        new_array[i][j] = 1 #Reset the fish that just bred
                    else: #Otherwise the fish only moves
                        new_array[chosenloc[0]][chosenloc[1]] = old_array[i][j] + 1 #The fish moves to the new game array with an increment to its breeding timer
                else: #If there are no options, the fish does not breed or move
                    new_array[i][j] = old_array[i][j] #The fish moves to the new game array without resetting
                old_array[i][j] = 0 #Removes the fish from the previous game array (so that it doesn't move/breed twice)
            elif 0 > old_array[i][j]: #Check if a shark occupies the space
                oldlocs = findfishoccupied([[[i,(j+1)%dims[1]],old_array[i][(j+1)%dims[1]]],[[(i+1)%dims[0],j],old_array[(i+1)%dims[0]][j]],[[i,(j-1)%dims[1]],old_array[i][(j-1)%dims[1]]],[[(i-1)%dims[0],j],old_array[(i-1)%dims[0]][j]]])
                newlocs = findfishoccupied([[[i,(j+1)%dims[1]],new_array[i][(j+1)%dims[1]]],[[(i+1)%dims[0],j],new_array[(i+1)%dims[0]][j]],[[i,(j-1)%dims[1]],new_array[i][(j-1)%dims[1]]],[[(i-1)%dims[0],j],new_array[(i-1)%dims[0]][j]]])
                availlocs = nestunion(oldlocs, newlocs) #Find all nearby fish locations in either game array (whether they've been updated or not)
                if len(availlocs) != 0: #Check if there are any options
                    chosenloc = availlocs[randint(0, len(availlocs)-1)] #Choose one of the adjacent fish randomly
                    if -breed_energy > old_array[i][j]: #Check if the shark is elligible to breed
                        new_array[chosenloc[0]][chosenloc[1]] = old_array[i][j] + start_energy - round(energy_gain/2) + 1 #Moves the reset shark to the new game array with an increase in energy
                        new_array[i][j] = -start_energy - round(energy_gain/2) #Creates a new shark at the previous position
                    else:
                        new_array[chosenloc[0]][chosenloc[1]] = old_array[i][j] - energy_gain + 1 #Moves the shark to the new game array with an increase in energy
                    if old_array[chosenloc[0]][chosenloc[1]] > 0: #Only need to remove the dead fish if it came from the old array
                        old_array[chosenloc[0]][chosenloc[1]] = 0 #Removes the dead fish
                else: #Implement shark moving
                    oldlocs = removeoccupied([[[i,(j+1)%dims[1]],old_array[i][(j+1)%dims[1]]],[[(i+1)%dims[0],j],old_array[(i+1)%dims[0]][j]],[[i,(j-1)%dims[1]],old_array[i][(j-1)%dims[1]]],[[(i-1)%dims[0],j],old_array[(i-1)%dims[0]][j]]])
                    newlocs = removeoccupied([[[i,(j+1)%dims[1]],new_array[i][(j+1)%dims[1]]],[[(i+1)%dims[0],j],new_array[(i+1)%dims[0]][j]],[[i,(j-1)%dims[1]],new_array[i][(j-1)%dims[1]]],[[(i-1)%dims[0],j],new_array[(i-1)%dims[0]][j]]])
                    availlocs = nestintersection(oldlocs, newlocs) #Determines which adjacent spaces are free in both arrays (i.e. actually empty)
                    if len(availlocs) != 0: #Check if there are any options
                        chosenloc = availlocs[randint(0, len(availlocs)-1)] #Randomly choose one of the options
                        if -breed_energy > old_array[i][j]: #Check if the shark is elligible to breed
                            new_array[chosenloc[0]][chosenloc[1]] = old_array[i][j] + start_energy + 1 #Moves the reset shark to the new game array with a decrease in energy
                            new_array[i][j] = -start_energy #Creates a new shark at the previous position
                        else:
                            new_array[chosenloc[0]][chosenloc[1]] = old_array[i][j] + 1 #The shark moves to the new game array with one less energy (or dies)
                    else: #If the shark can't move, it stays in place
                        new_array[i][j] = old_array[i][j] + 1 #The shark moves to the new game array with one less energy (or dies)
            old_array[i][j] = 0 #Removes the shark from the old game array (so that it doesn't eat/move/breed twice)
    return new_array #Outputs the updated game array

#Function that counts the total number of fish and sharks in the game array
def countsNf(game_array):
    fish_count = 0 #Initialize a fish counter
    shark_count = 0 #Initialize a shark counter
    for i in range(dims[0]): #Cycle over all row...
        for j in range(dims[1]): #...and column indices
            if game_array[i][j] > 0: #If there's a fish there...
                fish_count += 1 #...increment the fish counter
            if game_array[i][j] < 0: #If there's a shark there...
                shark_count += 1 #...increment the shark counter
    return [shark_count, fish_count]
  
#Function to convert the game array into a format for visual display
def createimgarray(game_array):
    img_array = zeros((dims[0], dims[1]), dtype=int)
    for i in range(dims[0]):
        for j in range(dims[1]):
            if game_array[i][j] > 0:
                img_array[i][j] = 1
            if game_array[i][j] < 0:
                img_array[i][j] = -1
    return img_array

game_array = zeros((dims[0],dims[1]), dtype=int) #Initialize the game array

if basicSetup == 0: #The basic set-up with random placement of new fish and sharks
    for k in range(initial_fish): #Randomly populate the game array with new initial fish
        i = randint(0, dims[0]-1)
        j = randint(0, dims[1]-1)
        while game_array[i][j] != 0: #Keep picking different indices until the chosen location is open
            i = randint(0, dims[0]-1)
            j = randint(0, dims[1]-1)
        game_array[i][j] = randint(1, breed_time) #Give the fish a random initial time
    for k in range(initial_sharks): #Randomly populate the game array with new initial sharks
        i = randint(0, dims[0]-1)
        j = randint(0, dims[1]-1)
        while game_array[i][j] != 0: #Keep picking different indices until the chosen location is open
            i = randint(0, dims[0]-1)
            j = randint(0, dims[1]-1)
        game_array[i][j] = randint(-breed_energy, -1) #Give the shark a random initial energy
elif basicSetup == 1: #Tile pattern setup
    for i in range(dims[0]): #Cycle over all entries in the game array
        for j in range(dims[1]):
            if (i%2 == 1) and (j%2 == 1): 
                game_array[i][j] = randint(-breed_energy, -1) #Give the shark a random initial energy
            elif (i%2 == 0) and (j%2 == 0):
                game_array[i][j] = randint(1, breed_time) #Give the fish a random initial time
elif basicSetup == 2: #Polar Ends setup
    for i in range(dims[0]): #Cycle over all entries in the game array
        for j in range(dims[1]):
            if (i == 0 or i == 1 or i == 2): 
                game_array[i][j] = randint(-breed_energy, -1) #Give the shark a random initial energy
            elif (i == dims[0]-1 or i == dims[0]-2 or i == dims[0]-3):
                game_array[i][j] = randint(1, breed_time) #Give the fish a random initial time

img_array = createimgarray(game_array)
arrayfig = figure(frameon=False)
ax = arrayfig.subplots()
ax.set_axis_off()
img = ax.imshow(img_array, cmap='bwr')
arrayfig.tight_layout()
savefig('tmp0001.png')

fishes = [initial_fish] #Initialize the list to store fish data
sharks = [initial_sharks] #Initialize the list to store the shark data
print("Playing game...")
prcnt = 0
k = 1 #Initialize a counter for the number of steps
actual_steps = steps #Initialize a separate variable to record how many steps the simulation actually runs
while k <= steps:
    game_array = stepgame(game_array) #Update the game array
    currcount = countsNf(game_array) #Counts the number of fish and sharks
    fishes.append(currcount[1]) #Store the number data
    sharks.append(currcount[0])
    img_array = createimgarray(game_array) #Create a version of the game array that's easier to plot
    img.set_data(img_array) #Draw the plot of the new game array
    savefig('tmp%04d.png' % (k+1)) #Save the new plot to the temporary folder
    if floor(k*100/steps) > prcnt: #Output the progress of the simulation
        ppstr = str(prcnt) + '%'
        sys.stdout.write('%s\r' % ppstr)
        sys.stdout.flush()
        prcnt += 1
    if 0 < currcount[0] + currcount[1] < dims[0] * dims[1]: #Check if the species have not gone extinct and the array isn't full
        k += 1
    else:
        print('Early termination!')
        actual_steps = k #Save the actual number of steps taken
        k = steps + 1 #Push the value of k large enough to terminate the while loop
    
sys.stdout.write('%s\r' % '100%') #Output that the game updates have completed
sys.stdout.flush()

print('Reading image files...')

#Save a string for the file name which includes all the parameters used in the run
filename = 'SnFanimation_'+str(dims[1])+'x'+str(dims[0])+'_('+str(breed_time)+','+str(energy_gain)+','+str(breed_energy)+','+str(start_energy)+')_('+str(initial_sharks)+','+str(initial_fish)+')_'+str(actual_steps)+'.gif' #File name for the output gif file, includes relevant simulation parameters
mypath = Path(__file__).parent.absolute() #File path to the temporary image folder
imgnames = glob.glob('tmp*.png') #Generate a list of all image names in the temporary image folder
imgPaths = []

for imgname in imgnames: #Convert the list of image names to a list of file paths to the images
    imgPaths.append(str(mypath/imgname))

imgPaths.sort() #Sort the images into chronological order
totaldata = []

for imgpath in imgPaths: #Read in all the image data
    currdata = io.imread(imgpath)
    totaldata.append(currdata)
    
print('Writing gif file...')
    
io.mimwrite(filename, totaldata, format= '.gif', fps = 20) #Convert all the images into a gif

for imgname in imgnames: #Remove all the png image files after the gif is created
    os.remove(imgname)

#Create and save plots of the number results
fig, axs = subplots(2)
fig.suptitle('Wa-Tor Populations')
axs[0].plot(range(actual_steps+1), fishes, label='fish')
axs[0].plot(range(actual_steps+1), sharks, label='sharks')
axs[0].legend()
axs[0].set(xlabel="", ylabel="Population")
axs[1].plot(take(fishes, range(actual_steps+1)), take(sharks, range(actual_steps+1)), marker='.')
axs[1].set(xlabel="Fish Population", ylabel="Shark Population")
#Save the plots to a file with a name that includes all the parameters of the run
savefig('SnFplots_'+str(dims[1])+'x'+str(dims[0])+'_('+str(breed_time)+','+str(energy_gain)+','+str(breed_energy)+')_('+str(initial_sharks)+','+str(initial_fish)+')_'+str(actual_steps)+'.png')

print('Complete!')
print('WARNING: Output files may be overwritten upon next run,')
print('to be safe be sure to move them out of the current folder!')