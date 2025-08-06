from apify_client import ApifyClient
import pandas as pd

filename = "CEO_Emails.xlsx"
data = []
new_row = {
    "id": "",
    "name": "",
    "headline": "",
    "title": "",
    "email": ""
}
# Initialize the ApifyClient with your API token
client = ApifyClient("APIFY_TOKEN")
pages = [1,3,6,9,12,15]
# Prepare the Actor input
for page in pages:
    run_input = {
        "url": f"https://app.apollo.io/#/people?page={page}&personTitles[]=ceo&sortAscending=false&sortByField=recommendations_score",
        "max_result": 1000,
        "include_email": True,
        "contact_email_status_v2_verified": True,
        "contact_email_exclude_catch_all": True,
    }

    # Run the Actor and wait for it to finish
    run = client.actor("iJcISG5H8FJUSRoVA").call(run_input=run_input)

    # Fetch and print Actor results from the run's dataset (if there are any)
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        print(item)
        if item["email"] != None:
            new_row["id"] = item["id"]
            new_row["name"] = item["name"]
            new_row["headline"] = item["headline"]
            new_row["title"] = item["title"]
            new_row["email"] = item["email"]

            data.append(new_row)
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)




