import socket
import getpass
import time
import psutil
import requests


BACKEND_URL = "http://127.0.0.1:8000/api/activities/"

seen_connections = set()


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


def collect_network_connections():
    connections = []

    try:
        local_ip = get_local_ip()
        username = getpass.getuser()

        for conn in psutil.net_connections(kind="inet"):
            if not conn.raddr:
                continue

            destination_ip = conn.raddr.ip

            # Ignore local loopback connections
            if destination_ip in ("127.0.0.1", "::1"):
                continue

            connection_key = (local_ip, destination_ip)

            # Skip connections already reported
            if connection_key in seen_connections:
                continue

            seen_connections.add(connection_key)

            connections.append({
                "event_type": "network_connection",
                "source_ip": local_ip,
                "destination_ip": destination_ip,
                "username": username,
            })

    except (psutil.AccessDenied, psutil.Error) as e:
        print("Network monitoring error:", e)

    return connections


def send_data(data):
    try:
        response = requests.post(
            BACKEND_URL,
            json=data,
            timeout=5
        )

        print("Server response:", response.status_code)

        if response.status_code != 201:
            print(response.text)

    except requests.exceptions.RequestException as e:
        print("Connection error:", e)


def main():
    print("LAN Insider Threat Detection Agent Started")
    print("--------------------------------------------")

    while True:

        # System monitoring
        system_data = collect_system_data()

        print("\nSystem Data:")
        print(system_data)

        send_data(system_data)

        # Network monitoring
        network_connections = collect_network_connections()

        print("\nNetwork Connections Found:", len(network_connections))

        for connection in network_connections:
            print(connection)
            send_data(connection)

        time.sleep(10)


if __name__ == "__main__":
    main()