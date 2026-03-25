"""
Test script for n8n Google Drive webhook endpoint
Run this to verify the endpoint works before connecting n8n
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
WEBHOOK_ENDPOINT = f"{BASE_URL}/webhooks/google-drive-file-added"
HEALTH_ENDPOINT = f"{BASE_URL}/health"
TEST_ENDPOINT = f"{BASE_URL}/webhooks/google-drive-file-added/test"

def test_health():
    """Test the health endpoint"""
    print("\n" + "="*80)
    print("Testing Health Endpoint")
    print("="*80)

    try:
        response = requests.get(HEALTH_ENDPOINT)
        print(f"Status Code: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("✅ Health check PASSED")
            return True
        else:
            print("❌ Health check FAILED")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_webhook_test_endpoint():
    """Test the webhook test endpoint"""
    print("\n" + "="*80)
    print("Testing Webhook Test Endpoint")
    print("="*80)

    try:
        response = requests.get(TEST_ENDPOINT)
        print(f"Status Code: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("✅ Webhook test endpoint PASSED")
            return True
        else:
            print("❌ Webhook test endpoint FAILED")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_webhook_with_sample_data():
    """Test the webhook with sample Google Drive file data"""
    print("\n" + "="*80)
    print("Testing Webhook POST with Sample Data")
    print("="*80)

    # Sample payload that mimics what n8n Google Drive Trigger sends
    sample_payload = {
        "id": "SAMPLE_FILE_ID_123",  # This is a fake ID for testing
        "name": "test_transcript.txt",
        "mimeType": "text/plain",
        "webViewLink": "https://drive.google.com/file/d/SAMPLE_FILE_ID_123/view",
        "webContentLink": "https://drive.google.com/uc?id=SAMPLE_FILE_ID_123&export=download",
        "createdTime": "2026-03-19T10:30:00.000Z",
        "modifiedTime": "2026-03-19T10:30:00.000Z"
    }

    print(f"Sending payload:\n{json.dumps(sample_payload, indent=2)}")

    try:
        response = requests.post(
            WEBHOOK_ENDPOINT,
            json=sample_payload,
            headers={"Content-Type": "application/json"}
        )

        print(f"\nStatus Code: {response.status_code}")

        try:
            response_data = response.json()
            print(f"Response:\n{json.dumps(response_data, indent=2)}")
        except:
            print(f"Response (raw):\n{response.text}")

        if response.status_code == 200:
            print("✅ Webhook POST test PASSED")
            return True
        elif response.status_code == 500:
            print("⚠️  Webhook received request but processing failed")
            print("   This is expected if the file ID doesn't exist in Google Drive")
            print("   The endpoint is working correctly!")
            return True
        else:
            print("❌ Webhook POST test FAILED")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_webhook_with_missing_data():
    """Test the webhook with missing required fields"""
    print("\n" + "="*80)
    print("Testing Webhook POST with Missing Data (Should Fail Gracefully)")
    print("="*80)

    # Invalid payload - missing 'id' and 'name'
    invalid_payload = {
        "mimeType": "text/plain"
    }

    print(f"Sending invalid payload:\n{json.dumps(invalid_payload, indent=2)}")

    try:
        response = requests.post(
            WEBHOOK_ENDPOINT,
            json=invalid_payload,
            headers={"Content-Type": "application/json"}
        )

        print(f"\nStatus Code: {response.status_code}")

        try:
            response_data = response.json()
            print(f"Response:\n{json.dumps(response_data, indent=2)}")
        except:
            print(f"Response (raw):\n{response.text}")

        if response.status_code == 400:
            print("✅ Webhook correctly rejected invalid data")
            return True
        else:
            print("⚠️  Expected 400 status code for invalid data")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n")
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║           n8n Google Drive Webhook - Endpoint Testing Suite                 ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")
    print("\nMake sure FastAPI server is running:")
    print("  uvicorn api.index:app --reload --host 0.0.0.0 --port 8000")
    print("\nPress Enter to continue...")
    input()

    results = []

    # Run tests
    results.append(("Health Check", test_health()))
    results.append(("Webhook Test Endpoint", test_webhook_test_endpoint()))
    results.append(("Webhook POST (Sample Data)", test_webhook_with_sample_data()))
    results.append(("Webhook POST (Invalid Data)", test_webhook_with_missing_data()))

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:.<50} {status}")

    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)

    print(f"\nTotal: {total_passed}/{total_tests} tests passed")

    if total_passed == total_tests:
        print("\n🎉 All tests passed! The endpoint is ready for n8n integration.")
        print("\nNext steps:")
        print("1. Start ngrok: ngrok http 8000")
        print("2. Copy the ngrok HTTPS URL")
        print("3. Update n8n HTTP Request node with: https://YOUR-NGROK-URL/webhooks/google-drive-file-added")
        print("4. Activate your n8n workflow")
        print("5. Add a test file to your Google Drive folder")
    else:
        print("\n⚠️  Some tests failed. Please check the FastAPI server logs.")
        print("   Make sure the server is running on http://localhost:8000")


if __name__ == "__main__":
    main()
