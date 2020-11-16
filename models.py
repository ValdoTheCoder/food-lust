from psycopg2.extras import Json

def user_login(conn, username):
    # Query database for username
    cur = conn.cursor()
    cur.execute("SELECT * FROM public.users WHERE username = %s", (username, ))
    user = cur.fetchall()
    cur.close()
    if user:
        user = user[0]
    return user

def signup(conn, username, password):
    cur = conn.cursor()
    cur.execute("INSERT INTO public.users (username, pass_hash, created) VALUES (%s, %s, NOW())", (username, password))
    cur.close()

def get_password_hash(conn, id):
    cur = conn.cursor()
    cur.execute("SELECT pass_hash FROM public.users WHERE id=%s", (id, ))
    pass_hash = cur.fetchone()[0]
    cur.close()
    return pass_hash

def change_pass_hash(conn, hash, id):
    cur = conn.cursor()
    cur.execute("UPDATE public.users SET pass_hash=%s WHERE id=%s", (hash, id))
    cur.close()

def get_user_recipes(conn, id):
    cur = conn.cursor()
    cur.execute("SELECT recipe_id, recipe FROM public.favorites WHERE user_id=%s AND favorites=true", (id, ))

    recipes = []
    for recipe in cur.fetchall():
        # Store database recipe_id into object[id], to be used recipe deletion from favorites
        recipe[1]['id'] = recipe[0]
        recipes.append(recipe[1])

    cur.close()
    return recipes

def add_to_favorites(conn, user_id, item):
    cur = conn.cursor()
    cur.execute('INSERT INTO public.favorites (user_id, recipe, favorites, feed) VALUES (%s, %s, %s, %s)', (user_id, Json(item), True, False))
    cur.close()

def delete_from_favorites(conn, id):
    cur = conn.cursor()
    cur.execute("SELECT feed FROM public.favorites WHERE recipe_id=%s", (id, ))
    is_shared = cur.fetchone()[0]
    cur.close()
    cur2 = conn.cursor()
    
    # Check if recipe shared in feed
    if is_shared:
        cur2.execute("UPDATE public.favorites SET favorites=False WHERE recipe_id=%s", (id, ))
    # Delete recipe from DB if it's not shared to feed
    else:
        cur2.execute("DELETE FROM public.favorites WHERE recipe_id=%s", (id, ))

    cur2.close()

def share(conn, msg, recipe_id):
    cur = conn.cursor()
    cur.execute('UPDATE public.favorites SET feed=true, feed_msg=%s, time=NOW() WHERE recipe_id=%s', (msg, recipe_id))
    cur.close()

def display_feed(conn):
    cur = conn.cursor()
    cur.execute("SELECT recipe_id, user_id, recipe, feed_msg, time FROM public.favorites WHERE feed=true ORDER BY time DESC LIMIT 20")
    items = cur.fetchall()
    cur.close()
    return items

def get_username(conn, id):
    cur = conn.cursor()
    cur.execute("SELECT username FROM public.users WHERE id=%s", (id,))
    username = cur.fetchone()[0]
    cur.close()
    return username

def get_recipe(conn, id):
    cur = conn.cursor()
    cur.execute("SELECT recipe FROM public.favorites WHERE recipe_id=%s", (id,))
    item = cur.fetchone()[0]
    cur.close()
    return item

def deactivate_user(conn, id):
    cur = conn.cursor()
    cur.execute("UPDATE public.users SET active=false WHERE id=%s", (id,))
    cur.close()