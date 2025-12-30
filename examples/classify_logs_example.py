#!/usr/bin/env python3

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
"""Example demonstrating log type classification with Chronicle."""

import argparse
import json
from datetime import datetime, timezone

from secops import SecOpsClient
from secops.exceptions import APIError


def create_sample_okta_log(username: str = "jdoe@example.com") -> str:
    """Create a sample OKTA log in JSON format.

    Args:
        username: The username to include in the log.

    Returns:
        A JSON string representing an OKTA log.
    """
    current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    okta_log = {
        "actor": {"displayName": "Joe Doe", "alternateId": username},
        "client": {
            "ipAddress": "192.168.1.100",
            "userAgent": {"os": "Mac OS X", "browser": "SAFARI"},
        },
        "displayMessage": "User login to Okta",
        "eventType": "user.session.start",
        "outcome": {"result": "SUCCESS"},
        "published": current_time,
    }

    return json.dumps(okta_log)


def create_sample_windows_log(username: str = "user123") -> str:
    """Create a sample Windows XML log.

    Args:
        username: The username to include in the log.

    Returns:
        An XML string representing a Windows Event log.
    """
    current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    return f"""<Event xmlns='http://schemas.microsoft.com/win/2004/08/events/event'>
  <System>
    <Provider Name='Microsoft-Windows-Security-Auditing'
      Guid='{{54849625-5478-4994-A5BA-3E3B0328C30D}}'/>
    <EventID>4624</EventID>
    <Version>1</Version>
    <Level>0</Level>
    <Task>12544</Task>
    <Opcode>0</Opcode>
    <Keywords>0x8020000000000000</Keywords>
    <TimeCreated SystemTime='{current_time}'/>
    <EventRecordID>202117513</EventRecordID>
    <Correlation/>
    <Execution ProcessID='656' ThreadID='700'/>
    <Channel>Security</Channel>
    <Computer>WIN-SERVER.xyz.net</Computer>
    <Security/>
  </System>
  <EventData>
    <Data Name='SubjectUserSid'>S-1-0-0</Data>
    <Data Name='SubjectUserName'>-</Data>
    <Data Name='TargetUserName'>{username}</Data>
    <Data Name='WorkstationName'>CLIENT-PC</Data>
    <Data Name='LogonType'>3</Data>
  </EventData>
</Event>"""


def create_sample_aws_cloudtrail_log() -> str:
    """Create a sample AWS CloudTrail log.

    Returns:
        A JSON string representing an AWS CloudTrail log.
    """
    current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    cloudtrail_log = {
        "eventVersion": "1.05",
        "userIdentity": {
            "type": "IAMUser",
            "principalId": "AIDAI1234EXAMPLE",
            "arn": "arn:aws:iam::123456789012:user/admin",
            "accountId": "123456789012",
            "accessKeyId": "AKIAI1234EXAMPLE",
            "userName": "admin",
        },
        "eventTime": current_time,
        "eventSource": "s3.amazonaws.com",
        "eventName": "GetObject",
        "awsRegion": "us-east-1",
        "sourceIPAddress": "192.0.2.1",
        "userAgent": "aws-cli/2.1.0",
        "requestParameters": {
            "bucketName": "my-bucket",
            "key": "example-file.txt",
        },
        "responseElements": None,
        "requestID": "1234567890ABCDEF",
        "eventID": "abcd1234-5678-90ef-ghij-klmnopqrstuv",
        "eventType": "AwsApiCall",
        "recipientAccountId": "123456789012",
    }

    return json.dumps(cloudtrail_log)


def log_classification(chronicle_client):
    """Raw log classification."""
    print("\n=== Log Type Classification Example ===\n")

    okta_log = create_sample_okta_log()
    print(f"Classifying OKTA log...")
    print(f"Raw log sample: {okta_log[:100]}...\n")

    try:
        log_type_predictions = chronicle_client.classify_logs(log_data=okta_log)

        if log_type_predictions:
            print("Predictions (sorted by confidence):")
            for idx, pred in enumerate(log_type_predictions[:5], 1):
                log_type = pred.get("logType", "Unknown")
                score = pred.get("score", 0)
                print(f"  {idx}. {log_type}: {score:.2%}")

            top_pred = log_type_predictions[0]
            confidence = top_pred.get("score", 0)
            print(f"\nTop prediction: {top_pred.get('logType')}")
            if confidence > 0.8:
                print("Confidence: High")
            elif confidence > 0.5:
                print("Confidence: Medium")
            else:
                print("Confidence: Low")
        else:
            print("No predictions available")

    except APIError as e:
        print(f"Error classifying log: {e}")
    except ValueError as e:
        print(f"Validation error: {e}")


def main():
    """Run the example."""
    parser = argparse.ArgumentParser(
        description="Example of log type classification with Chronicle"
    )
    parser.add_argument(
        "--customer-id",
        "--customer_id",
        required=True,
        help="Chronicle instance ID",
    )
    parser.add_argument(
        "--project-id", "--project_id", required=True, help="GCP project ID"
    )
    parser.add_argument("--region", default="us", help="Chronicle API region")

    args = parser.parse_args()

    client = SecOpsClient()

    chronicle = client.chronicle(
        customer_id=args.customer_id,
        project_id=args.project_id,
        region=args.region,
    )

    log_classification(chronicle)


if __name__ == "__main__":
    main()
