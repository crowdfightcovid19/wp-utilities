import requests
import json


def preReserveDOI():
    # preReserveDOI return a unpublished concetDOI and a version DOI 

    # Production comment this 4 lines
    ACCESS_TOKEN = 'USEYOURTOKEN'
    params = {'access_token': ACCESS_TOKEN, 'prereserve_doi': 'true'}
    headers = {"Content-Type": "application/json"}
    url = 'https://sandbox.zenodo.org/api/deposit/depositions'

    # Production uncomment this 4 lines
    # ACCESS_TOKEN = 'USEYOURTOKEN'
    # params = {'access_token': ACCESS_TOKEN, 'prereserve_doi': 'true'}
    # headers = {"Content-Type": "application/json"}
    # url = 'https://zenodo.org/api/deposit/depositions'

    r = requests.post(url,
                      params=params,
                      json={},
                      headers=headers)

    data = r.json()
    v_doi = data['metadata']['prereserve_doi']['doi']
    c_doi = v_doi.rsplit('.', 1)[0] + '.' + str(data['conceptrecid'])
    links = data["links"]

    return c_doi, v_doi, links


def publish(document_path, filename, links, metadata):
    # metadata example:
    # {'metadata': {'title': 'My first upload',
    #                      'upload_type': 'poster',
    #                      'description': 'This is my first upload',
    #                      'creators': [{'name': 'Doe, John',
    #                                   'affiliation': 'Zenodo'}]}}
    # Publish the document
    bucket_url = links['bucket']
    ACCESS_TOKEN = 'USEYOURTOKEN'
    params = {'access_token': ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    with open(document_path, "rb") as fp:
        r = requests.put(
            "%s/%s" % (bucket_url, filename),
            data=fp,
            # No headers included in the request, since it's a raw byte request
            params=params,
        )
        print(r.status_code)

    r = requests.put(links['self'],
                     params={'access_token': ACCESS_TOKEN}, data=json.dumps(metadata), headers=headers)
    print(r.status_code)

    r = requests.post(links['publish'],
                      params={'access_token': ACCESS_TOKEN})
    print(r.status_code)
    print(links['html'])


if __name__ == '__main__':
    c_doi, v_doi, links = preReserveDOI()
    metatdata = {'metadata': {'title': 'My first upload',
                              'upload_type': 'poster',
                              'description': 'This is my first upload',
                              'creators': [{'name': 'Doe, John',
                                            'affiliation': 'Zenodo'}]}}

    publish('xxx_report.pdf', 'xxx_report.pdf', links, metatdata)