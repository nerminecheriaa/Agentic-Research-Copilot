import sys
import requests

URL = "http://localhost:8000/chat"

def main():
    question = " ".join(sys.argv[1:]) or "What is corrective RAG?"
    print(f"Question : {question}\n")

    # Envoi standard sans stream=True
    response = requests.post(URL, json={"question": question}, timeout=120)
    
    if response.status_code == 200:
        data = response.json()
        print("=== RÉPONSE FINALE ===")
        print(data["answer"])
        print(f"\nSources : {data['sources']}")
        print(f"Fondée sur le contexte : {data['grounded']}")
        print(f"Retries : {data['retries']}")
    else:
        print(f"[Erreur {response.status_code}] {response.text}")

if __name__ == "__main__":
    main()