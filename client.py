# -*- coding: utf-8 -*-
"""
GenPark Ctrip Itinerary DAG Optimizer Client
Plans multi-day travel schedules using TSP graph heuristics with fatigue decay and opening hour constraints.
Zero external dependencies -- Python 3.9+ standard library only.
"""

import math
from typing import Dict, Any, List

class GenParkCtripItineraryDAGOptimizer:
    """
    Optimizes multi-stop travel itineraries by solving constrained TSP routing
    with Haversine distances, POI opening time windows, and traveler fatigue modeling.
    """

    EARTH_RADIUS_KM = 6371.0

    def __init__(self, max_walking_km_per_day: float = 15.0, walking_speed_kmh: float = 4.2):
        self.max_walk = max_walking_km_per_day
        self.walk_speed = walking_speed_kmh

    def calculate_haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Computes great-circle distance between two GPS coordinates in kilometers."""
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2)
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))
        return round(self.EARTH_RADIUS_KM * c, 3)

    def optimize_itinerary(
        self,
        start_location: Dict[str, Any],
        poi_candidates: List[Dict[str, Any]] = None,
        day_start_hour: float = 9.0,
        day_end_hour: float = 21.0
    ) -> Dict[str, Any]:
        """
        Solves greedy constrained routing across candidate attractions.
        """
        if poi_candidates is None:
            poi_candidates = [
                {"id": "POI-01", "name": "The Palace Museum (Forbidden City)", "lat": 39.9163, "lon": 116.3972, "open_hour": 8.5, "close_hour": 17.0, "dwell_hours": 3.0, "rating": 4.9, "priority": 10},
                {"id": "POI-02", "name": "Summer Palace", "lat": 39.9998, "lon": 116.2755, "open_hour": 6.5, "close_hour": 18.0, "dwell_hours": 2.5, "rating": 4.8, "priority": 8},
                {"id": "POI-03", "name": "Temple of Heaven", "lat": 39.8822, "lon": 116.4066, "open_hour": 8.0, "close_hour": 17.5, "dwell_hours": 2.0, "rating": 4.7, "priority": 7},
                {"id": "POI-04", "name": "798 Art District", "lat": 39.9842, "lon": 116.4947, "open_hour": 10.0, "close_hour": 20.0, "dwell_hours": 2.0, "rating": 4.5, "priority": 6},
                {"id": "POI-05", "name": "Jingshan Park (Sunset Panoramic)", "lat": 39.9250, "lon": 116.3965, "open_hour": 6.0, "close_hour": 20.5, "dwell_hours": 1.0, "rating": 4.6, "priority": 9}
            ]

        curr_lat = start_location.get("lat", 39.9042)
        curr_lon = start_location.get("lon", 116.4074)
        curr_time = day_start_hour
        cumulative_distance = 0.0
        cumulative_fatigue = 0.0
        scheduled_stops = []
        unvisited = list(poi_candidates)

        step_idx = 1
        while unvisited and curr_time < day_end_hour:
            # Score each candidate: min distance + wait penalty + rating reward
            best_poi = None
            best_cost = float('inf')
            best_travel_time = 0.0
            best_dist = 0.0

            for poi in unvisited:
                d = self.calculate_haversine_distance(curr_lat, curr_lon, poi["lat"], poi["lon"])
                travel_time_h = d / self.walk_speed  # or transit approx
                arr_time = curr_time + travel_time_h

                # Time window compatibility
                if arr_time + poi["dwell_hours"] > poi["close_hour"]:
                    continue  # Will be closed before finishing

                wait_time_h = max(0.0, poi["open_hour"] - arr_time)
                cost = (d * 1.5) + (wait_time_h * 3.0) - (poi["rating"] * 2.0) - (poi["priority"] * 1.2)

                if cost < best_cost:
                    best_cost = cost
                    best_poi = poi
                    best_dist = d
                    best_travel_time = travel_time_h

            if not best_poi:
                break  # No more viable stops within time constraints

            unvisited.remove(best_poi)
            arr_time = curr_time + best_travel_time
            start_visit_time = max(arr_time, best_poi["open_hour"])
            departure_time = start_visit_time + best_poi["dwell_hours"]

            cumulative_distance += best_dist
            cumulative_fatigue += (best_dist * 0.75) + (best_poi["dwell_hours"] * 0.8)

            # Check if rest buffer needed
            injected_rest_mins = 0
            if cumulative_fatigue > 8.0:
                injected_rest_mins = 45
                departure_time += (injected_rest_mins / 60.0)
                cumulative_fatigue = max(0.0, cumulative_fatigue - 4.5)

            scheduled_stops.append({
                "step_number": step_idx,
                "poi_id": best_poi["id"],
                "poi_name": best_poi["name"],
                "arrival_time": f"{int(start_visit_time):02d}:{int((start_visit_time % 1) * 60):02d}",
                "departure_time": f"{int(departure_time):02d}:{int((departure_time % 1) * 60):02d}",
                "dwell_hours": best_poi["dwell_hours"],
                "transit_distance_km": round(best_dist, 2),
                "injected_rest_break_mins": injected_rest_mins,
                "rating": best_poi["rating"]
            })

            curr_lat = best_poi["lat"]
            curr_lon = best_poi["lon"]
            curr_time = departure_time
            step_idx += 1

        total_transit_km = round(cumulative_distance, 2)
        total_trip_hours = round(curr_time - day_start_hour, 2)

        return {
            "total_scheduled_stops": len(scheduled_stops),
            "total_transit_distance_km": total_transit_km,
            "total_itinerary_duration_hours": total_trip_hours,
            "itinerary_pace_verdict": "OPTIMIZED_BALANCED" if cumulative_fatigue < 10.0 else "INTENSE_EXPEDITION",
            "stops_timeline": scheduled_stops,
            "unscheduled_pois_count": len(unvisited)
        }
