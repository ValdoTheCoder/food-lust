from flask import redirect, session
from functools import wraps
from datetime import datetime
import requests

''' Filter out required data '''
def info_filter(data):
    filtered = []
    nutrients_list = ['ENERC_KCAL', 'FAT', 'CHOCDF',
                            'FIBTG', 'SUGAR', 'PROCNT',
                            'CHOLE', 'NA', 'CA', 'MG', 'K',
                            'FE', 'ZN', 'P']
    counter = 0

    for i in data["hits"]:
        item = {}
        item['id'] = counter
        item["name"] = i["recipe"]["label"]
        item["url"] = i["recipe"]["url"]
        item["image"] = image_check(i["recipe"]["image"])
        item["healthLabels"] = i["recipe"]["healthLabels"]
        item["ingredientList"] = i["recipe"]["ingredientLines"]
        nutri = []

        nutrients = i["recipe"]["totalNutrients"]
        for j in nutrients:
            if j in nutrients_list:
                nutrient = {}
                nutrient['label'] = nutrients[j]['label']
                nutrient['quantity'] = str(round(nutrients[j]['quantity']))
                nutrient['unit'] = nutrients[j]['unit']
                nutri.append(nutrient)

        nutri.sort(key=lambda x: x["label"])
        nutri.insert(0, nutri.pop(3))
        item["nutritionInfo"] = nutri

        filtered.append(item)
        counter += 1

    return filtered

""" Display image placeholder if image not found """
def image_check(image):
    if image:
        return image
    else:
        return "https://foodluststorage.s3-eu-west-1.amazonaws.com/images/no-image.jpg"

""" Decorate routes to require login. """
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

"""" Search function """
def search(app_id, app_key, search_string):
    url = 'https://api.edamam.com/search'
    final_string = "%s%s&app_key=%s&app_id=%s" % (url, search_string, app_key, app_id)
    response = requests.get(final_string)
    return response.json()

""" Return time elapsed string """
def time_elapsed_string(time):
    now = datetime.now()
    elapsed = (now - time)
    days = elapsed.days
    if days > 365:
        year = days // 365
        if str(year)[-1:] == '1':
            return "%i year ago" % year
        else:
            return "%i years ago" % year
    elif days > 30:
        month = days // 30
        if str(month)[-1:] == '1':
            return "%i month ago" % month
        else:
            return "%i months ago" % month
    elif days > 7:
        week = days // 7
        if str(week)[-1:] == '1':
            return "%i week ago" % week
        else:
            return "%i weeks ago" % week
    elif days > 0:
        if str(days)[-1:] == '1':
            return "%i day ago" % days
        else:
            return "%i days ago" % days
    else:
        secs = elapsed.seconds
        mins = secs // 60
        hours = secs // 60 // 60
        # If less than 60 seconds passed
        if secs < 60:
            return "Just now"
        # If less than 1 hour passed
        elif secs < 3600:
            if str(mins)[-1:] == '1':
                return "%i minute ago" % mins
            else:
                return "%i minutes ago" % mins
        # If more than 1 hours passed
        else:
            if str(hours)[-1:] == '1':
                return "%i hour ago" % hours
            else:
                return "%i hours ago" % hours