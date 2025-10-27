import base64
from pathlib import Path
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest 
from DocumentIntelligence.utility import client, load_file_as_base64

#Função que vai ser usada no main.py para extrair os dados das notas fiscais
def extract_invoice_data(file_path: str, model_id: str = "prebuilt-invoice") -> dict:
    """
    Lê uma nota fiscal de serviço usando o Azure Document Intelligence
    e retorna as informações extraídas como um dicionário.

    Args:
        file_path (str): Caminho do arquivo PDF.
        model_id (str): ID do modelo do Azure (padrão: 'prebuilt-invoice').

    Returns:
        dict: Dados estruturados da nota fiscal.
    """
    document_intelligence_client = client()

    file_base64 = load_file_as_base64(file_path)
    poller = document_intelligence_client.begin_analyze_document(
        model_id,
        {"base64Source": file_base64},
        locale="pt-BR"
    )

    result = poller.result()

    if not result.documents:
        raise ValueError("Nenhum documento detectado no arquivo.")

    document = result.documents[0]
    fields = document['fields']

    data = {
        "InvoiceId": fields.get("InvoiceId", {}).get("content", ""),
        "InvoiceTotal": fields.get("InvoiceTotal", {}).get("content", ""),
        "InvoiceDate": fields.get("InvoiceDate", {}).get("content", ""),
        "DueDate": fields.get("DueDate", {}).get("content", ""),
        "Items": []
    }

    # Extrair lista de itens, se existir
    if "Items" in fields:
        for item in fields["Items"]["valueArray"]:
            item_obj = item["valueObject"]
            item_dict = {k: v.get("content", "") for k, v in item_obj.items()}
            data["Items"].append(item_dict)

    return data

