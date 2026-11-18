from Topology import create_network
import time
from mininet.log import setLogLevel #for at teste fejl

#Udfører kommando til at starte server
def start_server(server):
    server.cmd("python3 Code/Server.py &")

#Udfører kommando til at starte en klient
def start_client(client, duration):
    process = client.popen(
    "python3",
    "Code/Client.py",
    "--duration", str(duration),
    "--interval", "0.5",
    "--client-id", client.name
    )
    return process

def start_clients(net, num_clients, duration):
    processes = []

    for i in range(1, num_clients + 1):
        client = net.get(f"client{i}")
        process = start_client(client, duration)
        processes.append(process)

    return processes


def start_Capture(server):
    process = server.popen(

    ".venv/bin/python",
    "-u",
    "Code/PacketCapture.py"
    )

    return process

def main():
    net = create_network(
        num_clients=100, #ændret for nu
        num_attackers=0, #0 for baseline experimentet
        interactive=False
    )
    try:
        server = net.get("server")
        start_server(server)
        time.sleep(1)

        capture_process = start_Capture(server)
        time.sleep(1)

        processes = start_clients(net, num_clients=100, duration=300)

        for process in processes:
            exit_code = process.wait()
            print(f"Client exit code: {exit_code}")

        capture_exit_code = capture_process.wait()
        print(f"PacketCapture exit code: {capture_exit_code}")
    finally:
        net.stop()
    

if __name__ == "__main__":
    setLogLevel("debug") #test fejl.
    main()