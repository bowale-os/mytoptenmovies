import requests

BASE_URL = "https://api.themoviedb.org/3"
# API_KEY = FROMTMBDAPI
# API_READ_ACCESS_TOKEN = #FROM TMBD API
headers = {'Authorization': f'Bearer {API_READ_ACCESS_TOKEN}'}


def search_movie(query):
    search_url = f'{BASE_URL}/search/movie'
    params = {
        'api_key': API_KEY,
        'query': query,
    }
    response = requests.get(search_url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        if results:
            return results
        else:
            print("No results found.")
    else:
        print(f'Error: {response.status_code}')


print(search_movie('Endgame'))
        # release_year = movie_form.release_year.data
        # rating = movie_form.rating.data
        # review = movie_form.review.data
        # overview = movie_form.overview.data
        # try:
        #     new_movie = Movie(title=title, release_year=release_year, rating=rating, review=review, overview=overview)
        #     db.session.add(new_movie)
        #     db.session.commit()
        #     return redirect(url_for("home"))
        #
        # except Exception as e:
        #     flash("Your input has an error")
        #     print("Error:", e)
