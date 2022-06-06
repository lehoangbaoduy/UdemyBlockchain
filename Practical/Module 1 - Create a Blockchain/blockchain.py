# Module 1 - Create a Blockchain
import datetime
import hashlib
import json
from flask import Flask, jsonify

# Part 1 - Building a Blockchain
class Blockchain:

    def __init__(self):
        self.chain = []

        # proof = 1 means nonce = 1
        self.create_block(proof = 1, previous_hash = '0')

    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                'timestamp': str(datetime.datetime.now()),
                'proof': proof,
                'previous_hash': previous_hash}

        self.chain.append(block)
        return block

    def get_last_block(self):
        # return the last block by taking index of -1 from the array
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        # initial nonce value
        new_proof = 1
        check_proof = False

        # if we still cannot find the nonce value
        while check_proof is False:
            # hash the block by taking initial nonce value^2 minus previous nonce value^2
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    def hash(self, block):
        # json.dumps will convert object to string, then encode()
        encoded_block = json.dumps(block, sort_keys = True).encode()
        # then convert it to be 64 bit hex number
        return hashlib.sha256(encoded_block).hexdigest()

    # 1 - check if previous_hash of a block = hash of previous block
    # 2- check if hash of current block is valid
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1

        while block_index < len(chain):
            # current block
            block = chain[block_index]

            # check #1
            if block['previous_hash'] != self.hash(previous_block):
                return False

            # check #2
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False

            # increment value
            previous_block = block
            block_index += 1           
        
        return True

# Part 2 - Mining our Blockchain

# Creating a Web App
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Creating a Blockchain
blockchain = Blockchain()

# Mining a new block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    # get the last block
    previous_block = blockchain.get_last_block()
    # get the has of the last block
    previous_proof = previous_block['proof']
    # then past it to proof_of_work function to find nonce value that has hash[:4] == '0000'
    proof = blockchain.proof_of_work(previous_proof)
    # get the has of the previous block
    previous_hash = blockchain.hash(previous_block)
    # then add new block to the chain
    new_block = blockchain.create_block(proof, previous_hash)
    # postman response
    response = {'message': 'Congratulations, you just mined a block!', 
                'index': new_block['index'],
                'timestamp': new_block['timestamp'],
                'proof': new_block['proof'],
                'previous_hash': new_block['previous_hash']}

    return jsonify(response), 200

# Getting the full blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}

    return jsonify(response), 200

# Checking if the Blockchain is valid
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)

    if is_valid:
        response = {'message': 'All good. Blockchain is valid'}
    else: 
        response = {'message': 'We have a problem. Blockchain is not valid'}
    

    return jsonify(response), 200

# Running the app
app.run(host='0.0.0.0', port=5000)