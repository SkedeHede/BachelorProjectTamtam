from Topology import create_network
from Merge import merge_csv
import time
from mininet.log import setLogLevel #for at teste fejl
from pathlib import Path
import json
from datetime import datetime

#===========================================#
#        Experiment configurations          #
#===========================================#

NUM_CLIENTS = 100          #Antal legitime klienter
DURATION = 300             #Eksperimentets varighed i sekunder
CLIENT_INTERVAL = 0.5      #Sekunder mellem klientrequests
CAPTURE_DURATION = DURATION + 15   #Varighed af packet capture

NUM_ATTACKERS = 0          #Antal angribere (0 = baseline)
ATTACK_START = 15
ATTACK_DURATION = 30
ATTACK_RATE = 10



EXPERIMENT_TYPE = "baseline"  #baseline / attack / mitigation


#Global counter til eksåerimentforsøg
Counter_file = Path("Experiment_Counter.txt")

def get_next_experiment_ID():
    counter_file = Path("Experiment_Counter.txt")

    if counter_file.exists():
        experiment_id = int(counter_file.read_text().strip())
    else:
        experiment_id = 0

    counter_file.write_text(str(experiment_id + 1))

    return experiment_id

#Udfører kommando til at starte server
def start_server(server):
    server.cmd("python3 Code/Server.py &")

#Udfører kommando til at starte en klient
def start_client(client, duration, experiment_dir, interval):
    process = client.popen(
    "python3",
    "Code/Client.py",
    "--duration", str(duration),
    "--interval", str(interval),
    "--client-id", client.name,
    "--log-dir", str(experiment_dir)
    )
    return process

def start_clients(net, num_clients, duration, experiment_dir, interval):
    processes = []

    for i in range(1, num_clients + 1):
        client = net.get(f"client{i}")
        process = start_client(client, duration, experiment_dir, interval)
        processes.append(process)

    return processes

def start_attacker(attacker, duration, rate, experiment_dir):
    process = attacker.popen(
        "python3",
        "Code/Attacker.py",
        "--attacker-id", attacker.name,
        "--duration", str(duration),
        "--rate", str(rate),
        "--log-dir", str(experiment_dir)
    )

    return process


def start_Capture(server, pcap_file, capture_duration):
    process = server.popen(

    ".venv/bin/python",
    "-u",
    "Code/PacketCapture.py",
    "--output", str(pcap_file),
    "--duration", str(capture_duration)
    )

    return process


def save_experiment_config(experiment_dir, experiment_id):
    config = {
        "experiment_id": experiment_id,
        "experiment_type": EXPERIMENT_TYPE,
        "timestamp": datetime.now().isoformat(),
        "num_clients": NUM_CLIENTS,
        "num_attackers": NUM_ATTACKERS,
        "duration_seconds": DURATION,
        "client_interval_seconds": CLIENT_INTERVAL,
        "capture_duration_seconds": CAPTURE_DURATION
    }

    config_path = Path(experiment_dir) / "config.json"

    with open(config_path, "w") as file:
        json.dump(config, file, indent=4)

    print(f"Experiment configuration saved to {config_path}")


def main():

    experiment_id = get_next_experiment_ID()
    experiment_dir = Path("logs") / "csv" / f"experiment_{experiment_id:03d}"

    experiment_dir.mkdir(parents=True, exist_ok=True)


    pcap_dir = Path("logs") / "pcap" 
    pcap_dir.mkdir(parents=True, exist_ok=True)

    pcap_file = pcap_dir / f"experiment_{experiment_id:03d}.pcap"

    
    save_experiment_config(experiment_dir, experiment_id)

    net = create_network(
        num_clients=NUM_CLIENTS, #ændret for nu
        num_attackers=NUM_ATTACKERS, #0 for baseline experimentet
        interactive=False
    )
    try:
        server = net.get("server")
        start_server(server)
        time.sleep(1)

        capture_process = start_Capture(server, pcap_file, CAPTURE_DURATION)
        time.sleep(1)

        processes = start_clients(net, num_clients=NUM_CLIENTS, duration=DURATION, experiment_dir=experiment_dir, interval=CLIENT_INTERVAL)

        for process in processes:
            exit_code = process.wait()
            print(f"Client exit code: {exit_code}")

        capture_exit_code = capture_process.wait()
        print(f"PacketCapture exit code: {capture_exit_code}")
    finally:
        net.stop()
        merge_csv(experiment_dir)
    

if __name__ == "__main__":
    setLogLevel("debug") #test fejl.
    main()