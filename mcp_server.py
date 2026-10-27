# -*- coding: utf-8 -*-
"""
GenPark Ctrip Itinerary DAG Optimizer MCP Server
Exposes itinerary scheduling and TSP optimization tools via JSON-RPC 2.0 over STDIO.
"""

import sys
import json
from client import GenParkCtripItineraryDAGOptimizer

def handle_request(req):
    method = req.get("method")
    req_id = req.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "genpark-ctrip-itinerary-dag-optimizer", "version": "1.0.0"}
            }
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "optimize_itinerary",
                        "description": "Optimizes multi-stop travel itineraries by solving constrained TSP routing with POI opening hours and fatigue decay.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "start_location": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "lat": {"type": "number"},
                                        "lon": {"type": "number"}
                                    },
                                    "required": ["lat", "lon"]
                                },
                                "day_start_hour": {"type": "number"},
                                "day_end_hour": {"type": "number"}
                            },
                            "required": ["start_location"]
                        }
                    }
                ]
            }
        }
    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "optimize_itinerary":
            opt = GenParkCtripItineraryDAGOptimizer()
            res = opt.optimize_itinerary(
                start_location=args.get("start_location", {"lat": 39.9042, "lon": 116.4074}),
                poi_candidates=args.get("poi_candidates"),
                day_start_hour=args.get("day_start_hour", 9.0),
                day_end_hour=args.get("day_end_hour", 21.0)
            )
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
            }
        else:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"}}
    else:
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32600, "message": f"Method '{method}' not supported"}}

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("MCP Server Discovery Test OK")
        opt = GenParkCtripItineraryDAGOptimizer()
        test_res = opt.optimize_itinerary({"lat": 39.9042, "lon": 116.4074})
        print(f"Test Stops: {test_res['total_scheduled_stops']}, Distance: {test_res['total_transit_distance_km']}km")
        return

    for line in sys.stdin:
        if not line.strip(): continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
