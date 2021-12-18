import pickle, base64

def main():
    with open('dumps/pickle_dump.txt', 'r') as file:
        line = file.readline()
        decoded = base64.b64decode(line)
        loaded = pickle.loads(decoded)
        print(loaded)

if __name__ == '__main__':
    main()