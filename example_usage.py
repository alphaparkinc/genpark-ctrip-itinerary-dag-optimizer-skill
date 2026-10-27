# -*- coding: utf-8 -*-
"""
Example usage of GenParkCtripItineraryDAGOptimizer
Demonstrates intelligent route scheduling across Beijing cultural heritage POIs.
"""

from client import GenParkCtripItineraryDAGOptimizer

def main():
    optimizer = GenParkCtripItineraryDAGOptimizer()

    start_point = {
        "name": "Grand Hotel Beijing (Wangfujing)",
        "lat": 39.9080,
        "lon": 116.4110
    }

    res = optimizer.optimize_itinerary(
        start_location=start_point,
        day_start_hour=8.5,
        day_end_hour=20.0
    )

    print("================================================================")
    print("GenPark Ctrip Itinerary DAG Optimizer - Live Schedule")
    print("================================================================\n")
    print(f"Total Scheduled Stops : {res['total_scheduled_stops']} attractions")
    print(f"Total Walking/Transit : {res['total_transit_distance_km']} km")
    print(f"Total Day Duration    : {res['total_itinerary_duration_hours']} hours")
    print(f"Pace Verdict          : {res['itinerary_pace_verdict']}\n")
    print("Detailed Timeline Schedule:")
    for s in res["stops_timeline"]:
        rest_note = f" (Injected {s['injected_rest_break_mins']}m Tea Break)" if s['injected_rest_break_mins'] > 0 else ""
        print(f"  Step #{s['step_number']:02d}: {s['arrival_time']} - {s['departure_time']} | {s['poi_name']:<35} | {s['transit_distance_km']}km transit{rest_note}")

if __name__ == "__main__":
    main()
