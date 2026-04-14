from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import re
import math

from main import (
pipeline,
gov_df,
extract_coordinates,
detect_type,
extract_site_features,
recommend,
find_nearest_location,
get_all_types,
in_range,
final_df
)

from rag.res_llm import get_resp
from rag.query_validator import validate_query

app = FastAPI()

# enable CORS

app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

print("Loading pipelines...")
retriever_obj, fuzzy_matcher, kg_retriever, matcher, markov = pipeline()
print("Pipelines loaded")

types_list = get_all_types(gov_df)
types_map = {t.lower(): t for t in types_list}

aliases = {
"dam": "Pakka Check Dam",
"anicut": "Anicut",
"talab": "Talab",
"pond": "Farm Pond",
"tank": "Percolation Tank",
"percolation": "Percolation Tank",
"johad": "Johad",
"whs": "WHS",
"nalah": "Nalah"
}

class Query(BaseModel):
    question: str

def ai(context, q):
    try:
        return get_resp([context], q)
    except:
        return context

def parse_infiltration(val):
    val = str(val)

    if "<" in val:
        num = float(re.findall(r'\d+\.?\d*', val)[0])
        return num - 1

    if ">" in val:
        num = float(re.findall(r'\d+\.?\d*', val)[0])
        return num + 1

    nums = re.findall(r'\d+\.?\d*', val)
    if nums:
        return float(nums[0])

    return None


def detect_intent(q):
    q = q.lower()

    if any(w in q for w in ["compare", "difference", "vs"]):
        return "compare"

    if any(w in q for w in ["highest", "maximum", "max", "lowest", "minimum", "min"]):
        return "extreme"

    if "slope" in q:
        return "slope"

    if "infiltration" in q:
        return "feature"

    if any(w in q for w in ["count", "total", "number"]):
        return "count"

    if any(w in q for w in ["top", "highest", "largest", "rank"]):
        return "topk"

    if any(w in q for w in ["list", "show", "display"]):
        return "list"

    if any(w in q for w in ["district", "village", "panchayat"]):
        return "location_filter"

    return "kg"


@app.post("/ask")
def ask_question(query: Query):
    question = query.question

    q_low = question.lower()

    greetings = ["hello", "hi", "hey", "good morning", "good evening", "good afternoon"]
    thanks = ["thanks", "thank you", "thx"]
    bye = ["bye", "goodbye", "see you"]

    if any(g in q_low for g in greetings):
        return {
            "answer": "Hello! 👋 I can help you explore water bodies like talabs, anicuts, percolation tanks, and more. Try asking something like 'talabs near bhilwara'."
        }

    if any(t in q_low for t in thanks):
        return {
            "answer": "You're welcome! Let me know if you want to explore water bodies."
        }

    if any(b in q_low for b in bye):
        return {
            "answer": "Goodbye! Feel free to come back if you need information about water bodies."
        }
    

    # validate query
    valid, error = validate_query(question)
    if not valid:
        return {"answer": error}

    # normalize query using fuzzy matcher
    corrected = fuzzy_matcher.correct(question)
    corrected = markov.correct(corrected)
    corrected = re.sub(r'\b(storage|tank|tanks|storage-tanks)\b', '', corrected.lower())
    corrected = " ".join(dict.fromkeys(corrected.split()))

    words = corrected.split()
    lat, lon = extract_coordinates(corrected)
    t = detect_type(corrected, types_map, aliases)
    has_numbers = bool(re.search(r'\d', corrected))
    intent = detect_intent(corrected)

    q = corrected

    # -------------------------
    # KG / RAG ENGINE
    # -------------------------
    if intent == "kg":

        results = kg_retriever.dynamic_search(corrected)

        if not results:
            return {"answer": "No relevant knowledge found."}

        context = "\n".join(results[:8])

        return {"answer": ai(context, q)}

    # -------------------------
    # INFILTRATION FILTER
    # -------------------------
    if "infiltration" in corrected and any(w in corrected for w in ["less", "more", "greater", "below", "above"]):

        match = re.search(r'\d+\.?\d*', corrected)

        if not match:
            return {"answer": "Provide a numeric value for infiltration."}

        val = float(match.group())

        results = []

        for _, r in matcher.df.iterrows():

            v = parse_infiltration(r["Infiltration"])

            if v is None:
                continue

            if any(w in corrected for w in ["less", "below"]):
                if v < val:
                    results.append(r["Body Type"])

            if any(w in corrected for w in ["more", "greater", "above"]):
                if v > val:
                    results.append(r["Body Type"])

        if not results:
            return {"answer": "No structures match this condition."}

        return {"answer": "Suitable structures:\n" + "\n".join([f"- {r}" for r in results])}

    # -------------------------
    # SLOPE QUERIES
    # -------------------------
    if intent == "slope":

        match = re.search(r'(\d+)\s*[-–]\s*(\d+)', corrected)

        if not match:
            return {"answer": "Provide slope like 5-15"}

        low, high = float(match.group(1)), float(match.group(2))

        results = []

        for _, r in matcher.df.iterrows():

            slope = str(r["Slope"])
            nums = re.findall(r'\d+\.?\d*', slope)

            if len(nums) >= 2:

                s_low, s_high = float(nums[0]), float(nums[1])

                if not (high < s_low or low > s_high):
                    results.append(r["Body Type"])

        if not results:
            return {"answer": "No structures match this slope"}

        return {"answer": ai("\n".join(results), q)}

    # -------------------------
    # TOP K AREA
    # -------------------------
    if intent == "topk":

        match = re.search(r'\d+', corrected)
        k = int(match.group()) if match else 5

        rows = recommend(gov_df, t if t else "")

        valid = [r for r in rows if r.get("area")]

        sorted_rows = sorted(valid, key=lambda x: x["area"], reverse=True)[:k]

        return {"answer": ai(str(sorted_rows), q)}

    # -------------------------
    # COUNT
    # -------------------------
    if intent == "count":

        rows = recommend(gov_df, t if t else "")

        return {"answer": f"Total: {len(rows)}"}

    # -------------------------
    # LOCATION SEARCH
    # -------------------------
    if lat and lon:

        row = find_nearest_location(lat, lon)

        context = f"""
```

Nearest structure
{row['Work_Name']} at {row['Village']}
{row['Latitude']}, {row['Longitude']}
"""


        return {"answer": ai(context, q)}

    # -------------------------
    # DEFAULT LIST
    # -------------------------
    rows = recommend(gov_df, t if t else "")

    return {"answer": ai(str(rows[:10]), q)}
