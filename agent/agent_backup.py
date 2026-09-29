import socket
import getpass
import time
import psutil
import requests


BACKEND_URL = "http://127.0.0.1:8000/api/activities/"


def get_local_ip():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        local_ip = sock.getsockname()[0]
        sock.close()
        return local_ip
    except Exception:
        return "127.0.0.1"


def collect_system_data():
    return {
        "event_type": "system_monitor",
        "source_ip": get_local_ip(),
        "hostname": socket.gethostname(),
        "username": getpass.getuser(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "process_count": len(psutil.pids()),
    }

def send_data(data):
    try:
        response = requests.post(
            BACKEND_URL,
            json=data,
            timeout=5
        )

        print("Server response:", response.status_code)
        print(response.text)

    except requests.exceptions.RequestException as e:
        print("Connection error:", e)


def main():
    print("LAN Insider Threat Detection Agent Started")
    print("--------------------------------------------")

    while True:
        data = collect_system_data()

        print("\nCollected Data:")
        print(data)

        send_data(data)

        time.sleep(10)


if __name__ == "__main__":
    main()