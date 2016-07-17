"""
Implements user recommendation system using user and item based filtering. Use item based filtering if working with large dataset due
to excess computational costs associated with user based recommendation systems. 
User based recommendation filtering searches through each users and compares each items. 
Item based recommendation filtering builds a item similiarty dictionary and returns the top recommendations for each item
without having to do excess calculations.
"""
from math import sqrt


def similiarity_score(preferences, user1, user2):
	"""
	Calculate the similiarity between two users using Euclidean distances.
	Attributes:
			pereferences: dictionary of user preferences
			user1: name of user1
			user2: name of user2
			returns a float value
	"""
	si = {}
	for item in preferences[user1]:
		if item in preferences[user2]:
			si[item] = 1

	if len(si) == 0:
		return 0

	Euclidean_distance = sum([pow(preferences[user1][item] - preferences[user2][item], 2)
							  for item in preferences[user1] if item in preferences[user2]])

	return 1 / (1 + Euclidean_distance)


def sim_pearson(preferences, user1, user2):
	"""
	Calculates the similiarity measure using pearsons coefficient.

	Attributes:
		preferences: dict object
		user1: key values for user1
		user2: key value for user2
	"""
	si = {}
	
	for item in preferences[user1]:
		if item in preferences[user2]:
			si[item] = 1

	x1_sum1 = sum([preferences[user1][it] for it in si])
	y1_sum2 = sum([preferences[user2][it] for it in si])

	sumsq_x1 = sum([pow(preferences[user1][it],2) for it in si])
	sumsq_y2 = sum([pow(preferences[user2][it], 2) for it in si])

	sum_sq_x1_y2 = sum([preferences[user1][it]* preferences[user2][it] for it in si])

	n = len(si)

	num = (n*sum_sq_x1_y2) - ((x1_sum1 * y1_sum2))

	dem = sqrt((n*sumsq_x1) - (pow(x1_sum1, 2))) * sqrt(((n*sumsq_y2) - (pow(y1_sum2, 2))))

	if dem == 0: return 0

	pearson_r =  num / dem

	return pearson_r


def TopMatches(preferences, user, n = 5,  similiarity = sim_pearson):
	scores = [(similiarity(preferences, user, other), other) for other in preferences if other != user]

	scores.sort()	
	scores.reverse()

	return scores[0:n]	

def getRecommendations(preferences, user, similiarity = sim_pearson):

	totals = {}
	simSums = {}

	for other_users in preferences:
		if other_users == user: continue
		sim = similiarity(preferences, other_users, user)

		if sim < 0: continue
		for item in preferences[other_users]:
			if item not in preferences[user] or preferences[user][item] == 0:

				totals.setdefault(item, 0)
				totals[item] += preferences[other_users][item] * sim
				simSums.setdefault(item, 0)
				simSums[item] += sim

			rankings = [(totals/simSums[item], item) for item, totals in totals.items()]

		rankings.sort()
		rankings.reverse()

		return rankings

def TransformPreference(preferences):
	results = {}
	for user in preferences:
		for item in preferences[user]:
			results.setdefault(item,{})
			results[item][user] = preferences[user][item]

	return results

def CalculateSimiliarItem(preferences, n =10):
	results = {}

	for item in preferences:
		scores = TopMatches(preferences, item, n, similiarity = sim_pearson)
		results[item] = scores

	return results

def ItemRecommendation(preferences, itemSimList, user):
	"""
	Returns a dictionary of recommended items using item-based filtering.
	Preferences: dict of user rating
	itemSimList: dict of similar items for each item
	user: The user that you want to generate a recommendation list for
	"""
	scores = {}
	userRating = preferences[user]

	totalSimilarity = {}

	for (item, rating) in userRating.items():
		for (similarity, item2) in itemSimList[item]:
			if item2 in userRating: continue
			if similarity < 0: continue
			scores.setdefault(item2,0)
			scores[item2] += similarity * rating
			totalSimilarity.setdefault(item2, 0)
			totalSimilarity[item2] += similarity

	rankings = [(score/totalSimilarity[item], item) for item, score in scores.items()]

	rankings.sort()
	rankings.reverse()
	return rankings

