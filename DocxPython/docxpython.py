from docx import Document

def fill_word_template(data: dict, template_path: str, output_path: str):
    
    doc = Document(template_path)

    for paragraph in doc.paragraphs:
        text = paragraph.text
        for key, value in data.items():
            if isinstance(value, list):
                continue  # ignorar lista de itens neste exemplo
            placeholder = f"{{{key}}}"
            if placeholder in text:
                paragraph.text = text.replace(placeholder, str(value))

    doc.save(output_path)
