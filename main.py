from pathlib import Path
from datetime import datetime
import shutil
from DocumentIntelligence.invoice_extract import extract_invoice_data
from DocxPython.docxpython import fill_word_template
from GraphApi.baixar_anexos import download_attachments

# Baixa os anexos antes de processar
download_attachments()

# Caminhos principais 
attachments_dir = Path(r'C:\Users\gusth\OneDrive\Documentos\Auto-Certificação-nf\Anexos')
output_dir = Path(r'C:\Users\gusth\OneDrive\Documentos\Auto-Certificação-nf\Certificação_Gerada')
template_path = Path(r'C:\Users\gusth\OneDrive\Documentos\Auto-Certificação-nf\DocxPython\template\Certificaçãoteste.docx')
processed_dir = attachments_dir / "processados"

# Cria pasta de saída e de processados se não existirem
output_dir.mkdir(parents=True, exist_ok=True)
processed_dir.mkdir(parents=True, exist_ok=True)

# Cria log
log_path = output_dir / f"log_processamento_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
log = open(log_path, "w", encoding="utf-8")
log.write("=== LOG DE PROCESSAMENTO DE NOTAS ===\n\n")

try:
    for pdf_path in attachments_dir.glob("*.pdf"):
        try:
            print(f"📄 Processando arquivo: {pdf_path.name}")
            log.write(f"Processando: {pdf_path.name}\n")

            # Extrai os dados da nota
            invoice_data = extract_invoice_data(str(pdf_path))

            # Define o nome do arquivo de saída (sem sobrescrever)
            output_name = f"{pdf_path.stem}_preenchido.docx"
            output_path = output_dir / output_name

            # Gera o documento Word preenchido
            fill_word_template(
                data=invoice_data,
                template_path=str(template_path),
                output_path=str(output_path)
            )

            print(f"✅ Documento gerado: {output_name}")
            log.write(f"✅ Sucesso: {output_name}\n\n")

            # Move o PDF processado para a subpasta 'processados'
            dest_path = processed_dir / pdf_path.name
            shutil.move(str(pdf_path), str(dest_path))
            print(f"📦 PDF movido para: {dest_path}")
            log.write(f"📦 PDF movido para: {dest_path}\n")

        except Exception as e:
            print(f"❌ Erro ao processar {pdf_path.name}: {e}")
            log.write(f"❌ Erro em {pdf_path.name}: {e}\n\n")

finally:
    log.close()

print("\n🟢 Processamento concluído! Verifique a pasta de saída e o arquivo de log.")