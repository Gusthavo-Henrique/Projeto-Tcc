import os
from msal import PublicClientApplication, SerializableTokenCache
from dotenv import load_dotenv

load_dotenv()  # Carrega variáveis do .env automaticamente

# Configurações do Azure
CLIENT_ID = os.getenv("MS_CLIENT_ID")
TENANT_ID = os.getenv("MS_TENANT_ID")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["User.Read", "Mail.ReadWrite"]


# Arquivo de cache
CACHE_FILE = "token_cache.json"

def generate_token():
    # Criar cache persistente do msal
    cache = SerializableTokenCache()
    if os.path.exists(CACHE_FILE):
        cache.deserialize(open(CACHE_FILE, "r").read())

    app = PublicClientApplication(
        client_id=CLIENT_ID,
        authority=AUTHORITY,
        token_cache=cache
    )

    result = None
    accounts = app.get_accounts() # Buscar contas no cache

    if accounts: # Se houver contas com token válido em cache, tentar reutilizar
        print("Token em cache encontrado, tentando reusar...")
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        print(result)

    if not result: #se não houver token válido, iniciar login
        print("Nenhum token válido encontrado, abrindo login interativo...")
        result = app.acquire_token_interactive(scopes=SCOPES)
        print(result)

    # Salvar cache atualizado
    with open(CACHE_FILE, "w") as f:
        f.write(cache.serialize())

    if "access_token" in result:
        print("Token gerado com sucesso!")
        return result["access_token"]
    else:
        raise Exception(f"Falha ao gerar token: {result.get('error_description')}")

if __name__ == "__main__":
    token = generate_token()
    print("Token de acesso:", token) 

# Criar URI de redirecionamento para autorização no app azure
# URI mobile and desktop, utilizar http://localhost

# Web (Redirect URI Web + Secret) → usa ConfidentialClientApplication, ideal pra backends seguros.
# Mobile & Desktop (Redirect URI localhost) → usa PublicClientApplication, ideal pra apps rodando na máquina local (como seu script Python).