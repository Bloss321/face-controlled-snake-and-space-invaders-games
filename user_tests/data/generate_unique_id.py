import uuid


# generates 50 unique Ids
def generate_unique_ids():
    return [str(uuid.uuid4())[:4] for _ in range(50)]


def save_to_file(unique_id_list, file_path):
    with open(file_path, 'w') as file:
        for uid in unique_id_list:
            file.write(f"{uid}\n")


if __name__ == '__main__':
    unique_ids = generate_unique_ids()
    file_path = 'user_tests/data/unused_unique_ids.txt'
    save_to_file(unique_ids, file_path)
    print(unique_ids)
