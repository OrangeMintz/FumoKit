import httpx
import re

BASE_URL = "https://fitgirl-repacks.site/"

class FitGirl:
    def __init__(self):
        pass

    @staticmethod
    def new_posts():
        try:
            response = httpx.get(BASE_URL)

            results = re.findall(r'<h1 class="entry-title"><a href="(.+?)" rel="bookmark">(.+?)</a></h1>', response.text)
            results = [i for i in results if "Upcoming Repacks" not in i]
            json_results = {"status": "Success", "results": []}

            for result in results:
                json_results["results"].append({"url": result[0], "title": result[1]})

            return json_results

        except Exception as e:
            return {"status": "Error", "message": str(e)}