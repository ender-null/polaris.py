from core.utils import *

commands = [
    ('/issues', []),
    ('/issue', ['title', 'body'])
]
description = 'Creates and lists issues using GitHub API v3.'
hidden = True


def run(m):
    if not is_admin(m.sender.id):
        return send_message(m, 'No, shit isn\'t going that way.')

    url = 'https://api.github.com/repos/luksireiku/polaris/issues'

    if get_command(m) == 'issue':
        input = get_input(m)

        if not input:
            return send_message(m, 'No input')
        title = input.split('\n')[0]
        body = input.split('\n')[1]
        print(title + '/' + body)
        params = {
            'title': title,
            'body': body,
            'access_token': config.keys.github_token
        }
        jstr = requests.post(url, params=params)
        print(jstr.url)

        if jstr.status_code != 200:
            return send_message(m, 'Connection Error!\n' + jstr.text)

        issues = json.loads(jstr.text)[-1]
        if issues['body']:
            message = '#{} *{}*\n_{}_\n\n{}'.format(issues['number'], issues['title'], issues['body'], issues['url'])
        else:
            message = '#{} *{}*\n\n{}'.format(issues['number'], issues['title'], issues['url'])
            
    elif get_command(m) == 'issues':
        jstr = requests.get(url)

        if jstr.status_code != 200:
            return send_message(m, 'Connection Error!\n' + jstr.text)

        issues = json.loads(jstr.text)
        
        message = '*Open Issues:*\n'
        for issue in issues:
            message += '#{} *{}*\n_{}_\n\n'.format(issue['number'], issue['title'], issue['body'])
    
    send_message(m, message, markup='Markdown')
