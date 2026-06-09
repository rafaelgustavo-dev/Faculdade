import heapq
import random
from datetime import datetime

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import networkx as nx

NODES = {
    0: "Centro",
    1: "Batel",
    2: "Agua Verde",
    3: "Bigorrilho",
    4: "Portao",
    5: "CIC",
    6: "Pinheirinho",
    7: "Sitio Cercado",
    8: "Boqueirao",
    9: "Cajuru",
    10: "Bacacheri",
    11: "Boa Vista",
    12: "Sao Francisco",
    13: "Reboucas",
    14: "Pilarzinho",
}

# (origem, destino, tempo_base_em_minutos) — fluxo livre, sem pico/chuva
BASE_EDGES = [
    (0, 1, 8),  # Centro - Batel
    (0, 3, 10),  # Centro - Bigorrilho
    (0, 12, 7),  # Centro - Sao Francisco
    (0, 13, 9),  # Centro - Reboucas
    (0, 10, 19),  # Centro - Bacacheri
    (1, 2, 7),  # Batel - Agua Verde
    (1, 3, 7),  # Batel - Bigorrilho
    (1, 13, 6),  # Batel - Reboucas
    (2, 3, 8),  # Agua Verde - Bigorrilho
    (2, 4, 12),  # Agua Verde - Portao
    (2, 13, 9),  # Agua Verde - Reboucas
    (3, 4, 10),  # Bigorrilho - Portao
    (3, 12, 9),  # Bigorrilho - Sao Francisco
    (3, 14, 14),  # Bigorrilho - Pilarzinho
    (4, 5, 20),  # Portao - CIC
    (4, 6, 21),  # Portao - Pinheirinho
    (4, 7, 17),  # Portao - Sitio Cercado
    (5, 6, 17),  # CIC - Pinheirinho
    (6, 7, 19),  # Pinheirinho - Sitio Cercado
    (7, 8, 13),  # Sitio Cercado - Boqueirao
    (7, 13, 22),  # Sitio Cercado - Reboucas
    (8, 9, 16),  # Boqueirao - Cajuru
    (9, 10, 13),  # Cajuru - Bacacheri
    (9, 13, 14),  # Cajuru - Reboucas
    (10, 11, 11),  # Bacacheri - Boa Vista
    (10, 12, 14),  # Bacacheri - Sao Francisco
    (11, 12, 13),  # Boa Vista - Sao Francisco
    (11, 14, 9),  # Boa Vista - Pilarzinho
    (12, 14, 11),  # Sao Francisco - Pilarzinho
    (13, 8, 21),  # Reboucas - Boqueirao
]

POS = {
    0: (3.41, 6.66),
    1: (2.95, 6.46),
    2: (3.18, 6.07),
    3: (2.70, 6.72),
    4: (2.61, 5.49),
    5: (1.08, 5.64),
    6: (1.60, 2.71),
    7: (3.62, 3.26),
    8: (4.35, 4.76),
    9: (4.61, 6.35),
    10: (4.60, 7.71),
    11: (4.07, 8.11),
    12: (3.30, 7.09),
    13: (3.63, 6.39),
    14: (2.92, 8.03),
}

DIAS = ["Segunda", "Terca", "Quarta", "Quinta", "Sexta", "Sabado", "Domingo"]


def calcular_peso(base, hora, dia, clima):
    if 7 <= hora <= 9 or 17 <= hora <= 19:
        fator_pico = random.gauss(1.65, 0.12)
    else:
        fator_pico = random.gauss(1.0, 0.08)

    if dia < 5:
        fator_dia = random.gauss(1.25, 0.09)
    else:
        fator_dia = random.gauss(0.82, 0.07)

    if clima == "tempestade":
        fator_clima = random.gauss(1.90, 0.16)
    elif clima == "chuva":
        fator_clima = random.gauss(1.38, 0.11)
    else:
        fator_clima = random.gauss(1.0, 0.05)

    fator_pico = max(fator_pico, 0.6)
    fator_dia = max(fator_dia, 0.5)
    fator_clima = max(fator_clima, 0.7)

    return round(base * fator_pico * fator_dia * fator_clima, 1)


def construir_grafo(hora, dia, clima):
    # seed fixo por combinacao de condicoes — garante que o grafo seja igual toda vez que rodar com os mesmos parametros
    random.seed(
        hora * 100 + dia * 10 + {"normal": 0, "chuva": 1, "tempestade": 2}[clima]
    )

    G = nx.Graph()
    for n in NODES:
        G.add_node(n)
    for u, v, base in BASE_EDGES:
        peso = calcular_peso(base, hora, dia, clima)
        G.add_edge(u, v, weight=peso, base=base)
    return G


def dijkstra(G, origem, destino):
    dist = {n: float("inf") for n in G.nodes}
    anterior = {n: None for n in G.nodes}
    dist[origem] = 0
    heap = [(0.0, origem)]
    ja_visto = set()

    while heap:
        _, u = heapq.heappop(heap)
        if u in ja_visto:
            continue
        ja_visto.add(u)

        if u == destino:
            break

        for v in G.neighbors(u):
            novo = dist[u] + G[u][v]["weight"]
            if novo < dist[v]:
                dist[v] = novo
                anterior[v] = u
                heapq.heappush(heap, (novo, v))

    caminho = []
    no = destino
    while no is not None:
        caminho.append(no)
        no = anterior[no]
    caminho.reverse()

    if not caminho or caminho[0] != origem:
        return None, float("inf")

    return caminho, round(dist[destino], 1)


def desenhar(ax, G, origem, destino, rota1=None, rota2=None, titulo=""):
    ax.clear()
    ax.set_title(titulo, fontsize=10)
    ax.axis("off")

    cores = ["#e74c3c" if n in (origem, destino) else "#aec6cf" for n in G.nodes]

    nx.draw_networkx_nodes(G, POS, ax=ax, node_color=cores, node_size=600)
    nx.draw_networkx_labels(G, POS, ax=ax, labels=NODES, font_size=7)
    nx.draw_networkx_edges(G, POS, ax=ax, edge_color="#aaaaaa", width=1.2, alpha=0.5)

    edge_labels = {
        (u, v): f"{d['base']}|{d['weight']}" for u, v, d in G.edges(data=True)
    }
    nx.draw_networkx_edge_labels(
        G,
        POS,
        ax=ax,
        edge_labels=edge_labels,
        font_size=6,
        bbox=dict(boxstyle="round,pad=0.1", fc="white", alpha=0.6),
    )

    if rota2:
        nx.draw_networkx_edges(
            G,
            POS,
            ax=ax,
            edgelist=list(zip(rota2[:-1], rota2[1:])),
            edge_color="#e67e22",
            width=4.0,
            alpha=0.8,
            style="dashed",
        )
    if rota1:
        nx.draw_networkx_edges(
            G,
            POS,
            ax=ax,
            edgelist=list(zip(rota1[:-1], rota1[1:])),
            edge_color="#27ae60",
            width=4.5,
            alpha=0.95,
        )


def main():
    print("=== Previsao de Rotas de Transito — Curitiba ===")

    agora = datetime.now()
    hora = agora.hour
    dia = agora.weekday()

    print(f"\nHora atual: {hora:02d}h | {DIAS[dia]}")
    if (
        input("Usar horario atual? [Enter = sim / 'm' = manual]: ").strip().lower()
        == "m"
    ):
        hora = int(input("  Hora (0-23): "))
        dia = int(input("  Dia (0=Segunda ... 6=Domingo): "))

    print("  Clima: (1) Normal  (2) Chuva  (3) Tempestade")
    clima = {"2": "chuva", "3": "tempestade"}.get(
        input("  Opcao [1]: ").strip(), "normal"
    )

    G = construir_grafo(hora, dia, clima)

    print("\nBairros:")
    for n, nome in NODES.items():
        print(f"  [{n:2d}] {nome}")

    origem = int(input("\nOrigem  : "))
    destino = int(input("Destino : "))

    if origem not in NODES or destino not in NODES or origem == destino:
        print("Entrada invalida.")
        return

    rota1, tempo1 = dijkstra(G, origem, destino)

    if rota1 is None:
        print("Sem caminho disponivel.")
        return

    tempo_base1 = round(sum(G[u][v]["base"] for u, v in zip(rota1[:-1], rota1[1:])), 1)

    _, ax = plt.subplots(figsize=(12, 8))
    plt.subplots_adjust(left=0.02, right=0.98, top=0.92, bottom=0.08)

    em_pico = (7 <= hora <= 9) or (17 <= hora <= 19)
    # busca rota alternativa removendo as arestas da rota principal
    G2 = G.copy()
    for u, v in zip(rota1[:-1], rota1[1:]):
        G2.remove_edge(u, v)

    try:
        rota2 = nx.dijkstra_path(G2, origem, destino, weight="weight")
        tempo2 = round(nx.dijkstra_path_length(G2, origem, destino, weight="weight"), 1)
        tempo_base2 = round(
            sum(G[u][v]["base"] for u, v in zip(rota2[:-1], rota2[1:])), 1
        )
    except nx.NetworkXNoPath:
        rota2, tempo2, tempo_base2 = None, None, None

    titulo = (
        f"Resultado — {DIAS[dia]} {hora:02d}h | {clima}"
        + (" | PICO" if em_pico else "")
        + "\narestas: base|atual (min)"
    )
    desenhar(ax, G, origem, destino, rota1=rota1, rota2=rota2, titulo=titulo)

    legenda = [
        mpatches.Patch(color="#e74c3c", label="Origem / Destino"),
        mpatches.Patch(
            color="#27ae60",
            label=f"Principal: {' > '.join(NODES[n] for n in rota1)}\n"
            f"  Tempo estimado: {tempo1} min  |  Tempo base: {tempo_base1} min",
        ),
    ]
    if rota2:
        legenda.append(
            mpatches.Patch(
                color="#e67e22",
                label=f"Alternativa: {' > '.join(NODES[n] for n in rota2)}\n"
                f"  Tempo estimado: {tempo2} min  |  Tempo base: {tempo_base2} min",
            )
        )

    ax.legend(handles=legenda, loc="lower left", fontsize=8, framealpha=0.95)

    print(f"\nRota principal:   {' > '.join(NODES[n] for n in rota1)}")
    print(f"  Tempo estimado: {tempo1} min  |  Tempo base: {tempo_base1} min")
    if rota2:
        print(f"Rota alternativa: {' > '.join(NODES[n] for n in rota2)}")
        print(f"  Tempo estimado: {tempo2} min  |  Tempo base: {tempo_base2} min")

    plt.show()


if __name__ == "__main__":
    main()
