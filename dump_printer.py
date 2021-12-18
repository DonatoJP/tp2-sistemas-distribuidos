import pickle, base64

def main():
    with open('dumps/pickle_dump.txt', 'r') as file:
        pre_decode = ''
        for line in file:
            pre_decode += line.replace('\n', '')
        decoded = base64.b64decode(pre_decode)
        loaded = pickle.loads(decoded)
        print(loaded)

if __name__ == '__main__':
    main()