#Program to read in and decode DTMF sound data from a .wav file

from numpy import *
import matplotlib.pyplot as plt #Necessary if you want to plot the waveform (commented out lines at the end)
import wave #Necessary for reading the .wav file
import struct #Necessary for reading the .wav file

#These first few blocks read in the .wav file to an ordinary integer data list
fileName = "EncodedSound.wav"

wavefile = wave.open(fileName, 'r')

length = wavefile.getnframes()
framerate = wavefile.getframerate()
save_data = []
for i in range(0, length):
    wavedata = wavefile.readframes(1)
    data = struct.unpack("<h", wavedata)
    save_data.append(int(data[0]))
#At this point the sound data is saved in the save_data variable

low_frequencies = [697, 770, 852, 941]
high_frequencies = [1209, 1336, 1477]
decode_matrix = [[1,2,3],[4,5,6],[7,8,9],[-1,0,-1]]

def slice_data():
    i = 0
    data_list = []
    while i < length:
        if save_data[i] == 0 :
            i += 1
        else:
            j = 0
            current_signal = []
            while(save_data[j+i+1] != 0 or save_data[j+i-1] != 0):
                current_signal.append(save_data[i+j])
                j += 1
            data_list.append(current_signal)
            i += j + 1
    return data_list
 
def calculate_coefficient(dataSample, freq):
    a = 0 
    b = 0 
    T = len(dataSample)/framerate  
    N = len(dataSample)  
    for i in range(N):  
        t = i / framerate  
        a += dataSample[i] * cos(2 * pi * freq * t)
        b += dataSample[i] * sin(2 * pi * freq * t)
    a *= 2 / N
    b *= 2 / N
    return sqrt(a**2 + b**2)

def decode_freqs(low_freq, high_freq):
    return decode_matrix[low_frequencies.index(low_freq)][high_frequencies.index(high_freq)]

sliced_data = slice_data()

for signal in sliced_data:
    
    highFreq = high_frequencies[0]
    lowFreq = low_frequencies[0]
    highValues = []
    lowValues = []
    
    for i in range(len(high_frequencies)):
        highValues.append(calculate_coefficient(signal, high_frequencies[i])) #finds the value of the coefficient at each high frequency
        highFreq = high_frequencies[highValues.index(max(highValues))] #finds the largest/most "apparent" high frequency 

    for j in range(len(low_frequencies)):
        lowValues.append(calculate_coefficient(signal, low_frequencies[j])) #finds the value of the coefficient at each high frequency
        lowFreq = low_frequencies[lowValues.index(max(lowValues))] #finds the largest/most "apparent" high frequency


    print(decode_freqs(lowFreq, highFreq),end=" ")

#plt.plot(range(0, length), save_data)
#plt.show()