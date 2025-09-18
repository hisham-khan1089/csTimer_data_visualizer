import csv
import math
import matplotlib.pyplot as plt

def convert_to_seconds(time: str) -> float:
    """Convert the string time, which represents a time in hh:mm:ss.xx format, to seconds, turning 
    the string into a float."""

    components = time.split(':')
    if len(components) == 2:
        return(float(components[-2])*60 + float(components[-1]))
    else:
        return(float(components[-1]))

def solve_stats(filename: str) -> list:
    
    """Given a csTimer formatted csv file called filename, this function
    returns a list containing the total number of solves, mean, standard deviation, 
    fastest solve, and DNFs, in that order."""

    # Calculating mean and finding fastest solve
    non_dnf_solves, total_mean, total_solves = [0]*3
    fastest_solve = 1000000000.0
    with open(filename, 'r') as myfile:
        solves = csv.DictReader(myfile, delimiter=';')
        for row in solves:
            total_solves += 1
            
            if row['Time'][0] != 'D': # Ignoring DNF solves
                non_dnf_solves += 1
                total_mean += convert_to_seconds(row['P.1']) # P.1 is raw time key from dictionary
                
                if convert_to_seconds(row['P.1']) < fastest_solve: # Finding fastest solve
                    fastest_solve = convert_to_seconds(row['P.1'])
                
    mean = total_mean/non_dnf_solves
    DNFs = total_solves - non_dnf_solves

    # Calculating variance 
    total_variance = 0
    with open(filename, 'r') as myfile:
        solves = csv.DictReader(myfile, delimiter=';')
        for row in solves:
            if row['Time'][0] != 'D':
                total_variance += (convert_to_seconds(row['P.1']) - mean) ** 2

    variance = total_variance/non_dnf_solves
    stdev = math.sqrt(variance)

    return [total_solves, mean, stdev, fastest_solve, DNFs]

def data_for_plot(filename: str) -> list:
    
    """Return a list containing the total number of solves, mean, standard deviation, fastest solve, 
    as well as a list containing all of the categories for the bar graph and the list of frequency 
    values."""
    
    stats = solve_stats(filename)

    total_solves = stats[0]
    mean = stats[1]
    stdev = stats[2]
    fastest_solve = stats[3]
    DNFs = stats[4]
    categories = []
    
    # Contains almost all the same values as categories except for
    # 'N+' (where N is the largest number in categories) and 'DNF'.
    
    # Additionally, all values are integers rather than strings, 
    # which allows me to easily check whether time rounded down 
    # is present in num_categories, and thus whether its string 
    # counterpart is present in categories. (See continued documentation)

    num_categories = [] 

    smallest = math.floor(fastest_solve) # Smallest time category
    largest = math.floor(mean + 2*stdev) # Largest time category

    # Creating all the categories
    for i in range(smallest, largest+1):
        categories.append(str(i))
        num_categories.append(i)

    categories.append(str(largest+1) + '+')
    categories.append('DNF')
    
    # Creating the list for the values
    values = []
    for i in range(len(categories)):
        values.append(0)
    
    # Continued documentation
    # Using math.floor() to round down, I check whether each time is present
    # in num_categories, and document the index of that number if true.
    
    # Since the indexes of num_categories/categories correspond to the frequency
    # of each time in the values list, I use the index mentioned above
    # in the values list to add to the corresponding frequency value.
    
    # This allows me to escape the if statements I had to manually edit for each file
    # in previous versions of this project.

    with open(filename, 'r') as myfile:
        myfile = csv.DictReader(myfile, delimiter=';')
        for row in myfile:
            if row['Time'][0] != 'D':
                if math.floor(convert_to_seconds(row['P.1'])) in num_categories:
                    index = num_categories.index(math.floor(convert_to_seconds(row['P.1']))) 
                    values[index] += 1
                else:
                    values[-2] += 1

    values[-1] += DNFs
    
    return [total_solves, mean, stdev, fastest_solve, categories, values]

def create_plot(filename: str, png_filename: str | None=None) -> None: 
    
    """Creates a histogram plot representing solve frequency in various time categories.
    Takes a csTimer formatted csv file called fileame, and saves a plot with name png_filename."""

    stats = data_for_plot(filename)
    total_solves = stats[0]
    mean = stats[1]
    stdev = stats[2]
    fastest_solve = stats[3]
    categories = stats[4]
    values = stats[5]

    plt.bar(categories, values)
    plt.xlabel('Time Categories')
    plt.ylabel('Frequency')
    plt.title('3x3 Solve Histogram')

    # Displaying the frequency value above each bar using enumerate (search its documentation)
    for i, value in enumerate(values):
        plt.text(i, value + plt.ylim()[1]/100, str(value), ha = 'center', fontsize = 8)

    # Displaying number of solves, mean, standard deviation, and fastest solve in the top right corner
    plt.text(len(categories)-0.1, plt.ylim()[1]-0.01*plt.ylim()[1], 
             'solves: ' + str(total_solves) + '\nmean: ' + str(round(mean, 2)) 
             + '\nstdev: ' + str(round(stdev, 2)) + '\nfastest: ' + str(fastest_solve),
             fontsize = 8, ha = 'right', va = 'top')

    # Adjusting the fontsize of the names of time categories on the x-axis
    plt.tick_params('x', labelsize = 8)

    # Saving the figure at high quality (in this case 300 dpi)
    if png_filename != None:
        plt.savefig(png_filename, dpi=300)
    plt.show()


    
