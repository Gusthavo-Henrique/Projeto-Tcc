# ...existing code...
import sys
import importlib
import inspect
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

print(f"Project root: {project_root}")

tests_dir = Path(__file__).resolve().parent
print(f"Test folder: {tests_dir}\n")

py_files = [p.name for p in tests_dir.glob("*.py") if p.name != "__init__.py"]
print("Arquivos encontrados na pasta de testes:")
for f in py_files:
    print(f" - {f}")
print("")

pdf_path = r"C:\Users\gusth\Downloads\Notas fornecedores\NOTAS FORNECEDOR 1\4756 SESI RO NFE.PDF"
model_id = "sapiens2015415tcc"

try:
    from DocumentIntelligence.invoice_extract import extract_invoice_data
    print("Import: DocumentIntelligence.invoice_extract.extract_invoice_data -> OK")
except Exception as e:
    print(f"Erro ao importar extract_invoice_data: {e}")
    extract_invoice_data = None

test_mod_name = "Testes.DocumentIntelligenceTest.invoice_extract_test"
try:
    test_mod = importlib.import_module(test_mod_name)
    print(f"Import: {test_mod_name} -> OK\n")
except Exception as e:
    print(f"Não foi possível importar {test_mod_name}: {e}\n")
    test_mod = None

if test_mod:
    funcs = [name for name, obj in inspect.getmembers(test_mod, inspect.isfunction)]
    print("Funções disponíveis em invoice_extract_test:")
    for fn in funcs:
        print(f" - {fn}")
    print("")

def run_primary_extraction():
    # Primeiro, tente a função do projeto (com debug se disponível).
    if extract_invoice_data:
        try:
            sig = inspect.signature(extract_invoice_data)
            if "debug" in sig.parameters:
                print("Executando extract_invoice_data(..., debug=True) para inspecionar fields...")
                extract_invoice_data(pdf_path, model_id, debug=True)
                return
            else:
                print("Executando extract_invoice_data(...) sem debug (tentativa padrão)...")
                data = extract_invoice_data(pdf_path, model_id)
                print("Resultado (campos extraídos):")
                for k, v in (data or {}).items():
                    print(f" - {k}: {v}")
                return
        except Exception as e:
            print(f"Erro ao executar extract_invoice_data: {e}")
            # se falhar, tentamos o módulo de testes local (fallback)
    # Fallback para módulo de testes local
    if test_mod and hasattr(test_mod, "extract_invoice_data_teste"):
        try:
            print("Usando fallback: Testes.invoice_extract_test.extract_invoice_data_teste(...)")
            data = test_mod.extract_invoice_data_teste(pdf_path, model_id)
            print("Resultado do módulo de testes:")
            for k, v in (data or {}).items():
                print(f" - {k}: {v}")
        except Exception as e:
            print(f"Erro ao executar extract_invoice_data_teste: {e}")
    else:
        print("Nenhuma função de extração disponível para executar.")

def run_secondary_tests():
    if not test_mod:
        print("Módulo de testes não disponível, pulando testes secundários.")
        return
    if hasattr(test_mod, "extract_invoice_data_teste"):
        try:
            print("Executando extract_invoice_data_teste do módulo de testes...")
            result = test_mod.extract_invoice_data_teste(pdf_path, model_id)
            print("extract_invoice_data_teste retornou:")
            print(result)
        except Exception as e:
            print(f"Erro em extract_invoice_data_teste: {e}")

    if hasattr(test_mod, "_inspect_fields"):
        try:
            print("Tentando usar _inspect_fields via extração do módulo de testes...")
            doc = None
            try:
                doc = test_mod.extract_invoice_data_teste.__wrapped__ if hasattr(test_mod.extract_invoice_data_teste, "__wrapped__") else None
            except Exception:
                doc = None
            # simplesmente extraímos e reusamos os dados já impressos pela função de teste; caso precise de _inspect_fields com objeto raw,
            # podemos chamar _inspect_fields passando o resultado bruto retornado por begin_analyze_document se implementado no módulo de teste.
        except Exception as e:
            print(f"Erro ao executar _inspect_fields: {e}")

    if hasattr(test_mod, "_get_field_value"):
        try:
            print("Função _get_field_value disponível. Exemplo rápido de tipagem:")
            sample = {"content": "exemplo"}
            print(" - _get_field_value({'content': 'exemplo'}) ->", test_mod._get_field_value(sample))
        except Exception as e:
            print(f"Erro ao testar _get_field_value: {e}")

if __name__ == "__main__":
    print("==== INICIANDO TESTES DE INSPEÇÃO DE FIELDS ====\n")
    run_primary_extraction()
    print("\n--- Testes secundários (módulo invoice_extract_test) ---\n")
    run_secondary_tests()
    print("\n==== FIM DOS TESTES ====")
# ...existing code...