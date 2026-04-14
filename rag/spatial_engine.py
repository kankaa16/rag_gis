import math
import pandas as pd


def haversine(lat1, lon1, lat2, lon2):

    R = 6371  # km

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c

class SpatialEngine:

    def __init__(self, csv_path):

        df = pd.read_csv(csv_path)

        self.data = []

        for _, row in df.iterrows():

            self.data.append({
                "id": row["water_body_id"],
                "lat": row["avg_lat"],
                "lon": row["avg_lon"],
                "area": row["area_m2"]
            })

    def nearby(self, lat, lon, radius_km=10):

        results = []

        for body in self.data:

            d = haversine(lat, lon, body["lat"], body["lon"])

            if d <= radius_km:
                results.append((d, body))

        results.sort()

        return results  
          
    def nearest(self, lat, lon):

        best = None
        best_dist = float("inf")

        for body in self.data:

            d = haversine(lat, lon, body["lat"], body["lon"])

            if d < best_dist:
                best_dist = d
                best = body

        return best, best_dist         
    
    def largest_nearby(self, lat, lon, radius_km=10):

        candidates = self.nearby(lat, lon, radius_km)

        if not candidates:
            return None

        return max(candidates, key=lambda x: x[1]["area"])   