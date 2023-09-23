import json
import time
def find_car_by_id(target_id, file_path="./cars.json"):
    with open(file_path, 'r') as f:
        time.sleep(0.01) # Delay para simular archivo mas grande
        data = json.load(f)

        min, max = 0, len(data) - 1
        while min <= max:
            mid = (min + max) // 2
            if data[mid]['id'] == target_id:
                return data[mid]
            elif data[mid]['id'] < target_id:
                min = mid + 1
            else:
                max = mid - 1
        return None