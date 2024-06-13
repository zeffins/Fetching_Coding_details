import requests
import re
from bs4 import BeautifulSoup
from pymongo import MongoClient

def fetch_and_save_leetcode_details(profile_url):
    match = re.search(r'leetcode.com/u/([^/]+)/?', profile_url)
    
    if not match:
        print("Invalid LeetCode profile URL")
        return None, None
    
    username = match.group(1)
    url = f"https://leetcode-api-faisalshohag.vercel.app/{username}"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if "totalSolved" in data:
                return username, data["totalSolved"]
            else:
                print("'totalSolved' key not found in the response data")
        else:
            print(f"Failed to fetch details. HTTP Status Code: {response.status_code}")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    return username, None

def fetch_codeforces_solved(profile_url):
    # Extract the username from the Codeforces profile URL
    match = re.search(r'codeforces.com/profile/([^/]+)/?', profile_url)
    
    if not match:
        print("Invalid Codeforces profile URL")
        return None, 0
    
    username = match.group(1)
    
    url = f'https://codeforces.com/api/user.status?handle={username}'
    response = requests.get(url)
    data = response.json()

    if data['status'] == 'OK':
        solved_problems = set()
        for submission in data['result']:
            if submission['verdict'] == 'OK':
                problem_id = (submission['problem']['contestId'], submission['problem']['index'])
                solved_problems.add(problem_id)
        return username, len(solved_problems)
    else:
        return username, 0

def fetch_and_save_codeforces_user_rating(username):
    url = f'https://codeforces.com/api/user.info?handles={username}'
    response = requests.get(url)
    user_info = response.json()

    if user_info.get('status') == 'OK':
        for user in user_info.get('result', []):
            return user.get('rating', None)
    else:
        print("Failed to fetch rating details")
    return None

def fetch_codechef_solved_and_rating(cc_url):
    # Extract the username from the CodeChef profile URL
    match = re.search(r'codechef.com/users/([^/]+)/?', cc_url)
    
    if not match:
        print("Invalid CodeChef profile URL")
        return None, None
    
    username = match.group(1)
    
    response = requests.get(cc_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    rating_section = soup.find('div', class_='rating-number')
    if rating_section:
        rating = ''.join(char for char in rating_section.text if char.isdigit())
    else:
        rating = None
    
    return username, rating

def store_data_to_mongodb(data, collection_name):
    client = MongoClient('mongodb+srv://navin11104:Na1424vin*@cluster0.zreerhs.mongodb.net/studentdetails')  # Update with your MongoDB connection string if needed
    db = client['studentdetails']  # Database name
    collection = db[collection_name]  # Collection name

    result = collection.insert_one(data)
    print(f"Data inserted with record id {result.inserted_id}")

# Fetch data from Codeforces
cf_url = 'https://codeforces.com/profile/khanishram_72'
codeforces_username, codeforces_solved = fetch_codeforces_solved(cf_url)
codeforces_rating = fetch_and_save_codeforces_user_rating(codeforces_username)

# Fetch data from CodeChef
cc_url = "https://www.codechef.com/users/zeffins"
codechef_username, codechef_rating = fetch_codechef_solved_and_rating(cc_url)

# Fetch data from LeetCode
leetcode_profile_url = "https://leetcode.com/u/khanishram_78/"
leetcode_username, leetcode_solved = fetch_and_save_leetcode_details(leetcode_profile_url)

# Prepare the data for MongoDB
data = {
    "codeforces_username": codeforces_username,
    "codeforces_rating": codeforces_rating,
    "codeforces_solved": codeforces_solved,
    "codechef_username": codechef_username,
    "codechef_rating": int(codechef_rating),
    "leetcode_username": leetcode_username,
    "leetcode_solved": leetcode_solved
}

# Store the data in MongoDB
store_data_to_mongodb(data, 'Coding_Details')
