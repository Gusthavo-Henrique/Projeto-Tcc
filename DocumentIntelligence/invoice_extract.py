import base64
from pathlib import Path
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from DocumentIntelligence.utility import client, load_file_as_base64


def _get_field_value(field):
    """
    Extrai o valor real de um campo retornado pelo Azure Document Intelligence,
    tratando diferentes tipos de objetos (DocumentField, dict, etc.).
    """
    if field is None:
        return ""
    # Se for um objeto com atributo 'content'
    if hasattr(field, "content") and getattr(field, "content"):
        return getattr(field, "content")
    # Se for um objeto com atributo 'value'
    if hasattr(field, "value") and getattr(field, "value"):
        return getattr(field, "value")
    # Se for dicionário
    if isinstance(field, dict):
        return field.get("content") or field.get("value") or ""
    # Caso seja valor simples
    return str(field)


def extract_invoice_data(file_path: str, model_id: str = "sapiens2015415tcc") -> dict:
    """
    Extrai dados de uma nota fiscal de serviço usando o modelo customizado do Azure Document Intelligence.
    Retorna os campos definidos no treinamento do modelo.

    Args:
        file_path (str): Caminho do arquivo PDF.
        model_id (str): ID do modelo customizado no Azure.

    Returns:
        dict: Dados estruturados com os campos personalizados.
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
    fields = document.fields

    # Usa a função segura para pegar o valor de cada campo
    data = {
        "numerodanota": _get_field_value(fields.get("numerodanota")),
        "valordanota": _get_field_value(fields.get("valordanota")),
        "datadeemissao": _get_field_value(fields.get("datadeemissao")),
        "fornecedor": _get_field_value(fields.get("fornecedor")),
        "mesdopagamento": _get_field_value(fields.get("mesdopagamento")),
        "descricaodoservico": _get_field_value(fields.get("descricaodoservico")),
        "datadevencimento": _get_field_value(fields.get("datadevencimento")),
    }

    return data
