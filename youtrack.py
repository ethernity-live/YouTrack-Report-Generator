"""YouTrack JSON REST API Module"""
import requests

class Issues:
    """Access issues at a YouTrack instance"""
    def __init__(self, site_url, auth_token, project=None, batch_len=100):
        #HTTP headers
        self.headers = {
            'Authorization': 'Bearer ' + auth_token,
            'Accept': 'application/json',
        }
        #url setting
        self.url = site_url + '/youtrack/rest/issue/'
        if project:
            self.url += 'byproject/' + project
        #initialize variables
        self.attmap = {}
        self.b_len = batch_len

    def __iter__(self):
        #iterates over issues
        for issue in self.raw_issues():
            cur = {'id': issue['id']}
            #iterates over fields in issue (eg. name, summary, description)
            for field in issue['field']:
                #if field name is attachment, saves attachment in attmap (map of attachments) to download later
                if field['name'] == 'attachments':
                    for att in field['value']:
                        self.attmap[issue['id'], att['value']] = att['url']
                #else if field is summary or description, saves value in list (cur)
                elif field['name'] in ('summary', 'description'):
                    cur[field['name']] = field['value']
            yield cur

    #raw issues in json
    def raw_issues(self):
        start = 0
        while True:
            url = '%s?max=%d&after=%d' % (self.url, self.b_len, start)
            start += self.b_len
            #download all issues
            resp = requests.get(url, headers=self.headers)
            if resp:
                #is there are any issues, work with response in JSON
                batch = resp.json()
                #yields issues one by one
                for i in batch:
                    yield i
                if len(batch) < self.b_len:
                    break
    #download attachment (one per execution)
    def download_attachment(self, att_id):
        #Download an attachment by issue and name
        resp = requests.get(self.attmap[att_id], headers=self.headers)
        #returns attachment if there is any
        return resp.content if resp else None