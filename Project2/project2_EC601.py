# Copyright 2023 Iñigo Perez Gamiz

import googlemaps   

class GoogleMaps:

    def __init__(self, api_key):
        self.api_key = api_key
        self.gmaps = googlemaps.Client(key=api_key)

    def calculate_distance(self, origin, destination):
        
        # Calculate the distance between origin and destination using car route
        directions =  self.gmaps.directions(origin, destination, mode="driving")

        if directions and len(directions) > 0:
            route = directions[0]['legs'][0]
            return route['distance']['text']
        else:
            return None
        
    def get_location_after_distance(self, origin, destination, distance_miles):
        
        # Get directions for the car route
        directions = self.gmaps.directions(origin, destination, mode="driving")

        if not directions or len(directions) == 0:
            return None

        # Initialize variables to keep track of cumulative distance and the location
        cumulative_distance = 0
        location = None

        for step in directions[0]['legs'][0]['steps']:
            step_distance_meters = step['distance']['value']
            cumulative_distance += step_distance_meters

            # Check if the cumulative distance is greater than or equal to the desired distance (100 miles)
            if cumulative_distance >= distance_miles * 1609.34:  # Convert miles to meters
                location = step['end_location']
                break

        return location

    def sort_gas_stations_by_rating(self, gas_stations):
        # Sort the gas stations by rating in descending order (highest rating first)
        return sorted(gas_stations, key=lambda station: station.get('rating', 0), reverse=True)


    def get_gas_stations(self, origin, destination, covered_distance, k=0):
        # Get the highest rated gas stations at a specific location
        location = self.get_location_after_distance(origin, destination, covered_distance-10-12*k)
        if location == None:
            return None
        gas_stations = self.gmaps.places_nearby(location=location, keyword="gas station", radius=10000)
        sorted_gas_stations = self.sort_gas_stations_by_rating(gas_stations["results"])
        if len(sorted_gas_stations) >= 3:   # If there are more than 3 options, print the 3 highest rated
            for j in range(3):
                place = sorted_gas_stations[j]
                print(place["name"], place["vicinity"])
        elif len(sorted_gas_stations) >= 1:  # If there are less than 3 options, print all of them
            for place in sorted_gas_stations:
                print(place["name"], place["vicinity"])
        else:         
            # If there are no gas stations in the area, go back recursively to find one earlier 
            k += 1
            return self.get_gas_stations(origin, destination, covered_distance, k)

        return location
    

def main():

    GM = GoogleMaps("GOOGLE_MAPS_API_KEY")  # Replace with your Google Maps API Key
        
    # Inputs
    origin = input("Enter the origin city: ")
    destination = input("Enter the destination city: ")
    deposit_capacity = float(input("Enter the capacity of the deposit in gallons: "))
    fuel_consume = float(input("Enter the fuel consume in gallons per 100 miles: "))
    fuel_percentage = float(input("Enter the current fuel percentage (%): "))

    # Calculate the distance in miles between the 2 cities
    distance = GM.calculate_distance(origin, destination)
    if distance == None:
        print("You can not do this trip by car.")
        return None
    str_distance_in_miles = distance.split()[0]
    if ',' in str_distance_in_miles:
        i = str_distance_in_miles.index(',')
        str_distance_in_miles = str_distance_in_miles[:i] + str_distance_in_miles[i+1:]
    distance_in_miles = float(str_distance_in_miles)

    # Calculate the remaining fuel based on the given fuel percentage
    remaining_fuel = (fuel_percentage / 100) * deposit_capacity

    # Calculate the total fuel required for the whole trip
    total_fuel_required = distance_in_miles * (fuel_consume / 100)

    # If the total fuel required is less than the already available
    if total_fuel_required < remaining_fuel:
        print("You have enough fuel for the trip. Safe travels!")
        return None
        
    # If there is need to stop to refill the deposit
    # First stop (consume the available fuel)
    n_stop = 1
    distance_until_first_stop = remaining_fuel / (fuel_consume / 100)
    # Look for gas stations 10 miles before running out of fuel just in case
    print("Here are the highest rated gas stations for your stop number " + str(n_stop) +": ")
    last_location = GM.get_gas_stations(origin, destination, distance_until_first_stop)    

    # Rest of the stops. Same procedure with a cycle
    remaining_distance = distance_in_miles - distance_until_first_stop
    distance_per_deposit = deposit_capacity / (fuel_consume / 100)
    for i in range(int((remaining_distance // distance_per_deposit) - 1)):
        n_stop += 1
        location = GM.get_location_after_distance(last_location, destination, distance_per_deposit)
        if location == None:
            return None
        else:    
            print("Here are the highest rated gas stations for your stop number " + str(n_stop) +": ")
            last_location = GM.get_gas_stations(last_location, destination, distance_per_deposit)
        
    return None

if __name__ == "__main__":
    main()
    
                    