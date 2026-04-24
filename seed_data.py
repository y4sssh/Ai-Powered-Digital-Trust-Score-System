import requests
import random
import time

BASE_URL = "http://localhost:8000/api/collect"

def send_data(user_id, is_bot=False):
    if is_bot:
        data = {
            "userId": user_id,
            "browser": random.choice(["Chrome", "Firefox", "Bot-v1"]),
            "avgClickInterval": random.uniform(20, 100),
            "clickVariance": random.uniform(1, 10),
            "scrollSpeed": random.uniform(1500, 3000),
            "sessionDuration": random.uniform(10, 60),
            "tabSwitchCount": random.uniform(10, 50)
        }
    else:
        data = {
            "userId": user_id,
            "browser": random.choice(["Chrome", "Firefox", "Safari"]),
            "avgClickInterval": random.uniform(600, 1200),
            "clickVariance": random.uniform(30, 80),
            "scrollSpeed": random.uniform(50, 300),
            "sessionDuration": random.uniform(100, 1000),
            "tabSwitchCount": random.uniform(0, 3)
        }
    
    try:
        response = requests.post(BASE_URL, json=data)
        print(f"Sent data for {user_id} (Bot: {is_bot}) - Status: {response.status_code}, Score: {response.json().get('score')}")
    except Exception as e:
        print(f"Error sending data: {e}")

if __name__ == "__main__":
    print("Seeding data...")
    # Seed 10 normal users
    for i in range(10):
        send_data(f"user_{i}", is_bot=False)
    
    # Seed 3 bots
    for i in range(3):
        send_data(f"bot_{i}", is_bot=True)
    
    print("Seeding complete.")
