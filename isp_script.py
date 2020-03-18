from isp_rest import HostManager, LinkManager, IntentManager, FlowManager
from isp_dijkstra import install_best_dijkstra_path, install_best_redundant_dijkstra_path
from isp_utility import del_intent


def running_program(src, dst, priority):  # Running main program
    avg_bytes, avg_rate, lowest_bw = get_statistic_bytes_information()
    if avg_bytes < (0.98 * lowest_bw):
        print("-A1---------------------------------------------")
        print("Total Bytes < 98% from Lowest Bandwidth")
        print("Total Bytes         = {by}".format(by=avg_bytes))
        print("Lowest Bandwidth    = {bw}".format(bw=(0.98 * lowest_bw)))
        intent = IntentManager()
        intent_id = intent.get_intent()
        del_intent(intent_id)
        topology = LinkManager()
        link1, src1_dev, src1_port, dst1_dev, dst1_port, link1_bw, link1_bw_def = topology.get_link()
        dijkstra_primary_shortest_path(src, dst, priority)
        while avg_bytes < (0.98 * lowest_bw):
            topology2 = LinkManager()
            link2, src2_dev, src2_port, dst2_dev, dst2_port, link2_bw, link2_bw_def = topology2.get_link()
            avg_bytes2, avg_rate2, lowest_bw2 = get_statistic_bytes_information()
            if lowest_bw >= (0.98 * lowest_bw2):
                if link2 != link1 or avg_bytes2 >= (0.98 * lowest_bw):
                    print("-A2---------------------------------------------")
                    print("Total Bytes >= 98% from Lowest Bandwidth")
                    print("Total Bytes         = {by}".format(by=avg_bytes2))
                    print("Lowest Bandwidth    = {bw}".format(bw=(0.98 *lowest_bw)))
                    running_program(src, dst, priority)
            else:
                if link2 != link1 or avg_bytes2 >= (0.98 * lowest_bw):
                    print("-A3---------------------------------------------")
                    print("Total Bytes >= 98% from Lowest Bandwidth")
                    print("Total Bytes         = {by}".format(by=avg_bytes2))
                    print("Lowest Bandwidth    = {bw}".format(bw=(0.98 * lowest_bw)))
                    running_program(src, dst, priority)
    elif avg_bytes >= (0.98 * lowest_bw):
        print("-B1---------------------------------------------")
        print("Total Bytes >= 98% from Lowest Bandwidth")
        print("Total Bytes         = {by}".format(by=avg_bytes))
        print("Lowest Bandwidth    = {bw}".format(bw=(0.98 *lowest_bw)))
        intent = IntentManager()
        intent_id = intent.get_intent()
        del_intent(intent_id)
        topology = LinkManager()
        link1, src1_dev, src1_port, dst1_dev, dst1_port, link1_bw, link1_bw_def = topology.get_link()
        dijkstra_primary_shortest_path(src, dst, priority)
        dijkstra_secondary_shortest_path(src, dst, priority)
        while avg_bytes >= (0.98 * lowest_bw):
            topology2 = LinkManager()
            link2, src2_dev, src2_port, dst2_dev, dst2_port, link2_bw, link2_bw_def = topology2.get_link()
            avg_bytes2, avg_rate2, lowest_bw2 = get_statistic_bytes_information()
            if lowest_bw >= (0.98 * lowest_bw2):
                if link2 != link1 or avg_bytes2 < (0.98 * lowest_bw):
                    print("-B2---------------------------------------------")
                    print("Total Bytes < 98% from Lowest Bandwidth")
                    print("Total Bytes         = {by}".format(by=avg_bytes2))
                    print("Lowest Bandwidth    = {bw}".format(bw=(0.98 * lowest_bw)))
                    running_program(src, dst, priority)
            else:
                if link2 != link1 or avg_bytes2 < (0.98 * lowest_bw):
                    print("-B3---------------------------------------------")
                    print("Total Bytes < 98% from Lowest Bandwidth")
                    print("Total Bytes         = {by}".format(by=avg_bytes2))
                    print("Lowest Bandwidth    = {bw}".format(bw=(0.98 *lowest_bw)))
                    running_program(src, dst, priority)


def input_host():  # define source and destination
    hosts = HostManager()
    host_id, host_mac, host_ip, host_location = hosts.get_hosts()
    for n in range(len(host_id)):
        print("-----------------------------------------------")
        print("{no}. Host ID           = {id}".format(no=n + 1, id=host_id[n]))
        print("IP Address           = {ip}".format(ip=host_ip[n]))
        print("MAC Address          = {mac}".format(mac=host_mac[n]))
        print("-----------------------------------------------\n")
    counter = 1
    src_input = 0
    dst_input = 0
    while counter == 1:
        src_input = int(input("Choose Source Host\n"))
        dst_input = int(input("Choose Destination Host\n"))
        if src_input in range(1, len(host_id) + 1):
            src_input = host_id[src_input - 1]
            if dst_input in range(1, len(host_id) + 1):
                dst_input = host_id[dst_input - 1]
                counter = 0
            else:
                print("Destination not in list")
                counter = 1
        else:
            print("Source not in list")
            counter = 1
    print("Source       : {src}\n".format(src=src_input))
    print("Destination  : {dst}\n".format(dst=dst_input))
    return src_input, dst_input


def dijkstra_primary_shortest_path(source, destination, priority):  # calculate path from source and destination
    print("\nCalculate Dijkstra Shortest Path....")
    try:
        print("\n----------------------------------Dijkstra Primary Path-----------------------------------\n")
        install_best_dijkstra_path(source, destination, priority)
    except TypeError:
        print("\nNo Path Found")


def dijkstra_secondary_shortest_path(source, destination, priority):  # calculate path from source and destination
    try:
        print("\n----------------------------------Dijkstra Secondary Path---------------------------------\n")
        install_best_redundant_dijkstra_path(source, destination, priority - 10)
    except TypeError:
        print("\nNo Path Found")


def get_statistic_bytes_information():
    flow = FlowManager()
    dev, port, bs, br, bd, rate, bw = flow.get_statistic()
    bs_ls = []
    br_ls = []
    bd_ls = []
    rate_ls = []
    bw_ls = []
    for i in range(len(dev)):
        if rate[i] > 0:
            bs_ls.append(bs[i])
            br_ls.append(br[i])
            bd_ls.append(bd[i])
            rate_ls.append(rate[i])
            bw_ls.append(bw[i])
    try:
        bs_ls = [bs_ls[x] // bd_ls[x] for x in range(len(bs_ls))]
        br_ls = [br_ls[x] // bd_ls[x] for x in range(len(br_ls))]
        avg_bs = sum(bs_ls) // len(bs_ls)
        avg_br = sum(br_ls) // len(br_ls)
        avg_bytes = (avg_bs + avg_br) // 2
        actual_bytes = avg_bytes
    except (ValueError, ZeroDivisionError):
        avg_bs = sum(bs) // len(bs)
        avg_br = sum(br) // len(br)
        avg_bytes = (avg_bs + avg_br) // 2
        actual_bytes = avg_bytes
    try:
        avg_rates = sum(rate_ls) // len(rate_ls)
    except (ValueError, ZeroDivisionError):
        avg_rates = sum(rate) // len(rate)
    try:
        bw_filter = [(bw_ls[x] // 1) for x in range(len(bw_ls))]
        lowest_bw = min(bw_filter)
    except ValueError:
        lowest_bw = min(bw)
    return actual_bytes, avg_rates, lowest_bw
