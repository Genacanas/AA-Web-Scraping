import requests

def test_socks5_proxy():
    proxy = {
        "http": "socks5://GenaroCanas:Genaro4937@socks5.windscribe.com:1080",
        "https": "socks5://GenaroCanas:Genaro4937@socks5.windscribe.com:1080",
    }
    url = "https://httpbin.org/ip"

    try:
        response = requests.get(url, proxies=proxy, timeout=10)
        print(f"IP detectada: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar: {e}")

if __name__ == "__main__":
    test_socks5_proxy()
