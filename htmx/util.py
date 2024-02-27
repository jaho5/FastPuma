def get_line_in_double_brackets(text):
  start_index = text.find("[[")  # Find the index of the first occurrence of "[["
  if start_index != -1:
    end_index = text.find("]]", start_index)  # Find the index of the first occurrence of "]]" after start_index
    if end_index != -1:
        return text[start_index + 2:end_index]  # Extract the text between "[[" and "]]"
  return ''  # Return None if no match is found