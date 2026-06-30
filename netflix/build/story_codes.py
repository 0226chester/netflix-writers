"""This module contains functions to create a CSV file with unique shows and their corresponding Polti codes."""

import json
import logging
import os

import pandas as pd
import requests

from netflix.const import DATA_DIR

logger = logging.getLogger(__name__)

UNIQUE_SHOWS_CSV_PATH = os.path.join(DATA_DIR, "kaggle", "netflix-top-10-tv-shows-and-films", "unique-shows.csv")


def fetch_netflix_narrative_map():
    # The SPARQL endpoint allows us to query Wikidata's live graph database
    url = "https://query.wikidata.org/sparql"

    # This query finds all items that are TV series, have a Netflix ID, AND have a TV Tropes ID.
    query = """
    SELECT ?show ?showLabel ?genreLabel ?subjectLabel ?countryLabel ?languageLabel ?year ?article WHERE {

  ?show wdt:P31 wd:Q5398426 .

  OPTIONAL { ?show wdt:P136 ?genre . }

  OPTIONAL { ?show wdt:P921 ?subject . }

  OPTIONAL { ?show wdt:P495 ?country . }

  OPTIONAL { ?show wdt:P364 ?language . }

  OPTIONAL { ?show wdt:P571 ?inception . }

  BIND(YEAR(?inception) AS ?year)

  OPTIONAL {

    ?article schema:about ?show ;

             schema:isPartOf <https://en.wikipedia.org/> .

  }

  SERVICE wikibase:label {

    bd:serviceParam wikibase:language "en".

  }

}

LIMIT 200
    """

    logger.info("Querying Wikidata's narrative graph relationship table...")
    headers = {
        "User-Agent": "NetflixNarrativeCodifier/1.0",
        "Accept": "application/sparql-results+json",
    }
    response = requests.get(url, params={"format": "json", "query": query}, headers=headers, timeout=15)
    logger.info("URL: %s", response.url)
    logger.info("Content-Type: %s", response.headers.get("content-type"))

    if response.status_code == 200:
        logger.info("Successfully fetched data from Wikidata's narrative graph relationship table.")
        logger.info(response.text)
        data = response.json()
        results = data["results"]["bindings"]

        narrative_catalog = []
        for row in results:
            narrative_catalog.append(
                {
                    "title": row["showLabel"]["value"],
                    "wikidata_url": row["show"]["value"],
                    "netflix_id": row["netflixID"]["value"],
                    "tv_tropes_slug": row["tvTropesID"]["value"],
                }
            )

        return narrative_catalog
    else:
        logger.error("Error fetching data: %s", response.status_code)
        return []


if __name__ == "__main__":
    catalog = fetch_netflix_narrative_map()

    # Preview the linked data structure
    logger.info("Successfully linked %d shows directly to their structural narrative IDs!", len(catalog))
    logger.info(json.dumps(catalog[:3], indent=4))
