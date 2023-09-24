import grpc
import json
import time
import numpy as np
import cache_service_pb2
import cache_service_pb2_grpc
from find_car_by_id import find_car_by_id
from pymemcache.client import base


class CacheClient:
    def __init__(self, host="master", port=50051):
        
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = cache_service_pb2_grpc.CacheServiceStub(self.channel)

    def get(self, key, option, simulated=False): # 1: JSON    2: Cache
        start_time = time.time()  # Inicio del temporizador

        if option == "1": # Buqueda directa al archivo JSON
            value = find_car_by_id(int(key))
            value = str(value)
            if value:
                elapsed_time = time.time() - start_time
                print(f"Time taken: {elapsed_time:.5f} seconds") 
                return [value, 0]
            else:
                elapsed_time = time.time() - start_time  # Calcula el tiempo transcurrido
                print(f"Time taken: {elapsed_time:.5f} seconds")
                print("Key not found.")
                return None
            
        elif option == "2": # Buqueda con Cache
            response = self.stub.Get(cache_service_pb2.Key(key=key))
        
            if response.value:
                elapsed_time = time.time() - start_time  # Calcula el tiempo transcurrido
                print(f"Time taken (cache): {elapsed_time:.5f} seconds")
                return [response.value, 1]
            else:
                # Si no está en el caché, buscar en el JSON
                value = find_car_by_id(int(key))
                
                value = str(value)
                if value:
                    # Agregando la llave-valor al caché
                    self.stub.Put(cache_service_pb2.CacheItem(key=key, value=value))
                    elapsed_time = time.time() - start_time
                    print(f"Time taken: {elapsed_time:.5f} seconds") 
                    return [value, 0]
                else:
                    elapsed_time = time.time() - start_time  # Calcula el tiempo transcurrido
                    print(f"Time taken: {elapsed_time:.5f} seconds")
                    print("Key not found.")
                    return None

            
    def simulate_searches(self, option, n_searches=100):
        keys_to_search = [f"{i}" for i in np.random.randint(1, 101, n_searches)]
        
        # Métricas
        start_time = time.time()
        avoided_json_lookups = 0

        count = 0
        for key in keys_to_search:
            # clear console
            count += 1
            print("\033[H\033[J")
            print(f"Searching : {count}/{n_searches}")
            
            if self.get(key, option)[1] == 1:
                avoided_json_lookups += 1

        elapsed_time = time.time() - start_time
        print(f"Total Time taken: {elapsed_time:.5f} seconds")

        print(f"Number of times JSON lookup was avoided: {avoided_json_lookups}")


# memcached:
class MemClient:
    def __init__(self, host="memcached", port=11211):
        self.mclient = base.Client((host, port))

    def get(self, key):
        start_time = time.time()  # Inicio del temporizador
        response = self.mclient.get(key)

        if response:
            elapsed_time = time.time() - start_time  # Calcula el tiempo transcurrido
            print(f"Time taken (cache): {elapsed_time:.5f} seconds")
            return [response.decode('utf-8'), 1] # el resultado extraido de memcached viene en bytes
        else:
            # Si no está en memcache, buscar en el JSON
            value = find_car_by_id(int(key))
            
            value = str(value)
            if value:
                # Agregando la llave-valor a memcache
                self.mclient.set(key, value)
                elapsed_time = time.time() - start_time
                print(f"Time taken: {elapsed_time:.5f} seconds") 
                return [value, 0]
            else:
                elapsed_time = time.time() - start_time  # Calcula el tiempo transcurrido
                print(f"Time taken: {elapsed_time:.5f} seconds")
                print("Key not found.")
                return None


    def simulate_searches(self, n_searches=100):
        keys_to_search = [f"{i}" for i in np.random.randint(1, 101, n_searches)]
        
        # Métricas
        start_time = time.time()
        avoided_json_lookups = 0

        count = 0
        for key in keys_to_search:
            # clear console
            count += 1
            print("\033[H\033[J")
            print(f"Searching : {count}/{n_searches}")
            
            if self.get(key)[1] == 1:
                avoided_json_lookups += 1

        elapsed_time = time.time() - start_time
        print(f"Total Time taken: {elapsed_time:.5f} seconds")

        print(f"Number of times JSON lookup was avoided: {avoided_json_lookups}")


if __name__ == '__main__':

    while True:
        print("\nChoose an option:")
        print("1. JSON Search")
        print("2. Cache Search")
        print("3. Memcached Search")
        print("4. Exit")
        option = input("Enter your choice: ")

        if option == "1" or option == "2":
            client = CacheClient()

            print("\nChoose an operation:")
            print("1. Get")
            print("2. Simulate Searches")
            print("3. Exit")

            choice = input("Enter your choice: ")

            if choice == "1":
                key = input("Enter key: ")
                value = client.get(key, option)
                if value is not None:
                    print(f"Value: {value[0]}")
            elif choice == "2":
                n_searches = int(input("Enter the number of searches you want to simulate: "))
                client.simulate_searches(option, n_searches)
            elif choice == "3":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Try again.")

        elif option == "3":
            client = MemClient()
            
            print("\nChoose an operation:")
            print("1. Get")
            print("2. Simulate Searches")
            print("3. Exit")

            choice = input("Enter your choice: ")
            if choice == "1":
                key = input("Enter key: ")
                value = client.get(key)
                if value is not None:
                    print(f"Value: {value[0]}")
            elif choice == "2":
                n_searches = int(input("Enter the number of searches you want to simulate: "))
                client.simulate_searches(n_searches)
            elif choice == "3":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Try again.")
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")