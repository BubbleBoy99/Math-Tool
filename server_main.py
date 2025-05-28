from Controller import Controller

def main():
    controller = Controller()
    controller.run_server(host='127.0.0.1', port=12345)

if __name__ == "__main__":
    main() 