import json
import os

from azure.storage.blob import BlobServiceClient
from flask import Flask
from flask import request
from flask_cors import CORS

def blob_konteineri_loomine(konteineri_nimi):
    container_client = blob_service_client.get_container_client(container=konteineri_nimi)
    if not container_client.exists():
        blob_service_client.create_container(konteineri_nimi)


def blob_alla_laadimine(faili_nimi):
    blob_client = blob_service_client.get_blob_client(container=blob_container_name, blob=faili_nimi)
    return blob_client.download_blob().content_as_text()


app = Flask(__name__)
cors = CORS(app, resources={r"/raamatud/*": {"origins": "*"}, r"/raamatu_otsing/*": {"origins": "*"}})


@app.route('/raamatu_otsing/<book_id>', methods=['POST'])
def raamatust_sone_otsimine(book_id):
    input = json.loads(request.data)
    sone = input['sone']
    try:
        input = blob_alla_laadimine(book_id)
        hulk = count_word_occurrences(input, sone)
        return ({"raamatu_id": book_id,
                 "sone": sone,
                 "leitud": hulk}, 201)
    except:
        return {}, 404


@app.route('/raamatu_otsing/', methods=['POST'])
def raamatu_otsing():
    input = json.loads(request.data)
    sone = input['sone']
    container_client = blob_service_client.get_container_client(container=blob_container_name)
    raamatud = []
    for el in container_client.list_blobs():
        raamatud.append({
            "raamatu_id": el.name,
            "leitud": count_word_occurrences(blob_alla_laadimine(el), sone)
        })

    return ({
        "sone": sone,
        "tulemused": raamatud,
    })


def count_word_occurrences(text, word):
    count = 0
    words = text.split()
    for w in words:
        if w == word:
            count += 1
    return count

blob_connection_string = os.getenv('AZURE_BLOB_CONNECTION_STRING')
blob_service_client = BlobServiceClient.from_connection_string(blob_connection_string)
blob_container_name = "raamatud"
blob_konteineri_loomine(blob_container_name)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
