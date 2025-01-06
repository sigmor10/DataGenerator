import random
import csv
import string
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Manager

import faker
import datetime


class SkiCenter:
    def __init__(self, s_id, name):
        self.id = s_id
        self.name = name


class Gear:
    def __init__(self, g_id, center_id, gear_type):
        self.id = g_id
        self.center_id = center_id
        self.g_type = gear_type


class GearExcel(Gear):
    def __init__(self, g_id, center_id, g_type, producer, model, size):
        Gear.__init__(self, g_id, center_id, g_type)
        self.producer = producer
        self.model = model
        self.size = size


class Service:
    def __init__(self, s_id, gear_id, service_date, planned_date, return_date):
        self.id = s_id
        self.gear_id = gear_id
        self.start_date = service_date
        self.planned_date = planned_date
        self.return_date = return_date


class LeasedGear:
    def __init__(self, l_id, gear_id, client_id, lease_date, planned_date, return_date):
        self.id = l_id
        self.gear_id = gear_id
        self.client_id = client_id
        self.lease_date = lease_date
        self.planned_date = planned_date
        self.return_date = return_date


class Client:
    def __init__(self, c_id, name, last_name, phone_number):
        self.id = c_id
        self.name = name
        self.last_name = last_name
        self.phone_number = phone_number


def rand_g_type():
    return random.choice(["snowboard", "narty", "kijki", "kask"])


def rand_prod():
    return random.choice([
        "Alpine", "Summit", "Polar", "Glacier", "Snow", "Ice", "Mountain", "Frost",
        "Avalanche", "Blizzard", "Winter", "Chill", "Crystal", "Peak", "Storm",
        "Ski", "Frozen", "Ridge", "Slide", "Rider", "Rush", "Flex", "Edge", "Craft",
        "Blade", "Core", "Quest", "Glide", "Force", "Horizon", "Fire", "Surge"
    ])


def rand_size(g_type: str):
    if g_type == "snowboard":
        return random.randint(50, 100)
    elif g_type == "narty":
        return random.randint(60, 130)
    elif g_type == "kijki":
        return random.randint(50, 110)
    else:
        return random.randint(10, 30)


def rand_price(g_type: str):
    if g_type == "snowboard":
        return random.randint(100, 200)
    elif g_type == "narty":
        return random.randint(100, 150)
    elif g_type == "kijki":
        return random.randint(30, 90)
    else:
        return random.randint(20, 50)


def export_to_csv(file_name, header, data):
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data)


def save_to_csv(file_name, data):
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)


def gen_id(length):
    characters = string.digits + string.ascii_uppercase

    return ''.join(random.choices(characters, k=length))


def gen_uniq_id(ids: list):
    u_id = None

    while u_id is None or u_id in ids:
        u_id = gen_id(9)

    ids.append(u_id)
    return u_id


def check_for_date_conflict(start_date, end_date, gear_id, g_dict) -> bool:
    if gear_id in g_dict:
        for dates in g_dict[gear_id]:
            if end_date < dates[0]:
                break
            if not (dates[0] > end_date or dates[1] < start_date):
                return True

    return False


def gen_clients(uids: list, idx: int, ids: list, n: int) -> [Client]:
    fake = faker.Faker("pl_PL")
    client_list = []

    for i in range(n):
        ids.append(uids[idx + i])
        client_list.append(Client(uids[idx + i], fake.first_name(), fake.last_name(), fake.bothify('###-###-###')))
    return client_list


def gen_ski_centers(ids: list, n: int) -> [SkiCenter]:
    fake = faker.Faker("pl_PL")
    centers = []
    for _ in range(n):
        centers.append(SkiCenter(gen_uniq_id(ids), fake.company()))
    return centers


def gen_random_idx(idx_list: [int], count: int) -> int:
    if len(idx_list) > 0:
        tmp = random.choice(idx_list)
        idx_list.remove(tmp)
        return tmp
    else:
        return random.randint(0, count)


def gen_gear(uids: list, idx: int, centers: [SkiCenter], ids: list, n: int):
    fake = faker.Faker("pl_PL")
    gear_list, gear_ex_list = [], []
    center_count = len(centers)
    center_ids = list(range(center_count))

    for i in range(n):
        ski_idx = gen_random_idx(center_ids, center_count - 1)
        ids.append(uids[idx + i])
        gear_type = rand_g_type()

        gear_list.append(Gear(uids[idx + i], centers[ski_idx].id, gear_type))
        gear_ex_list.append(GearExcel(uids[idx + i], centers[ski_idx].id, gear_type, rand_prod(), fake.vin(),
                                      rand_size(gear_type)))
    return gear_list, gear_ex_list


def save_leased_gear(l_list: [LeasedGear], suffix: str):
    save_to_csv('leasedGear' + suffix + '.csv',
                [[g.id, g.gear_id, g.client_id, g.lease_date, g.planned_date, g.return_date] for g in l_list])


def save_service(service_list: [Service], suffix: str):
    save_to_csv('service' + suffix + '.csv',
                [[service.id, service.gear_id, service.start_date, service.planned_date, service.return_date]
                 for service in service_list])


def gen_leased_gear(ids: list, idx: int, n: int, g_list: list, c_list: list,
                    start_date, end_date, p_dict, g_dict, n_dict):
    lease_list = []
    fake = faker.Faker("pl_PL")
    for a in range(n):
        g_id = None
        conflict = True
        lease_date, planned_date, ret_date = None, None, None

        if a % 10000 == 0:
            print("another 10000, currently: " + str(a))

        while conflict:
            g_id = random.choice(g_list)
            lease_date = fake.date_between(start_date=start_date, end_date=end_date)
            planned_date = lease_date + datetime.timedelta(days=random.randint(0, 4))
            ret_date = planned_date + datetime.timedelta(days=random.randint(0, 3))
            conflict = check_for_date_conflict(lease_date, ret_date, g_id, g_dict)

            if not conflict:
                conflict = check_for_date_conflict(lease_date, ret_date, g_id, p_dict)
                if not conflict:
                    conflict = check_for_date_conflict(lease_date, ret_date, g_id, n_dict)

        if g_id in g_dict:
            g_dict[g_id].append([lease_date, ret_date])
        else:
            g_dict[g_id] = [[lease_date, ret_date]]

        lease_list.append(LeasedGear(ids[idx + a], g_id, random.choice(c_list), lease_date,  planned_date, ret_date))

    return lease_list


def gen_services(ids: list, idx: int, n: int, g_list: list, start_date, end_date, p_dict, g_dict, n_dict):
    service_list = []
    fake = faker.Faker("pl_PL")
    for a in range(n):
        g_id = None
        conflict = True
        service_date, planned_date, return_date = None, None, None

        if a % 10000 == 0:
            print("another 10000, currently: " + str(a))

        while conflict:
            g_id = random.choice(g_list)
            service_date = fake.date_between(start_date=start_date, end_date=end_date)
            planned_date = service_date + datetime.timedelta(days=random.randint(0, 7))
            return_date = planned_date + datetime.timedelta(days=random.randint(0, 3))
            conflict = check_for_date_conflict(service_date, return_date, g_id, g_dict)
            if not conflict:
                conflict = check_for_date_conflict(service_date, return_date, g_id, p_dict)
                if not conflict:
                    conflict = check_for_date_conflict(service_date, return_date, g_id, n_dict)

        if g_id in g_dict:
            g_dict[g_id].append([service_date, return_date])
        else:
            g_dict[g_id] = [[service_date, return_date]]

        service_list.append(Service(ids[idx + a], g_id, service_date, planned_date, return_date))

    return service_list


def export_services(service_list: [Service], suffix: str):
    export_to_csv('service' + suffix + '.csv', ['id', 'gear_id', 'service_date', 'planned_date', 'return_date'],
                  [[service.id, service.gear_id, service.start_date, service.planned_date, service.return_date]
                   for service in service_list])


def export_clients(client_list: [Client], suffix: str):
    export_to_csv('clients' + suffix + '.csv', ['id', 'name', 'last_name', 'phone_number'],
                  [[client.id, client.name, client.last_name, client.phone_number] for client in client_list])


def export_gear(g_list: [Gear], g_ex_list: [GearExcel], suffix: str):
    export_to_csv('gear' + suffix + '.csv', ['id', 'center_id'], [[g.id, g.center_id] for g in g_list])

    export_to_csv('gearExcel' + suffix + '.csv', ['id', 'center_id', 'gear_type', 'producer', 'model', 'size'],
                  [[g.id, g.center_id, g.g_type, g.producer, g.model, g.size] for g in g_ex_list])


def export_centers(center_list: [SkiCenter], suffix: str):
    export_to_csv('ski_center' + suffix + '.csv', ['id', 'name'],
                  [[ski_center.id, ski_center.name] for ski_center in center_list])


def export_leased_gear(l_list: [LeasedGear], suffix: str):
    export_to_csv('leasedGear' + suffix + '.csv',
                  ['id', 'gear_id', 'client_id', 'lease_date', 'planned_date', 'return_date'],
                  [[g.id, g.gear_id, g.client_id, g.lease_date, g.planned_date, g.return_date] for g in l_list])


def get_unique_sample(src: list, result: list, ids: list, sample_size: int):
    chosen_samples = []
    for _ in range(sample_size):
        chosen = False
        while not chosen:
            sample = random.choice(src)
            if sample not in chosen_samples:
                ids.append(sample.id)
                chosen_samples.append(sample)
                result.append(sample)
                chosen = True
    return chosen_samples


def gen_id_set(ids: list, count: int):
    for _ in range(count):
        gen_uniq_id(ids)


def modify_and_add_clients(new_clients, old_clients):
    fake = faker.Faker("pl_PL")
    for c in old_clients:
        c.last_name = fake.last_name()

    return new_clients + old_clients


def add_old_gear(new_gear, old_gear, new_gear_excel, old_gear_excel, ng_ids, og_ids, count):
    for i in range(count):
        if og_ids[i] in ng_ids:
            new_gear_excel.append(old_gear_excel[i])
            new_gear.append(old_gear[i])

    return new_gear, new_gear_excel


def gen_dimensions(c_count1, c_count2, g_count1, g_count2, center_count, c_sample_size, g_sample_size):
    gc_t1, gg_t1, gc_t2, gg_t2, ski_ids = [], [], [], [], []
    c_count2_diff = c_count2 - c_sample_size
    g_count2_diff = g_count2 - g_sample_size
    ski_centers = gen_ski_centers(ski_ids, center_count)
    print("centers t1 generated")
    with Manager() as manager:
        g_ids, c_ids = manager.list(), manager.list()
        mc_t1, mg_t1, mc_t2, mg_t2 = manager.list(), manager.list(), manager.list(), manager.list()
        with ProcessPoolExecutor() as executor:
            p1 = executor.submit(gen_fact_ids, g_ids, g_count1 + g_count2)
            p2 = executor.submit(gen_fact_ids, c_ids, c_count1 + c_count2)

            p1.result()
            p2.result()
            print("Dimension ids generated")

            p1 = executor.submit(gen_clients, c_ids, 0, mc_t1, c_count1)
            p2 = executor.submit(gen_clients, c_ids, c_count1, mc_t2, c_count2_diff)
            p3 = executor.submit(gen_gear, g_ids, 0, ski_centers, mg_t1, g_count1)
            p4 = executor.submit(gen_gear, g_ids, g_count1, ski_centers, mg_t2, g_count2_diff)

            clients_t1 = p1.result()
            clients_t2 = p2.result()
            gear_t1, gear_excel_t1 = p3.result()
            gear_t2, gear_excel_t2 = p4.result()
            print("Clients and gear generated for T1 and T2")
            p1 = executor.submit(get_unique_sample, clients_t1, clients_t2, mc_t2, c_sample_size)
            p2 = executor.submit(get_unique_sample, gear_t1, gear_t2, mg_t2, g_sample_size)

            old_clients = p1.result()
            p2.result()

            p1 = executor.submit(add_old_gear, gear_t2, gear_t1, gear_excel_t2, gear_excel_t1, mg_t2, mg_t1, g_count1)
            p2 = executor.submit(modify_and_add_clients, clients_t2, old_clients)
            clients_t2 = p2.result()
            gear_t2, gear_excel_t2 = p1.result()

            gc_t1, gg_t1, gc_t2, gg_t2, = list(mc_t1), list(mg_t1), list(mc_t2), list(mg_t2)
            print("Some clients and gear moved from T1 to T2")
            print("Gear excel t1 moved to gear excel t2")

    export_clients(clients_t1, 'T1')
    export_clients(clients_t2, 'T2')
    export_centers(ski_centers, 'T1')
    export_centers(ski_centers, 'T2')
    export_gear(gear_t1, gear_excel_t1, 'T1')
    export_gear(gear_t2, gear_excel_t2, 'T2')
    print("dimension exports done")
    return gc_t1, gg_t1, gc_t2, gg_t2


def gen_time_periods(start_date, count, span):
    periods = [[start_date, start_date + datetime.timedelta(days=span)]]

    for i in range(count):
        next_start = periods[i][1] + datetime.timedelta(days=1)
        next_end = next_start + datetime.timedelta(days=span)
        periods.append([next_start, next_end])

    return periods


def parallel_facts_gen(l_ids, s_ids, start_idx, c_per_p, gear, clients, period, dicts, idx_list, suffix):
    with ProcessPoolExecutor() as executor:
        l_results = list(
            executor.map(lambda x: gen_leased_gear(l_ids, c_per_p * x + start_idx, c_per_p, gear, clients,
                                                   period[x][0], period[x][1], dicts[x], dicts[x + 1],
                                                   dicts[x + 2]
                                                   ),
                         idx_list
                         ))

        s_results = list(
            executor.map(lambda x: gen_services(s_ids, c_per_p * x + start_idx, c_per_p, gear,
                                                period[x][0], period[x][1], dicts[x], dicts[x + 1],
                                                dicts[x + 2]
                                                ),
                         idx_list
                         ))

        save_leased_gear(l_results, suffix)
        save_service(s_results, suffix)


def gen_fact_ids(ids, count):
    tmp = list(range(1, count + 1))
    random.shuffle(tmp)
    ids.extend(tmp)


def gen_facts(period1: list, period2: list, c_per_p1: int, c_per_p2: int,
              gear_t1, gear_t2, clients_t1, clients_t2):

    period1_count = len(period1)
    period2_count = len(period2)
    fact_count1 = c_per_p1 * period1_count
    fact_count2 = c_per_p2 * period2_count
    even_idx = [i for i in range(period1_count) if i % 2 == 0]
    odd_idx = [i for i in range(period1_count) if i % 2 != 0]
    even_idx2 = [i for i in range(period2_count) if i % 2 == 0]
    odd_idx2 = [i for i in range(period2_count) if i % 2 != 0]

    with Manager() as manager:
        dicts = [manager.dict() for _ in range(period1_count + 2)]
        dicts2 = [manager.dict() for _ in range(period2_count + 2)]
        l_ids, s_ids = manager.list(), manager.list()

        with ProcessPoolExecutor() as executor:
            future1 = executor.submit(gen_fact_ids, l_ids, fact_count1 + fact_count2)
            future2 = executor.submit(gen_fact_ids, s_ids, fact_count1 + fact_count2)

            future1.result()
            future2.result()
            print("Fact id generated")
            l_results, s_results = [], []

            for x in even_idx:
                l_results.append(executor.submit(gen_leased_gear, l_ids, c_per_p1 * x, c_per_p1, gear_t1, clients_t1,
                                                 period1[x][0], period1[x][1], dicts[x],
                                                 dicts[x + 1], dicts[x + 2]))
            for result in l_results:
                save_leased_gear(result, 'T1')
            for x in even_idx:
                s_results.append(executor.submit(gen_services, s_ids, c_per_p1 * x, c_per_p1, gear_t1, period1[x][0],
                                                 period1[x][1], dicts[x], dicts[x + 1], dicts[x + 2]))
            for result in s_results:
                save_service(result, 'T1')
            l_results, s_results = [], []
            print("T1 around half finished")

            for x in odd_idx:
                l_results.append(executor.submit(gen_leased_gear, l_ids, c_per_p1 * x, c_per_p1, gear_t1, clients_t1,
                                                 period1[x][0], period1[x][1], dicts[x],
                                                 dicts[x + 1], dicts[x + 2]))
            for result in l_results:
                save_leased_gear(result, 'T1')
            for x in odd_idx:
                s_results.append(executor.submit(gen_services, s_ids, c_per_p1 * x, c_per_p1, gear_t1, period1[x][0],
                                                 period1[x][1], dicts[x], dicts[x + 1], dicts[x + 2]))
            for result in s_results:
                save_service(result, 'T1')
            l_results, s_results = [], []
            print("T1 finished")

            for x in even_idx2:
                l_results.append(executor.submit(gen_leased_gear, l_ids, c_per_p2 * x + fact_count1, c_per_p2, gear_t2,
                                                 clients_t2, period2[x][0], period2[x][1], dicts2[x], dicts2[x + 1],
                                                 dicts2[x + 2]))
            for result in l_results:
                save_leased_gear(result, 'T2')
            for x in even_idx2:
                s_results.append(executor.submit(gen_services, s_ids, c_per_p2 * x + fact_count1, c_per_p2, gear_t2,
                                                 period2[x][0], period2[x][1], dicts2[x], dicts2[x + 1], dicts2[x + 2]))
            for result in s_results:
                save_service(result, 'T2')
            l_results, s_results = [], []
            print("T2 around half finished")

            for x in odd_idx2:
                l_results.append(executor.submit(gen_leased_gear, l_ids, c_per_p2 * x + fact_count1, c_per_p2, gear_t2,
                                                 clients_t2, period2[x][0], period2[x][1], dicts2[x], dicts2[x + 1],
                                                 dicts2[x + 2]))
            for result in l_results:
                save_leased_gear(result, 'T2')
            for x in odd_idx2:
                s_results.append(executor.submit(gen_services, s_ids, c_per_p2 * x + fact_count1, c_per_p2, gear_t2,
                                                 period2[x][0], period2[x][1], dicts2[x], dicts2[x + 1], dicts2[x + 2]))
            for result in s_results:
                save_service(result, 'T2')
            print("T2 finished")


if __name__ == '__main__':
    export_leased_gear([], 'T1')
    export_services([], 'T1')
    export_leased_gear([], 'T2')
    export_services([], 'T2')

    time_periods = gen_time_periods(datetime.datetime(2023, 1, 1), 9, 30)
    init_date2 = time_periods[9][1] + datetime.timedelta(days=1)
    time_periods2 = gen_time_periods(init_date2, 1, 30)

    c_t1, g_t1, c_t2, g_t2 = gen_dimensions(50000, 5000, 100000, 10000, 1000, 2000, 5000)

    gen_facts(time_periods, time_periods2, 100000, 10000, g_t1, g_t2, c_t1, c_t2)
