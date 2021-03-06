import math
import random
from operator import itemgetter
import csv
import sys


# parameters
f = 50000
elite_number = 30
selection_k = 50
m_best = 10
initial_population = 250
alpha = 0.05
two_opt_offsprings = 3


# this variable is used to keep track of number of fitness function calls
fitness_calls = 0

# this variable is used to keep track of the optimal path generated by the algorithm
# first value of the list is a path and the second one is the length of the path
best_result = [0, 19999999999999]


filename = sys.argv[1]

#gives a total distance traveled after following the given path
def fitness_function(city_list, coor):
	global fitness_calls
	total_dis = 0
	city_from = city_list[0]
	length = len(city_list)
	for i in range(1, length+1):
		if i==length:
			city_to = city_list[0]
		else:
			city_to = city_list[i]


		coor1 = coor[city_from]
		coor2 = coor[city_to]

		x1 = coor1[0]
		y1 = coor1[1]
		x2 = coor2[0]
		y2 = coor2[1]

		distance = math.sqrt( (x1-x2)**2 + (y1-y2)**2 )
		total_dis += distance
		city_from = city_to

	fitness_calls+=1
	return total_dis


# given the data from the file, generates a dictionary where 
# keys are the cities, and the values are x and y coordinates
def coor_dic(data):
	coor_dic = {}
	for city in data:
		coor_dic[city[0]] = [city[1], city[2]]
	return coor_dic


# generates list of numbers from 1 to num_cities
def cities_list(num_cities):
	cities = []
	for i in range(1, (num_cities+1)):
		cities.append(i)
	return cities

# randomly creates initial population using population_length which is equal to the initial population size
def random_population(num_cities, population_length):
	cities_l = cities_list(num_cities)
	random_pop = []
	for i in range(population_length):
		cities = cities_l[:]
		random.shuffle(cities)
		random_pop.append(cities)

	return random_pop


# function to retrieve the data from a .tsp file
def retrieve_data(filename):
	f = open(filename, "r")
	line = f.readline()

	while(line[0]!='1'):
		line = f.readline()
	coor = []
	while(line.strip()!="EOF"):
		coor.append(line.rstrip())
		line = f.readline()
	f.close()

	for i in range(len(coor)):
		coor[i] = [ float(j) for j in coor[i].split()]

	return coor


# tournament selection function
def selection(population, parents_len, pool_len):
	# result = sorted(result, key=itemgetter(1))

	selection_numbers = random.sample(range(len(population)), pool_len)

	selected = []

	for number in selection_numbers:
		selected.append(population[number])

	ordered_selected = sorted(selected, key=itemgetter(1))

	final_selected = ordered_selected[:parents_len]

	# parents = [ parent[0] for parent in final_selected ]

	return final_selected



# this function sorts the whole population by their fitness values and stores it in an ordered list
def sort_gene_pool(population, elite_number):
	global best_result
	result = population[:elite_number]
	for i in range(elite_number, len(population)):
		fitness = fitness_function(population[i], coor)
		result.append([population[i], fitness])

	# result = sorted(result, key=itemgetter(1))


	ordered = sorted(result, key=itemgetter(1))

	if best_result[1]>ordered[0][1]:
		best_result = ordered[0]
	return ordered


# simple mutation that swaps the place of two random cities in a path
def mutation(offsprings):
	path_len = len(offsprings[0])

	for offspring in offsprings:
		perm1 = random.randint(0, path_len-1)
		perm2 = random.randint(0, path_len-1)

		offspring[perm1], offspring[perm2] = offspring[perm2], offspring[perm1]



	return offsprings
	
# two-point crossover (explanation is in the report)
def crossover(parents):
	offsprings = []
	parents_len = len(parents)
	path_len = len(parents[0])
	for parent1 in parents:
		parent2_index = random.randint(0,parents_len-1)
		parent2 = parents[parent2_index]

		crossover_point1 = random.randint(1,path_len-1)
		crossover_point2 = random.randint(1,path_len-1)
		if crossover_point1>crossover_point2:
			crossover_point1, crossover_point2 = crossover_point2, crossover_point1

		child1 = [0]*crossover_point1 
		child1.extend(parent1[crossover_point1:crossover_point2])
		child1.extend([0]*(path_len - crossover_point2))

		child2 = parent1[:crossover_point1] 
		child2.extend([0]*(crossover_point2-crossover_point1))
		child2.extend( parent1[crossover_point2:])

		child1_set = set(child1)
		child2_set = set(child2)

		i = 0
		j = 0
		while(i!=path_len):
			if child1[i]==0:
				if parent2[j] not in child1_set:
					child1[i] = parent2[j]
					i+=1
					j+=1
				else:
					j+=1
			else:
				i+=1

		i = 0
		j = 0
		while(i!=path_len):
			if child2[i]==0:
				if parent2[j] not in child2_set:
					child2[i] = parent2[j]
					i+=1
					j+=1
				else:
					j+=1
			else:
				i+=1

		offsprings.append(child1)
		offsprings.append(child2)

	return offsprings

# simple function that calculates the distance between two cities
def dist(city1, city2, coor):
	coor1 = coor[city1]
	coor2 = coor[city2]

	x1 = coor1[0]
	y1 = coor1[1]
	x2 = coor2[0]
	y2 = coor2[1]

	distance = math.sqrt( (x1-x2)**2 + (y1-y2)**2 )

	return distance

# 2-opt algorithm which optimizes edges between two randomly generated points
def two_opt(children, coor):
	path_len = len(children[0])
	for child in children:
		point1 = random.randint(1,path_len-1)
		point2 = random.randint(1,path_len-1)

		# if point1>(path_len//2):
		# 	point2 = point1
		# 	point1 -= (path_len//2)+1
		# else:
		# 	point2 = point1 + (path_len//2)-1
		if point1>point2:
			point1, point2 = point2, point1
		for i in range(point1, point2-2):
			for j in range(i+2, point2):
				d1 = dist(child[i], child[j], coor) + dist(child[i+1], child[j+1], coor)
				d2 = dist(child[i], child[i+1], coor) + dist(child[j], child[j+1], coor) 
				if d2>d1:
					child[i+1], child[j] = child[j], child[i+1]
	return children



data = retrieve_data(filename)
coor = coor_dic(data)
pop = random_population(len(data), initial_population)

for i in range(0, elite_number):
	fitness = fitness_function(pop[i], coor)
	pop[i] = ([pop[i], fitness])	



while fitness_calls<=f:
	ordered_gene_pool = sort_gene_pool(pop, elite_number)

	temp = selection(ordered_gene_pool, m_best, selection_k)
	temp += selection(ordered_gene_pool, m_best, selection_k)
	temp += selection(ordered_gene_pool, m_best, selection_k)
	temp += selection(ordered_gene_pool, m_best, selection_k)
	temp += selection(ordered_gene_pool, m_best, selection_k)

	elite = temp[:elite_number]

	parents = [parent[0] for parent in temp]
	offsprings = crossover(parents)
	mutated_offsprings = mutation(offsprings)

	random_number = random.uniform(0.0, 1.0)
	
	if random_number<alpha:
		opted_offsprings = two_opt(mutated_offsprings[:two_opt_offsprings], coor)

		pop = elite + opted_offsprings + mutated_offsprings[two_opt_offsprings:]
	else:
		pop = elite + mutated_offsprings



print(best_result[1])



with open('solution.csv', 'w', newline='') as file:
	writer = csv.writer(file)
	for city in best_result[0]:
		writer.writerow([city])
