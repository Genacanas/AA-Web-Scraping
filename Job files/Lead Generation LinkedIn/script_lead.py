from apify_client import ApifyClient

# Initialize the ApifyClient with your API token
client = ApifyClient("<YOUR_API_TOKEN>")

# Prepare the Actor input
run_input = {
    "action": "get-profiles",
    "keywords": [
        "Engineering",
        "Arts and Design",
        "Customer Success and Support",
        "Business Development",
        "Research",
        "Sales",
        "Marketing",
        "Information Technology",
        "Product Management",
        "Quality Assurance"
    ],
    "isUrl": False,
    "isName": False,
    "limit": 1,
}

# Run the Actor and wait for it to finish
run = client.actor("od6RadQV98FOARtrp").call(run_input=run_input)

# Fetch and print Actor results from the run's dataset (if there are any)
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(item)