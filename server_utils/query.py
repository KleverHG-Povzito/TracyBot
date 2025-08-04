import socket
import time

def read_string(data, offset):
    end = data.find(b'\x00', offset)
    return data[offset:end].decode('utf-8'), end + 1

cache = {}
CACHE_TTL = 30  # segundos

def query_server(ip, port, max_retries=3):
    key = f"{ip}:{port}"
    now = time.time()
    if key in cache and now - cache[key]["time"] < CACHE_TTL:
        return cache[key]["data"], 1
    request_info = b'\xFF\xFF\xFF\xFFTSource Engine Query\x00'
    attempts = 0
    data = None
    for i in range(max_retries):
        attempts += 1
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(3)
            s.sendto(request_info, (ip, port))
            data, _ = s.recvfrom(4096)
            if data[4] == 0x41:  # Challenge
                challenge = data[5:]
                s.sendto(request_info + challenge, (ip, port))
                data, _ = s.recvfrom(4096)
            cache[key] = {"data": data, "time": now}
            return data, attempts
        except Exception:
            continue
    return None, attempts

def parse_server_info(data):
    if not data or len(data) < 6:
        return None
    try:
        offset = 6
        name, offset = read_string(data, offset)
        map_name, offset = read_string(data, offset)
        folder, offset = read_string(data, offset)
        game, offset = read_string(data, offset)
        offset += 2  # Saltar ID del juego (short)
        players = data[offset]
        max_players = data[offset + 1]
        return {
            "name": name,
            "map": map_name,
            "folder": folder,
            "game": game,
            "players": players,
            "max_players": max_players
        }
    except Exception:
        return None
