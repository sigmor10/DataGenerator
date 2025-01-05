import bisect
import random
import csv
import faker
import datetime
import chardet


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


def gen_uniq_id(fake_gen, ids: list):
    u_id = None

    while u_id is None or u_id in ids:
        u_id = fake_gen.bothify('######')

    ids.append(u_id)
    return u_id


def check_for_date_conflict(start_date, end_date, gear_id, g_dict) -> bool:
    length = len(g_dict[gear_id])
    date_ranges = g_dict[gear_id]
    start_dates = [dates[0] for dates in date_ranges]
    idx = bisect.bisect_left(start_dates, start_date)
    if idx > 0:
        idx = idx - 1

    for j in  range(idx, length):
        dates = date_ranges[j]
        if end_date < dates[0]:
            break
        if not (dates[0] > end_date or dates[1] < start_date):
            return True

    bisect.insort(g_dict[gear_id], (start_date, end_date))

    return False


def gen_clients(fake_gen, uids: list, ids: list, n: int) -> [Client]:
    client_list = []

    for _ in range(n):
        uid = gen_uniq_id(fake_gen, uids)
        ids.append(uid)
        client_list.append(Client(uid, fake_gen.first_name(), fake_gen.last_name(),
                                  fake_gen.bothify('###-###-###')))
    return client_list


def gen_ski_centers(fake_gen, ids: list, n: int) -> [SkiCenter]:
    centers = []
    for _ in range(n):
        centers.append(SkiCenter(gen_uniq_id(fake_gen, ids), fake_gen.company()))
    return centers


def gen_random_idx(idx_list: [int], count: int) -> int:
    if len(idx_list) > 0:
        tmp = random.choice(idx_list)
        idx_list.remove(tmp)
        return tmp
    else:
        return random.randint(0, count)


def gen_gear(fake_gen, uids: list, n: int, centers: [SkiCenter], ids: list):
    gear_list, gear_ex_list = [], []
    center_count = len(centers)
    center_ids = list(range(center_count))
    for _ in range(n):
        ski_idx = gen_random_idx(center_ids, center_count - 1)
        gear_id = gen_uniq_id(fake_gen, uids)
        ids.append(gear_id)
        gear_type = rand_g_type()

        gear_list.append(Gear(gear_id, centers[ski_idx].id, gear_type))
        gear_ex_list.append(GearExcel(gear_id, centers[ski_idx].id, gear_type, rand_prod(), fake_gen.vin(),
                                      rand_size(gear_type)))
    return gear_list, gear_ex_list


def gen_leased_gear(fake_gen, ids: list, n: int, g_list: list, c_list: list,
                    start_date, end_date, g_dict) -> [LeasedGear]:
    lease_list = []
    client_count, gear_count = len(c_list), len(g_list)
    client_ids, gear_ids = list(range(client_count)), list(range(gear_count))
    for a in range(n):
        g_idx = None
        conflict = True
        lease_date, planned_date, ret_date = None, None, None

        if a % 10000 == 0:
            print("another 1000, currently: " + str(a))

        while conflict:
            g_idx = gen_random_idx(gear_ids, gear_count - 1)
            lease_date = fake_gen.date_between(start_date=start_date, end_date=end_date)
            planned_date = lease_date + datetime.timedelta(days=random.randint(0, 7))
            ret_date = planned_date + datetime.timedelta(days=random.randint(0, 3))
            conflict = check_for_date_conflict(lease_date, ret_date, g_list[g_idx], g_dict)

        lease_list.append(LeasedGear(gen_uniq_id(fake_gen, ids), g_list[g_idx], random.choice(c_list), lease_date,
                                     planned_date, ret_date))
    return lease_list


def gen_services(fake_gen, ids: list, n: int, g_list: list, start_date, end_date, g_dict) -> [Service]:
    service_list = []
    for a in range(n):
        g_idx = None
        conflict = True
        service_date, planned_date, return_date = None, None, None

        if a % 10000 == 0:
            print("another 1000, currently: " + str(a))

        while conflict:
            g_idx = random.randint(0, len(g_list) - 1)
            service_date = fake_gen.date_between(start_date=start_date, end_date=end_date)
            planned_date = service_date + datetime.timedelta(days=random.randint(0, 15))
            return_date = planned_date + datetime.timedelta(days=random.randint(0, 5))

            conflict = check_for_date_conflict(service_date, return_date, g_list[g_idx], g_dict)

        service_list.append(Service(gen_uniq_id(fake_gen, ids), g_list[g_idx], service_date, planned_date,
                                    return_date))
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


if __name__ == '__main__':
    fake = faker.Faker("pl_PL")
    t1_start_date = datetime.datetime(2023, 1, 1)
    t1_end_date = datetime.datetime(2023, 12, 31)
    t2_start_date = datetime.datetime(2024, 1, 1)
    t2_end_date = datetime.datetime(2024, 12, 31)

    g_ids, c_ids, lg_ids, ski_ids, serv_ids = [], [], [], [], []
    # ^ lists of used ids for gear, clients, leases, ski centers, services ^
    c_t1, g_t1, c_t2, g_t2 = [], [], [], []

#   Set T1
    clients = gen_clients(fake, c_ids, c_t1, 50000)
    print("clients t1 generated")
    clients_t2 = gen_clients(fake, c_ids, c_t2, 20000)
    print("clients t2 generated")
    old_clients = get_unique_sample(clients, clients_t2, c_t2, 30000)
    print("clients t1 moved to clients t2")
    for c in old_clients:
        c.last_name = fake.last_name()
    export_clients(clients, 'T1')
    export_clients(clients_t2, 'T2')
    clients, clients_t2, old_clients, c_ids = [], [], [], []

    ski_centers = gen_ski_centers(fake, ski_ids, 1000)
    print("centers t1 generated")

    gear, gear_excel = gen_gear(fake, g_ids, 100000, ski_centers, g_t1)
    coll_dict = {g: [] for g in g_t1}
    print("gear t1 generated")
    gear_t2, gear_excel_t2 = gen_gear(fake, g_ids, 50000, ski_centers, g_t2)
    for g in gear_t2:
        coll_dict[g.id] = []
    print("gear t2 generated")
    get_unique_sample(gear, gear_t2, g_t2, 50000)
    print("gear t1 moved to gear t2")
    for i in range(len(gear)):
        if gear[i] in gear_t2:
            gear_excel_t2.append(gear_excel[i])
    print("gear excel t1 moved to gear excel t2")
    export_centers(ski_centers, 'T1')
    export_centers(ski_centers, 'T2')
    export_gear(gear, gear_excel, 'T1')
    export_gear(gear_t2, gear_excel_t2, 'T2')
    print("dimension exports done")
    gear, gear_t2, gear_excel, gear_excel_t2, ski_centers, g_ids, ski_ids = [], [], [], [], [], [], []

    leased_gear = gen_leased_gear(fake, lg_ids, 1000000, g_t1, c_t1, t1_start_date, t1_end_date, coll_dict)
    print("lease facts t1 generated")
    export_leased_gear(leased_gear, 'T1')
    leased_gear.clear()

    services = gen_services(fake, serv_ids, 1000000, g_t1, t1_start_date, t1_end_date, coll_dict)
    print("service facts t1 generated")
    export_services(services, 'T1')
    services.clear()

# Set T2
    leased_gear_t2 = gen_leased_gear(fake, lg_ids, 100000, g_t2, c_t2, t2_start_date, t2_end_date, coll_dict)
    print("lease facts t2 generated")
    export_leased_gear(leased_gear_t2, 'T2')

    services_t2 = gen_services(fake, serv_ids, 100000, g_t2, t2_start_date, t2_end_date, coll_dict)
    print("service facts t2 generated")
    export_services(services_t2, 'T2')

with open('clientsT1.csv', 'rb') as f:
    print(chardet.detect(f.read()))
