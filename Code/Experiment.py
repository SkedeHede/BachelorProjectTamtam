from Topology import create_network
import time

#Udfører kommando til at starte server
def start_server(server):
    server.cmd("python3 Code/Server.py &")

#Udfører kommando til at starte en klient
def start_client(client, requests):
    process = client.popen(
    "python3",
    "Code/Client.py",
    "--requests", str(requests),
    "--interval", "0.5",
    "--client-id", client.name
    )
    return process

def start_clients(net, num_clients, requests):
    processes = []

    for i in range(1, num_clients + 1):
        client = net.get(f"client{i}")
        process = start_client(client, requests)
        processes.append(process)

    return processes



def main():
    net = create_network(
        num_clients=2,
        num_attackers=1,
        interactive=False
    )
    try:
        server = net.get("server")
        start_server(server)
        time.sleep(1)

        processes = start_clients(net, num_clients=2, requests=10)

        for process in processes:
            process.wait()

    finally:
        net.stop()


if __name__ == "__main__":
    main()