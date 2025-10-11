import os
import base64
import requests
from GraphApi.gerar_token import generate_token
from dotenv import load_dotenv

load_dotenv()  # Carrega variáveis do .env automaticamente

#configs
GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0/me/messages"
SAVE_FOLDER = r'C:\Users\gusth\OneDrive\Documentos\Auto-Certificação-nf\Anexos'
FILTER_SENDER = os.getenv("ALLOWED_EMAIL_PROVIDERS").split(',')  # Lista de emails permitidos, separados por vírgula no .env

def download_attachments(): 
    token = generate_token()

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    params = {
        '$top':10, #pega os primeiros 10 emails
        '$select':'subject,from,hasAttachments' #seleciona apenas os campos necessários
    } 

    # Primeiro teste o token com endpoint básico
    test_response = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers)
    if test_response.status_code != 200:
        print(f"❌ Token inválido para /me: {test_response.status_code}")
        print(test_response.text)
        return
    
    print("✅ Token válido para /me, testando /me/messages...")
    
    # Agora tenta o endpoint de emails
    params = {
        '$top': 10,
        '$select': 'subject,from,hasAttachments'
    }
    
    response = requests.get("https://graph.microsoft.com/v1.0/me/messages", headers=headers, params=params)
    if response.status_code != 200:
        print(f"❌ Erro no endpoint de emails: {response.status_code}")
        print(response.text)
        return

    response = requests.get(GRAPH_API_ENDPOINT, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"Erro ao buscar emails: {response.status_code} - {response.text}")
    
    emails = response.json().get('value', [])
    for email in emails:
        sender = email['from']['emailAddress']['address']
        if sender.lower() not in [s.lower() for s in FILTER_SENDER]:
            continue #ignora quem não está na lista de remententes

        if not email.get('hasAttachments', False):
            continue #ignora emails sem anexos

        email_id = email['id']
        print(f'email de {sender} com notas anexadas encontrado: {email["subject"]}')

        attachment_url = f"{GRAPH_API_ENDPOINT}/{email_id}/attachments"
        attachment_response = requests.get(attachment_url, headers=headers)
        attachment_response.raise_for_status()
        attachemnts = attachment_response.json().get('value', [])

        for attachment in attachemnts:
            if attachment['@odata.type'] == '#microsoft.graph.fileAttachment':
                file_name = attachment['name']
                content_bytes = base64.b64decode(attachment['contentBytes'])
                file_path = os.path.join(SAVE_FOLDER, file_name)

                with open(file_path, 'wb') as f:
                    f.write(content_bytes)

                print(f'Anexo {file_name} salvo em {file_path}')


if __name__ == "__main__":
    download_attachments()

                
