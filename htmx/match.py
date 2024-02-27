from htmx.util import get_line_in_double_brackets

def match_html(match_list):
  content=''
  with open('./htmx/match.html', 'r') as f:
    content = f.read()

  html = ''
  match_line = get_line_in_double_brackets(content)
  match_list_str = ''
  for match in match_list:
    user_match_line = match_line.replace('{{side_1_user_1_display_name}}', match['side_1_user_1_display_name'])
    user_match_line = user_match_line.replace('{{side_1_user_2_display_name}}', match['side_1_user_2_display_name'])
    user_match_line = user_match_line.replace('{{side_2_user_1_display_name}}', match['side_2_user_1_display_name'])
    user_match_line = user_match_line.replace('{{side_2_user_2_display_name}}', match['side_2_user_2_display_name'])
    user_match_line = user_match_line.replace('{{id}}', str(match['id']))
    match_list_str+=user_match_line
  html=content.replace('[['+match_line+']]', match_list_str)
  return html
