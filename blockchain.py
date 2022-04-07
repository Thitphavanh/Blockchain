import datetime
import json
import hashlib
from flask import Flask, jsonify


class Blockchain:
    def __init__(self):  # ເກັບກຸ່ມຂອງ Block list ບ່ອນເກັບ block
        self.chain = []  # list ບ່ອນເກັບ block
        self.transaction = 0  # genesis block
        self.create_block(nonce=1, previous_hash="0")

    def create_block(self, nonce, previous_hash):  # ສ້າງ Block ຂຶ້ນໃນລະບົບ Blockchain
        # ເກັບສ່ວນປະກອບຂອງ Block ແຕ່ລະ Block
        block = {
            "index": len(self.chain)+1,
            "timestamp": str(datetime.datetime.now()),
            "nonce": nonce,
            "data": self.transaction,
            "previous_hash": previous_hash
        }
        self.chain.append(block)
        return block

    def get_previous_block(self):  # ໃຫ້ບໍລິການກ່ຽວກັບ Block ກ່ອນໜ້າ
        return self.chain[-1]

    def hash(self, block):  # ເຂົ້າລະຫັດ Block
        # ແປງ python object (dict) => json object
        encode_block = json.dumps(block, sort_keys=True).encode()  # sha-256
        return hashlib.sha256(encode_block).hexdigest()

    # ຢາກໄດ້ຄ່າ nonce = ??? ທີ່ສົ່ງຜົນໃຫ້ໄດ້ target hash => 4 ຫຼັກທຳອິດ => 0000xxxxxx
    def proof_of_work(self, previous_nonce):
        new_nonce = 1  # ຄ່າ nonce ທີ່ຕ້ອງການ
        check_proof = False  # ໂຕແປທີ່ເຊັຄຄ່າ nonce ໃຫ້ໄດ້ຕາມ target ທີ່ກຳນົດ

        while check_proof is False:  # ແກ້ໂຈດທາງຄະນິດສາດ
            hashoperation = hashlib.sha256(
                str(new_nonce**2 - previous_nonce**2).encode()).hexdigest()  # ເລກຖານ 16 ມາ 1 ຊຸດ
            if hashoperation[:4] == "0000":
                check_proof = True
            else:
                new_nonce += 1
        return new_nonce

    def is_chain_valid(self, chain):  # ກວດສອບ block
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]  # block ທີ່ກວດສອບ

            if block["previous_hash"] != self.hash(previous_block):
                return False

            previous_nonce = previous_block["nonce"]  # nonce block ກ່ອນໜ້ານີ້
            nonce = block["nonce"]  # nonce ຂອງ block ທີ່ກວດສອບ
            hashoperation = hashlib.sha256(
                str(nonce**2 - previous_nonce**2).encode()).hexdigest()  # 5

            if hashoperation[:4] != "0000":
                return False
            previous_block = block
            block_index += 1
        return True


# web server
app = Flask(__name__)
blockchain = Blockchain()  # ໃຊ້ງານ Blockchain

# routing


@app.route('/')
def hello():
    return "<h1>Hello Blockchain</h1>"


@app.route('/get_chain', methods=["GET"])
def get_chain():
    response = {
        "chain": blockchain.chain,
        "length": len(blockchain.chain)
    }
    return jsonify(response), 200


@app.route('/mining', methods=["GET"])
def mining_block():
    amount = 1000000  # ຈຳນວນເງິນທໃນການເຮັດທຸລະກຳ
    blockchain.transaction = blockchain.transaction+amount  # pow
    previous_block = blockchain.get_previous_block()
    previous_nonce = previous_block["nonce"]
    nonce = blockchain.proof_of_work(previous_nonce)  # nonce
    previous_hash = blockchain.hash(previous_block)  # hash block ກ່ອນໜ້າ
    block = blockchain.create_block(nonce, previous_hash)  # update block ໃໝ່
    response = {
        "message": "Mining Block ແລ້ວໆ",
        "index": block["index"],
        "timestamp": block["timestamp"],
        "data": block["data"],
        "nonce": block["nonce"],
        "previous_hash": block["previous_hash"]
    }
    return jsonify(response), 200


@app.route('/is_valid', methods=["GET"])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {"message": "Blockchain Is Valid"}
    else:
        response = {"message": "Have Problem , Blockchain Is Not Valid"}
    return jsonify(response), 200


# run server
if __name__ == "__main__":
    app.run()
