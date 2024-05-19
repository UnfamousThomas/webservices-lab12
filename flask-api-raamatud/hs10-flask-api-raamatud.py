import json
import os

import requests
from azure.storage.blob import BlobServiceClient
from flask import Flask
from flask import request
from flask_cors import CORS


def blob_konteineri_loomine(konteineri_nimi):
    container_client = blob_service_client.get_container_client(container=konteineri_nimi)
    if not container_client.exists():
        blob_service_client.create_container(konteineri_nimi)


def blob_raamatute_nimekiri():
    container_client = blob_service_client.get_container_client(container=blob_container_name)
    raamatud = []
    for el in container_client.list_blobs():
        raamatud.append(el.name)
    return raamatud


def blob_alla_laadimine(faili_nimi):
    blob_client = blob_service_client.get_blob_client(container=blob_container_name, blob=faili_nimi)
    return blob_client.download_blob().content_as_text()


def blob_ules_laadimine(faili_nimi, sisu):
    blob_client = blob_service_client.get_blob_client(container=blob_container_name, blob=faili_nimi)
    blob_client.upload_blob(sisu)


def blob_kustutamine(faili_nimi):
    blob_client = blob_service_client.get_blob_client(container=blob_container_name, blob=faili_nimi)
    blob_client.delete_blob()


app = Flask(__name__)
cors = CORS(app, resources={r"/raamatud/*": {"origins": "*"}, r"/raamatu_otsing/*": {"origins": "*"}})


@app.route('/raamatud/', methods=['POST'])
def raamatu_lisamine():
    input = json.loads(request.data)
    book_id = input['raamatu_id']
    try:
        lae_ules_raamat(book_id)
        return ({"tulemus": "Raamatu loomine onnestus",
                 "raamatu_id": book_id}, 201)
    except:
        return {}, 404


def count_word_occurrences(text, word):
    count = 0
    words = text.split()
    for w in words:
        if w == word:
            count += 1
    return count


def lae_ules_raamat(gutenberg_id):
    address = "https://www.gutenberg.org/cache/epub/" + str(gutenberg_id) + "/pg" + str(gutenberg_id) + ".txt"
    response = requests.get(address)
    sisu = response.text
    blob_ules_laadimine(gutenberg_id, sisu)


@app.route('/raamatud/<book_id>', methods=['DELETE'])
def raamatu_kustutamine(book_id):
    try:
        blob_kustutamine(book_id)
        return {}, 204
    except:
        return {}, 404


@app.route('/raamatud/<book_id>', methods=['GET'])
def raamatu_allatombamine(book_id):
    if not book_id.isnumeric():
        return ({}, 404)
    try:
        book = blob_alla_laadimine(book_id)
        return (book, 200, {'Content-Type': 'text/plain; charset=utf-8'})
    except:
        return ({}, 404)


@app.route('/raamatud/', methods=['GET'])
def raamatu_nimekiri():
    blob_nimekiri = blob_raamatute_nimekiri()

    return ({
                "raamatud": blob_nimekiri
            }, 200)


blob_connection_string = os.getenv('APPSETTING_AzureWebJobsStorage')
blob_service_client = BlobServiceClient.from_connection_string(blob_connection_string)
blob_container_name = os.getenv("APPSETTING_blob_container_name")
blob_konteineri_loogitmine(blob_container_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
