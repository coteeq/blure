from app import blure
from config import host, port, debug

if __name__ == '__main__':
    blure.go_fast(host=host, port=port, debug=debug)
