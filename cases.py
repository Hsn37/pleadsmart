import requests
import json


def split_and_parse_json(raw_response):
    # Try to split the response into separate JSON objects
    try:
        # Naive splitting; assumes responses are separated by a newline for this example
        parts = raw_response.split('\n')
        json_objects = [json.loads(part) for part in parts if part.strip()]
        return json_objects
    except json.JSONDecodeError as e:
        print("JSON parsing error:", e)
        print("Raw part causing issue:", part)
        return None


def search_corpus(query, k=3):
    url = "https://api.vectara.io:443/v1/stream-query"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": "zwt_jojaGgqldpGweMkDa6nf4jWdVFwfffEVcBtxhQ"
    }
    body = {
        "query": [{
            "query": query,
            "queryContext": "",
            "start": 0,
            "numResults": k,
            "contextConfig": {
                "charsBefore": 0,
                "charsAfter": 0,
                "sentencesBefore": 2,
                "sentencesAfter": 2,
                "startTag": "%START_SNIPPET%",
                "endTag": "%END_SNIPPET%"
            },
            "rerankingConfig": {
                "rerankerId": 272725718,
                "mmrConfig": {
                    "diversityBias": 0
                }
            },
            "corpusKey": [{
                "customerId": 2391333402,
                "corpusId": 4,
                "semantics": 0,
                "metadataFilter": "",
                "lexicalInterpolationConfig": {
                    "lambda": 0.025
                },
                "dim": []
            }],
            "summary": []
        }]
    }

    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 200:
        try:
            return split_and_parse_json(response.text)
        except Exception as e:
            print("Failed to parse JSON:", e)
            return None
    else:
        print(f"Failed to fetch data: {response.status_code}, Response body: {response.text}")
        return None



