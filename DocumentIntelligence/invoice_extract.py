import base64
from pathlib import Path
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest 
from DocumentIntelligence.utility import client, load_file_as_base64

file_dir = Path(r'C:\Users\gusth\OneDrive\Documentos\Projeto Tcc\Anexos')
file_name = 'NF 7836 CONTRATO 005-2023.pdf'

model_id = "prebuilt-invoice"

document_intelligence_client = client()

doc_source = file_dir / file_name

file_base64 = load_file_as_base64(str(doc_source))
poller = document_intelligence_client.begin_analyze_document(
    model_id, 
    {"base64Source": file_base64},
    locale="pt-BR"
)

result = poller.result()
print("Document count:", len(result.documents)) 

for document in result.documents:
    # print('Doc type:', document['docType'])
    # print('Bounding Area:', document['boundingRegions'])
    # print('Confidence:', document['confidence'] * 100.0, '%')
    
    document_fields = document['fields']
    fields = document_fields.keys()
    print(fields)

    for field in fields:
        if field == 'Items':
            items_list = []
            items = document_fields[field]

            for item in items['valueArray']:
                item_fields = item['valueObject']
                item_dict = {}
                for item_field in item_fields.keys():
                    value = item_fields[item_field].get('content', '')
                    item_dict[item_field] = value
                items_list.append(item_dict)
            print(items_list)
            print('---')
            continue
        value = document_fields[field].get('content', '')
        print(f'{field} : {value}')
        print('---------------')
        valor_nota = document_fields.get('InvoiceTotal', {}).get('content', '0').replace('.', '').replace(',', '.')
        data_emissao_nota = document_fields.get('InvoiceDate', {}).get('content', '')
        data_vencimento_nota = document_fields.get('DueDate', {}).get('content', '')
        numero_nota = document_fields.get('InvoiceId', {}).get('content', '')

        print(f'Valor nota: {valor_nota}')
        print(f'Data emissao nota: {data_emissao_nota}')
        print(f'Data vencimento nota: {data_vencimento_nota}')
        print(f'Numero nota: {numero_nota}')


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

