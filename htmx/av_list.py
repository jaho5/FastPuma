from htmx.util import get_line_in_double_brackets

content=''
with open('./htmx/av-list.html', 'r') as f:
  content = f.read()

def get_av_html(user_list):
  html = ''
  av_line = get_line_in_double_brackets(content)
  av_list = ''
  for user in user_list:
    user_av_line = av_line.replace('{{user_id}}', str(user['user_id']))
    user_av_line = user_av_line.replace('{{display_name}}', str(user['display_name']))
    if 'is_saved' in user and user['is_saved']:
      user_av_line = user_av_line.replace('{{class}}', 'is_saved')
    av_list+=user_av_line
  html = content.replace('[['+av_line+']]', av_list)
  return html
