"""
Note: This program is just a basis program, slight modifications were made while
making the report in order to ease testing and to provide nice and convenient graphs.
"""
#A program to implement Vector RK4 Method to solve a system of 1st order ODEs and graph output

#Import necessary libraries
from numpy import * #Necessary for sine/cosine/pi etc
import matplotlib.pyplot as plt #Necessary for graphing

directory = "C:/Users/.../(FILENAME)/" #Modify directory depending on user (Example directory shown)
iterations = 5 #Change depending on # of reports/graphs desired.

#Define the f(t,u) vector in du/dt=f(t,u)
def f(t, u):
    x = u[0]
    vx = u[1]
    y = u[2]
    vy = u[3]
    return [vx, (-kr*vx - kl*vy)*((vx**2 + vy**2)**0.5), vy, -g + (-kr*vy + kl*vx)*((vx**2 + vy**2)**0.5)]

def RK4MethodStep(t, u):
    k1 = f(t, u)
    k2 = f(t + step/2, add(u, multiply(step/2, k1)))
    k3 = f(t + step/2, add(u, multiply(step/2, k2)))
    k4 = f(t + step, add(u, multiply(step, k3)))
    return add(u, multiply(step/6, add(add(add(k1, multiply(2, k2)), multiply(2, k3)), k4)))

for w in range(6):
    R=[] #Empty list to store range values
    V=[] #Empty list to store speed values
    for p in range(iterations):
        #Parameters go here (Use SI units)
        step = 0.001
        kl = 0.5 #Lift constant  (for the system)
        kr = 1 #Drag constant (for the system)
        g = 1 #Gravitational acceleration(for the system)
        t_initial = 0 #Starting time for the solution
        t_final = 5 #Terminating time for the solution

        x_initial = 0 #Starting x position (for the system)
        y_initial = 0 #Starting y position (for the system)

        vx_initial = 1 #Starting x velocity (for the system)
        vy_initial = 1 #Starting y velocity (for the system)

        launchAngleUse = True #Set to True if launched at an angle or set to False to set each velocity separately
        angle = pi/12 + w*(pi/12) #Launch angle in radians (0 < angle < π/2)
        v_initial = 1 + 0.5*p #Launch Speed
        
        V.append(v_initial)

        if launchAngleUse:
            vx_initial = v_initial*round(cos(angle), 12) #Starting x velocity at an angle (for the system)
            vy_initial = v_initial*round(sin(angle), 12) #Starting y velocity at an angle (for the system)

        u_initial = [x_initial, vx_initial,y_initial, vy_initial]
        
        #Initialize lists to store the values of the points
        t_values = [t_initial]
        u_values = [u_initial]
        while t_values[-1] < t_final: #Loop until you reach or pass the end point
            u_values.append(RK4MethodStep(t_values[-1], u_values[-1])) #Add the next u values (using RK4 Method)
            t_values.append(t_values[-1] + step) #Add the next t value
            
        #Extract the data from the u values list of lists
        x_values = transpose(u_values)[0]
        vx_values = transpose(u_values)[1]
        y_values = transpose(u_values)[2]
        vy_values = transpose(u_values)[3]

        xList = []

        #Finds the time where y values go from negative to positive, (i.e. pass through the x axis)
        #Appends corresponding x values to list
        for i in range(len(t_values)):
            if i == 0:
                xList.append(x_values[0])
            elif i != len(t_values)-1:
                if y_values[i] > 0 and y_values[i+1] < 0 :
                    xList.append(x_values[i])
                    xList.append(x_values[i+1])
            elif i == len(t_values)-1:
                xList.append(x_values[i])
                xList.append(x_values[i])
        #Finds the two bounding ranges that are less or more than the "true" range          
        Range1 = xList[1] - xList[0]
        Range2 = xList[2] - xList[0]

        #Calculates the effective or the average range between the two bounding ranges and finds their error.
        effRange = abs(Range1 + Range2)/2
        errorRange = abs(Range2 - Range1)/2 #Increasing step size reduces the error of the range
        
        R.append(effRange)
        
        file_path = (f"{directory}Report #{p+1}.txt") 

        with open(file_path, 'w') as file:
            file.write("========================================================\n")
            file.write(f"Report #{p+1}\n")
            file.write("========================================================\n")
            file.write(f"Gravitational acceleration: {g} m/s^2\n")
            file.write(f"Drag constant: {kr} 1/m\n")
            file.write(f"Lift constant: {kl} 1/m\n")
            file.write(f"Initial time: {t_initial} s\n")
            file.write(f"Final time: {t_final} s\n")
            if launchAngleUse:
                file.write(f"Initial speed: {v_initial} m/s\n")
                file.write(f"Launch Angle: {angle} rad || {angle*180/pi}°\n")  
            file.write(f"Initial x position: {x_initial} m\n")
            file.write(f"Initial y position: {y_initial} m\n")
            file.write(f"Initial x velocity: {vx_initial} m/s\n")
            file.write(f"Initial y velocity: {vy_initial} m/s\n")
            file.write(f"Range: {effRange} ± {errorRange} m\n")
            file.write(f"Height: {max(y_values)} m\n")
            file.write("========================================================\n")   
            
        print("========================================================")
        print(f"Report #{p+1}")
        print("========================================================")
        print(f"Gravitational acceleration: {g} m/s^2")
        print(f"Drag constant: {kr} 1/m")
        print("Lift constant: {kl} 1/m")
        print(f"Initial time: {t_initial} s")
        print(f"Final time: {t_final} s")
        if launchAngleUse:
            print(f"Initial speed: {v_initial} m/s")
            print(f"Launch Angle: {angle} rad || {angle*180/pi}°")  
        print(f"Initial x position: {x_initial} m")
        print(f"Initial y position: {y_initial} m")
        print(f"Initial x velocity: {vx_initial} m/s")
        print(f"Initial y velocity: {vy_initial} m/s")
        print(f"Range: {effRange} ± {errorRange} m")
        print(f"Height: {max(y_values)} m")
        print("========================================================")

        #Graph the output
        plt.figure()
        plt.title(f"Trajectory \n(Speed: {v_initial} m/s) (Angle: {round(angle*180/pi, 2)}°) (Lift Constant: {kl})")
        plt.xlabel("x position")
        plt.ylabel("y position")
        plt.plot(x_values, y_values,)
        plt.ylim(bottom=0)
        plt.margins(y=0.2)
        plt.grid(True)
        plt.savefig(f"{directory}graph{p+1}.png", dpi=300) #Modify directory depending on user
        plt.close()
        
    plt.figure()
    plt.title(f"Range vs Speed\n (Angle: {round(angle*180/pi, 2)}°)")
    plt.xlabel("Speed (m/s)")
    plt.ylabel("Range (m)")
    plt.plot(V, R)
    plt.ylim(bottom=0)
    plt.margins(y=0.2)
    plt.grid(True)
    plt.savefig(f"{directory}RVgraph{w+1}.png", dpi=300) #Modify directory depending on user
    plt.close


