import json


# Function to create an index based on city_ascii and admin_name
def create_index(events):
    index = {}
    for event in events:
        key = (event.get("city_ascii"), event.get("admin_name"))
        if key not in index:
            index[key] = event
    return list(index.values())


# Read the JSON file
with open("2024_eclipse_events.json", "r") as file:
    data = json.load(file)

print('Number of events: ' + str(len(data)))

# Remove duplicates based on the index
filtered_data = create_index(data)

print('Number of filtered events: ' + str(len(filtered_data)))

# Write the filtered data back to the JSON file if needed
with open("filtered_events.json", "w") as output_file:
    json.dump(filtered_data, output_file, indent=2)
