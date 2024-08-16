# https://github.com/Brntpcnr/Pwnagotchi/blob/main/check_wpa.py
import os
from scapy.all import rdpcap, EAPOL

def is_crackable(pcap_file):
    try:
        packets = rdpcap(pcap_file)
        eapol_packets = [pkt for pkt in packets if EAPOL in pkt]
        return len(eapol_packets) > 0
    except Exception as e:
        print(f"Error processing {pcap_file}: {e}")
        return False

def check_pcap_files(directory):
    if not os.path.isdir(directory):
        print(f"The directory '{directory}' does not exist.")
        return {}

    pcap_files = [f for f in os.listdir(directory) if f.endswith('.pcap')]
    if not pcap_files:
        print(f"No .pcap files found in the directory '{directory}'.")
        return {}

    results = {}
    for pcap_file in pcap_files:
        full_path = os.path.join(directory, pcap_file)
        print(f"Processing file: {full_path}")
        results[pcap_file] = is_crackable(full_path)
    return results

def main():
    directory = input("Enter the directory path containing .pcap files: ")
    results = check_pcap_files(directory)
    if results:
        for pcap_file, crackable in results.items():
            status = "Crackable" if crackable else "Not crackable"
            print(f"{pcap_file}: {status}")

if __name__ == "__main__":
    main()