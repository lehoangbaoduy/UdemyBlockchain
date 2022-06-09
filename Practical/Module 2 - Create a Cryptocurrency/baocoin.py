# Module 2 - Create a Cryptocurrency
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

# Part 1 - Building a Blockchain
class Blockchain:

    def __init__(self):
        self.chain = []

        # transaction list
        self.transactions = []

        # proof = 1 means nonce = 1
        self.create_block(proof = 1, previous_hash = '0')

        # the nodes
        self.nodes = set()

    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                'timestamp': str(datetime.datetime.now()),
                'proof': proof,
                'previous_hash': previous_hash,
                "transactions": self.transactions}
        
        self.transactions = []
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

    # append a transaction into the transaction list
    # probably an object that has keys of sender, receiver, and amount sending
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({"sender": sender,
                                "receiver": receiver,
                                "amount": amount})
        
        last_block = self.get_last_block

        # return the block index that the transaction will be added
        # because the last block is a "locked" block
        # so we will append the transaction to the "will be" created block
        return last_block['index'] + 1

    
    def add_node(self, address):
        # convert the address to URL object
        parsed_url = urlparse(address)

        # add the new nodes IP address and port to the set 
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        # our whole internet network that contains all of the nodes
        network = self.nodes

        # our longest chain, initialize it to be None 
        longest_chain = None

        # maximum length of the chain
        max_length = len(self.chain)

        # for each node in our network
        for node in network:
            # send a request to get the chain and its length
            response = requests.get(f'http:/{node}/get_chain')

            # if the request is good
            if response.status_code == 200:
                # assign 2 new variables with each key
                length = response.json()['length']
                chain = response.json()['chain']

                # if the current length > max length 
                # and the chain is valid
                if length > max_length and self.is_chain_valid(chain):
                    # current length is the maximum length
                    max_length = length
                    longest_chain = chain

        # if we found the new longest chain
        if longest_chain:
            # update our chain to be the longest one
            self.chain = longest_chain
            return True               
        
        return False

# Part 2 - Mining our Blockchain

# Creating a Web App
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Creating an address for the node on Port 5000
node_address = str(uuid4()).replace('-', '')

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
    # add new transaction when mining a block
    blockchain.add_transaction(sender = node_address, receiver = 'Le', amount = 10)
    # then add new block to the chain
    new_block = blockchain.create_block(proof, previous_hash)
    # postman response
    response = {'message': 'Congratulations, you just mined a block!', 
                'index': new_block['index'],
                'timestamp': new_block['timestamp'],
                'proof': new_block['proof'],
                'previous_hash': new_block['previous_hash'],
                "transactions": new_block['transactions']}

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

# Adding a new transaction to the Blockchain
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']

    # if all the keys in the transaction_keys list
    # are not in our json
    if not all (key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    
    # the index of the block that has new transactions
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'This transaction will be added to block {index}'}

    # return of a 'created' status code
    return jsonify(response), 201


# Part 3 - Decentralizing the Blockchain

# Connecting new nodes
@app.route('/connect_node', methods=['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')

    if nodes is None:
        return 'No node', 400

    for node in nodes:
        blockchain.add_node(node)
    
    response = {'message': 'All the nodes are now connected. The Blockchain now contains the following nodes',
                'total_nodes': list(blockchain.nodes)}

    return jsonify(response), 201

# Replace the chain in any node in the chain that does not have up to date chain
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_replace = blockchain.replace()

    if is_chain_replace:
        response = {'message': 'The chain was replaced by the longest one.',
                    'new_chain': blockchain.chain}
    else: 
        response = {'message': 'All good. The chain is the longest one.',
                    'actual_chain': blockchain.chain}
    
    return jsonify(response), 200

# Running the app
app.run(host='0.0.0.0', port=5000)