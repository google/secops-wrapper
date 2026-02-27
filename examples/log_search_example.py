# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Example usage of raw log search functionality."""

import argparse
from datetime import datetime, timedelta
from pprint import pprint

from secops.chronicle import ChronicleClient
from secops.exceptions import APIError


def main():
    """Run raw log search example."""
    parser = argparse.ArgumentParser(description="Chronicle Raw Log Search Example")
    parser.add_argument("--project_id", required=True, help="GCP Project ID")
    parser.add_argument("--customer_id", required=True, help="Chronicle Customer ID")
    parser.add_argument("--region", default="us", help="Chronicle Region")
    parser.add_argument("--query", default="user = \"user\"", help="Raw log search query")
    parser.add_argument("--days", type=int, default=1, help="Search time range in days")
    
    args = parser.parse_args()

    client = ChronicleClient(
        project_id=args.project_id,
        customer_id=args.customer_id,
        region=args.region,
    )

    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=args.days)

    print(f"Searching raw logs from {start_time} to {end_time}")
    print(f"Query: {args.query}")

    try:
        # Example 1: Basic Search
        results = client.search_raw_logs(
            query=args.query,
            start_time=start_time,
            end_time=end_time,
            page_size=10,
        )
        
        print("\nResults:")
        pprint(results)

        # Example 2: Filtering by Log Type (if available)
        # Note: Replace 'OKTA' with a valid log type in your environment
        # print("\nSearching with Log Type filter:")
        # results_filtered = client.search_raw_logs(
        #     query=args.query,
        #     start_time=start_time,
        #     end_time=end_time,
        #     page_size=10,
        #     log_types=["OKTA"]
        # )
        # pprint(results_filtered)

    except APIError as e:
        print(f"API Error: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
