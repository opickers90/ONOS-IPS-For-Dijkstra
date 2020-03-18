from collections import defaultdict
from heapq import *
from isp_rest import LinkManager
from isp_utility import intent_p2p_install, intent_s2mp_install, intent_m2sp_install


def dijkstra(edges, source, destination):  # Dijkstra Shortest Path Algorithm
    graph = defaultdict(list)
    for node_src, node_dst, bw in edges:
        graph[node_src].append((bw, node_dst))

    # dist records the min value of each node in heap.
    queue, seen, distance = [(0, source, ())], set(), {source: 0}
    while queue:
        (cost, vertex1, path) = heappop(queue)
        if vertex1 in seen:
            continue

        seen.add(vertex1)
        path += (vertex1,)
        if vertex1 == destination:
            return cost, path

        for bw, vertex2 in graph.get(vertex1, ()):
            if vertex2 in seen:
                continue

            # Not every edge will be calculated. The edge which can improve the value of node in heap will be useful.
            if vertex2 not in distance or cost + bw < distance[vertex2]:
                distance[vertex2] = cost + bw
                heappush(queue, (distance[vertex2], vertex2, path))

    return float("inf")


def generate_edge():  # Generate Primary Topology
    link = LinkManager()
    link_json, src_dev, src_port, dst_dev, dst_port, link_bw, link_bw_def = link.get_link()
    ref_bw = 10000
    cost = [ref_bw // int(link_bw[x]) for x in range(len(link_bw))]
    edges = list(zip(src_dev, dst_dev, cost))
    device_in = list(zip(src_dev, src_port))
    device_eg = list(zip(dst_dev, dst_port))
    edges_with_port = list(zip(device_in, device_eg, cost))
    return edges, device_in, device_eg, edges_with_port


def calculate_dijkstra_path(src, dst):  # Calculate Primary Best Path from Primary Topology
    edge, dev_in, dev_eg, edge_port = generate_edge()
    di_dijkstra = []
    de_dijkstra = []
    pi_dijkstra = []
    pe_dijkstra = []
    di = []
    de = []
    pi = []
    pe = []

    path_dijkstra = dijkstra(edge, src, dst)
    for n in range(len(path_dijkstra[1]) - 1):
        for o in range(len(edge_port)):
            if (path_dijkstra[1][n] == edge_port[o][0][0] and path_dijkstra[1][n + 1] ==
                    edge_port[o][1][0]):
                di_dijkstra.append(edge_port[o][0][0])
                pi_dijkstra.append(edge_port[o][0][1])
                de_dijkstra.append(edge_port[o][1][0])
                pe_dijkstra.append(edge_port[o][1][1])
                if "of:" in edge_port[o][0][0]:
                    de.append(edge_port[o][0][0])
                    pe.append(edge_port[o][0][1])
                if "of:" in edge_port[o][1][0]:
                    di.append(edge_port[o][1][0])
                    pi.append(edge_port[o][1][1])
    return path_dijkstra, di_dijkstra, pi_dijkstra, de_dijkstra, pe_dijkstra, di, pi, de, pe


def install_best_dijkstra_path(src, dst, priority):  # Primary Path Intent Installation
    path_dijkstra, dij, pij, dej, pej, di, pi, de, pe = calculate_dijkstra_path(src, dst)
    path = " - ".join(path_dijkstra[1])
    print("Dijkstra's Shortest Path Calculation Result: \n")
    print(path)
    print("Total Cost for this path: {cost}\n".format(cost=path_dijkstra[0]))
    print("------------------------------------------------------------------------------------------")
    print("Installing Best-Path Dijkstra's Shortest Path..\n")
    # Install Forwarding Intent
    print("Forwarding Intents based on Path Information")
    if len(di) == len(de):
        for n in range(len(de)):
            response = intent_p2p_install(pi[n], di[n], pe[n], de[n], priority)
            print("{no}.  Ingress = {di}:{pi} <--->  Egress = {de}:{pe} : status {stt}".format(no=n + 1, di=di[n],
                                                                                               pi=pi[n], de=de[n],
                                                                                               pe=pe[n],
                                                                                               stt=response))
    # Install Reverse Forwarding Intent
    print("Reverse/Backwarding Intents based on Path Information")
    if len(di) == len(de):
        for n in range(len(de)):
            response = intent_p2p_install(pe[n], de[n], pi[n], di[n], priority)
            print("{no}.  Ingress = {de}:{pe} <--->  Egress = {di}:{pi} : status {stt}".format(no=n + 1, di=di[n],
                                                                                               pi=pi[n],
                                                                                               de=de[n], pe=pe[n],
                                                                                               stt=response))


def generate_redundant_edge(src, dst):  # Generate redundant Topology
    edges, dev_in, dev_eg, edge_port = generate_edge()
    path_dijkstra, dij, pij, dej, pej, di, pi, de, pe = calculate_dijkstra_path(src, dst)
    delete_edge = []
    redundant_edges = []
    for y in range(len(edges)):
        for x in range(len(dij)):
            if edges[y][0] == dij[x] and edges[y][1] == dej[x]:
                if "of:" in edges[y][0] and "of:" in edges[y][1]:
                    delete_edge.append(edges[y])
            if edges[y][1] == dij[x] and edges[y][0] == dej[x]:
                if "of:" in edges[y][1] and "of:" in edges[y][0]:
                    delete_edge.append(edges[y])
    delete_edge.sort()
    even = [delete_edge[n] for n in range(len(delete_edge)) if n % 2 == 0]
    odd = [delete_edge[n] for n in range(len(delete_edge)) if n % 2 != 0]
    new_del_edge = list(zip(even, odd))

    for n in range(len(new_del_edge)):
        temp_edge = edges[:]
        redundant_edges.append(temp_edge)

    for n in range(len(redundant_edges)):
        redundant_edges[n].remove(new_del_edge[n][0])
        redundant_edges[n].remove(new_del_edge[n][1])

    for i in range(len(delete_edge)):
        edges.remove(delete_edge[i])
    return redundant_edges, edge_port


def calculate_redundant_dijkstra_path(src, dst):  # Calculate All Redundant Path
    redundant_edge, edge_port = generate_redundant_edge(src, dst)
    di_dijkstra = []
    de_dijkstra = []
    pi_dijkstra = []
    pe_dijkstra = []
    di = []
    de = []
    pi = []
    pe = []

    redundant_dijkstra = []
    redundant_di_dijkstra = []
    redundant_de_dijkstra = []
    redundant_pi_dijkstra = []
    redundant_pe_dijkstra = []
    redundant_di = []
    redundant_de = []
    redundant_pi = []
    redundant_pe = []
    new_redundant_dijkstra = []

    for edge in redundant_edge:
        path_dijkstra = dijkstra(edge, src, dst)
        redundant_dijkstra.append(path_dijkstra)

    redundant_dijkstra.sort()
    for i in redundant_dijkstra:
        if i not in new_redundant_dijkstra:
            new_redundant_dijkstra.append(i)

    for index in range(len(new_redundant_dijkstra)):
        for n in range(len(new_redundant_dijkstra[index][1]) - 1):
            for o in range(len(edge_port)):
                if (new_redundant_dijkstra[index][1][n] == edge_port[o][0][0] and
                        new_redundant_dijkstra[index][1][n + 1] == edge_port[o][1][0]):
                    di_dijkstra.append(edge_port[o][0][0])
                    pi_dijkstra.append(edge_port[o][0][1])
                    de_dijkstra.append(edge_port[o][1][0])
                    pe_dijkstra.append(edge_port[o][1][1])
                    if "of:" in edge_port[o][0][0]:
                        de.append(edge_port[o][0][0])
                        pe.append(edge_port[o][0][1])
                    if "of:" in edge_port[o][1][0]:
                        di.append(edge_port[o][1][0])
                        pi.append(edge_port[o][1][1])
        redundant_di_dijkstra.append(di_dijkstra)
        redundant_de_dijkstra.append(de_dijkstra)
        redundant_pi_dijkstra.append(pi_dijkstra)
        redundant_pe_dijkstra.append(pe_dijkstra)
        redundant_di.append(di)
        redundant_de.append(de)
        redundant_pi.append(pi)
        redundant_pe.append(pe)
    return (new_redundant_dijkstra, redundant_di_dijkstra, redundant_pi_dijkstra, redundant_de_dijkstra,
            redundant_pe_dijkstra, redundant_di, redundant_pi, redundant_de, redundant_pe)


def install_best_redundant_dijkstra_path(src, dst, priority):  # Best Redundant Path Intent Installation
    path, dij, pij, dej, pej, di, pi, de, pe = calculate_dijkstra_path(src, dst)
    path_red, dij_red, pij_red, dej_red, pej_red, di_red, pi_red, de_red, pe_red = calculate_redundant_dijkstra_path(
        src, dst)
    pi_a = []
    di_a = []
    pe_a = []
    de_a = []
    priority_multi = priority + 20
    print("Dijkstra's Shortest Path Calculation Result: \n")
    print("\nTotal Redundant Path: {total}\n".format(total=len(path_red)))
    for i in range(len(path_red)):
        path = " - ".join(path_red[i][1])
        print("{no}: {path}".format(no=i + 1, path=path))
        print("Total Cost for this path: {cost}\n".format(cost=path_red[i][0]))
    print("------------------------------------------------------------------------------------------")
    print("Installing Best-Path Redundant Dijkstra's Shortest Path...\n")

    # Install Forwarding Intent
    if len(di_red[0]) == len(de_red[0]):
        for n in range(len(path_red[0][1]) - 2):
            pi_a.append(pi_red[0][n])
            di_a.append(di_red[0][n])
            pe_a.append(pe_red[0][n])
            de_a.append(de_red[0][n])

    devin_red = list(zip(di_a, pi_a))
    devout_red = list(zip(de_a, pe_a))
    devin = list(zip(di, pi))
    devout = list(zip(de, pe))

    if len(di_red[0]) == len(de_red[0]):
        for n in range(len(path_red[0][1]) - 2):
            response = intent_p2p_install(pi_red[0][n], di_red[0][n], pe_red[0][n], de_red[0][n], priority)
            print(
                "{no}.  Ingress = {di}:{pi} <--->  Egress = {de}:{pe} : status {stt}".format(no=n + 1,
                                                                                             di=di_red[0][n],
                                                                                             pi=pi_red[0][n],
                                                                                             de=de_red[0][n],
                                                                                             pe=pe_red[0][n],
                                                                                             stt=response))
    if len(devin_red) == len(devout_red):
        for x in range(len(devin)):
            for y in range(len(devin_red)):
                if (devin[x][0] == devin_red[y][0] and devin[x][1] != devin_red[y][1]) and \
                        (devout[x][0] == devout_red[y][0] and devout[x][1] == devout_red[y][1]):
                    response = intent_m2sp_install(devin[x][1], devin[x][0], devin_red[y][1], devin_red[y][0],
                                                   devout_red[y][1], devout_red[y][0], priority_multi)
                    print("{no}.  Ingress = {di1}:{pi1}:{di2}:{pi2} <--->  Egress1 = {de}:{pe} : status {stt}".
                          format(no=y + 1,
                                 di1=devin[x][0],
                                 pi1=devin[x][1],
                                 di2=devin_red[y][0],
                                 pi2=devin_red[y][1],
                                 de=devout_red[y][0],
                                 pe=devout_red[y][1],
                                 stt=response))
                elif (devin[x][0] == devin_red[y][0] and devin[x][1] == devin_red[y][1]) and \
                        (devout[x][0] == devout_red[y][0] and devout[x][1] != devout_red[y][1]):
                    response = intent_s2mp_install(devin_red[y][1], devin_red[y][0], devout[x][1],
                                                   devout[x][0], devout_red[y][1], devout_red[y][0], priority_multi)
                    print("{no}.  Ingress = {di}:{pi} <--->  Egress1 = {de1}:{pe1}:{de2}:{pe2}  : status {stt}".
                          format(no=y + 1,
                                 di=devin_red[y][0],
                                 pi=devin_red[y][1],
                                 de1=devout[x][0],
                                 pe1=devout[x][1],
                                 de2=devout_red[y][0],
                                 pe2=devout_red[y][1],
                                 stt=response))

    # Install Reverse Forwarding Intent
    print("\n")
    print("Reverse/Backwarding Intents based on Path Information")
    if len(di_red[0]) == len(de_red[0]):
        for n in range(len(path_red[0][1]) - 2):
            response = intent_p2p_install(pe_red[0][n], de_red[0][n], pi_red[0][n], di_red[0][n], priority)
            print(
                "{no}.  Ingress = {de}:{pe} <--->  Egress = {di}:{pi} : status {stt}".format(no=n + 1,
                                                                                             di=di_red[0][n],
                                                                                             pi=pi_red[0][n],
                                                                                             de=de_red[0][n],
                                                                                             pe=pe_red[0][n],
                                                                                             stt=response))
    if len(devin_red) == len(devout_red):
        for x in range(len(devin)):
            for y in range(len(devin_red)):
                if (devin[x][0] == devin_red[y][0] and devin[x][1] != devin_red[y][1]) and \
                        (devout[x][0] == devout_red[y][0] and devout[x][1] == devout_red[y][1]):
                    response = intent_s2mp_install(devout_red[y][1], devout_red[y][0], devin[x][1], devin[x][0],
                                                   devin_red[y][1], devin_red[y][0], priority_multi)
                    print("{no}.  Ingress = {di}:{pi} <--->  Egress1 = {de1}:{pe1}:{de2}:{pe2}  : status {stt}".
                          format(no=y + 1,
                                 di=devout_red[y][0],
                                 pi=devout_red[y][1],
                                 de1=devin[x][0],
                                 pe1=devin[x][1],
                                 de2=devin_red[y][0],
                                 pe2=devin_red[y][1],
                                 stt=response))
                elif (devin[x][0] == devin_red[y][0] and devin[x][1] == devin_red[y][1]) and \
                        (devout[x][0] == devout_red[y][0] and devout[x][1] != devout_red[y][1]):
                    response = intent_m2sp_install(devout[x][1], devout[x][0], devout_red[y][1], devout_red[y][0],
                                                   devin_red[y][1], devin_red[y][0], priority_multi)

                    print("{no}.  Ingress = {di1}:{pi1}:{di2}:{pi2} <--->  Egress1 = {de}:{pe} : status {stt}".
                          format(no=y + 1,
                                 di1=devout[x][0],
                                 pi1=devout[x][1],
                                 di2=devout_red[y][0],
                                 pi2=devout_red[y][1],
                                 de=devin_red[y][0],
                                 pe=devin_red[y][1],
                                 stt=response))
