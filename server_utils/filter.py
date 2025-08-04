def vacios(servidores):
    return [s for s in servidores if s["players"] == 0]

def llenos(servidores):
    return [s for s in servidores if s["players"] >= s["max_players"]]
