# ...existing code...
from DocumentIntelligence.utility import client as project_client, load_file_as_base64 as project_load_file_as_base64

def _get_field_value(field):
    """Retorna valor útil de DocumentField / dict / lista / primitivo."""
    if field is None:
        return ""
    if hasattr(field, "content"):
        return getattr(field, "content") or ""
    if hasattr(field, "value"):
        val = getattr(field, "value")
        if isinstance(val, (str, int, float)):
            return val
        if isinstance(val, list):
            return [_get_field_value(v) for v in val]
        if isinstance(val, dict):
            return val.get("content") or val.get("value") or val
        return str(val)
    if isinstance(field, dict):
        if "valueArray" in field:
            arr = field.get("valueArray") or []
            result = []
            for item in arr:
                if isinstance(item, dict) and "valueObject" in item:
                    obj = item["valueObject"]
                    result.append({k: _get_field_value(v) for k, v in obj.items()})
                else:
                    result.append(_get_field_value(item.get("value") if isinstance(item, dict) else item))
            return result
        if "content" in field:
            return field.get("content")
        if "value" in field:
            return field.get("value")
        return field
    if hasattr(field, "to_dict"):
        try:
            d = field.to_dict()
            return _get_field_value(d)
        except Exception:
            pass
    return str(field)

def _inspect_fields(document):
    """Imprime nomes/infos dos fields para debug."""
    fields = getattr(document, "fields", None)
    if fields is None and isinstance(document, dict):
        fields = document.get("fields", {})
    print("=== INSPEÇÃO DE FIELDS DO DOCUMENTO ===")
    if not fields:
        print("Nenhum field encontrado ou fields vazio.")
        return
    for k, v in fields.items():
        print(f"- Field name: {k}")
        try:
            print(f"  type: {type(v)}")
            if hasattr(v, "content"):
                print(f"  content: {getattr(v, 'content')}")
            if hasattr(v, "value"):
                print(f"  value: {getattr(v, 'value')}")
            if hasattr(v, "value_type"):
                print(f"  value_type: {getattr(v, 'value_type')}")
            if isinstance(v, dict):
                print(f"  dict keys: {list(v.keys())}")
            if hasattr(v, "to_dict"):
                try:
                    print(f"  to_dict(): {v.to_dict()}")
                except Exception:
                    pass
        except Exception as e:
            print(f"  erro ao inspecionar field: {e}")

def client():
    """Wrapper para obter cliente do projeto usado nos testes."""
    return project_client()

def load_file_as_base64(path):
    return project_load_file_as_base64(path)

def extract_invoice_data_teste(file_path: str, model_id: str = "sapiens2015415tcc"):
    """
    Versão de teste que retorna um dicionário utilizando acesso robusto aos fields.
    Também imprime inspeção dos fields para ajudar a identificar nomes/formatos.
    """
    cli = client()
    file_b64 = load_file_as_base64(file_path)
    poller = cli.begin_analyze_document(
        model_id,
        {"base64Source": file_b64},
        locale="pt-BR"
    )
    result = poller.result()
    if not result.documents:
        raise ValueError("Nenhum documento detectado no arquivo.")
    document = result.documents[0]
    _inspect_fields(document)
    fields = getattr(document, "fields", None)
    if fields is None and isinstance(document, dict):
        fields = document.get("fields", {})

    data = {
        "numerodanota": _get_field_value(fields.get("numerodanota")) if fields else "",
        "valornota": _get_field_value(fields.get("valornota")) if fields else "",
        "datadeemissao": _get_field_value(fields.get("datadeemissao")) if fields else "",
        "fornecedor": _get_field_value(fields.get("fornecedor")) if fields else "",
        "mesdopagamento": _get_field_value(fields.get("mesdopagamento")) if fields else "",
        "descricaodoservico": _get_field_value(fields.get("descricaodoservico")) if fields else "",
        "datadevencimento": _get_field_value(fields.get("datadevencimento")) if fields else ""
    }

    # itens (se existir campo de itens no modelo)
    possible_items = None
    if fields:
        for candidate in ("Items", "items", "itens"):
            if candidate in fields:
                possible_items = fields.get(candidate)
                break
    if possible_items:
        items = _get_field_value(possible_items)
        data["Items"] = items if isinstance(items, list) else []

    return data
# ...existing code...