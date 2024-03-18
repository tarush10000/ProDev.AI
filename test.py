def format_text_data(input_text):
    lines = input_text.split('\n')
    formatted_entries = []
    current_entry = []
    
    for line in lines:
        if line.strip():
            if line[0].isdigit():
                if current_entry:
                    formatted_entries.append(' '.join(current_entry))
                    current_entry = []
                current_entry.append(line[1:].strip())
            else:
                current_entry.append(line.strip())
    if current_entry:
        formatted_entries.append(' '.join(current_entry))
    
    return formatted_entries

input_text = """1 abc
def
2 xyz kjcao
ckhsc
coleac
3 pfmcpime
coaecn
cosnvs
"""

print(format_text_data(input_text))
