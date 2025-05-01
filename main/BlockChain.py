import hashlib
import json
import time
from uuid import uuid4
import requests
from flask import Flask, request, jsonify
from urllib.parse import urlparse


class Chain:
    def __init__(self):
        self.chain = []       # List to store all blocks
        self.txns = []        # Current list of transactions
        self.new_block(prev_hash=1, proof=100)  # Create genesis block
        self.nodes = set()    # Set to store registered nodes (peers)

    def new_block(self, proof, prev_hash=None):
        # Creates a new block and adds it to the chain
        blk = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'txns': self.txns,
            'proof': proof,
            'prev_hash': prev_hash or self.hash(self.chain[-1]),
        }
        self.txns = []  # Reset the transaction list
        self.chain.append(blk)
        return blk

    def new_txn(self, sender, recipient, amt):
        # Adds a new transaction to the list
        self.txns.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amt,
        })
        return self.last_blk['index'] + 1  # Index of the block that will hold this txn

    def proof_of_work(self, last_proof):
        # Simple Proof of Work algorithm:
        # Find a number `proof` such that hash(last_proof + proof) contains 4 leading zeroes
        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1
        return proof

    def register_node(self, addr):
        # Add a new node to the network
        parsed = urlparse(addr)
        self.nodes.add(parsed.netloc)

    def valid_chain(self, chain):
        # Check if a given blockchain is valid
        last = chain[0]
        idx = 1

        while idx < len(chain):
            blk = chain[idx]
            print(f'{last}\n{blk}\n---')  # Debug print
            if blk['prev_hash'] != self.hash(last):
                return False
            if not self.valid_proof(last['proof'], blk['proof']):
                return False
            last = blk
            idx += 1
        return True

    def resolve(self):
        # Consensus algorithm:
        # Replace local chain with the longest valid chain in the network
        longest = self.chain
        for node in self.nodes:
            try:
                r = requests.get(f'http://{node}/chain')
                if r.status_code == 200:
                    data = r.json()
                    if data['length'] > len(longest) and self.valid_chain(data['chain']):
                        longest = data['chain']
            except:
                continue
        if longest != self.chain:
            self.chain = longest
            return True
        return False

    @property
    def last_blk(self):
        # Returns the last block in the chain
        return self.chain[-1]

    @staticmethod
    def hash(blk):
        # Creates a SHA-256 hash of a block
        blk_str = json.dumps(blk, sort_keys=True).encode()
        return hashlib.sha256(blk_str).hexdigest()

    @staticmethod
    def valid_proof(last, proof):
        # Validates the proof: does hash(last_proof + proof) start with 4 zeroes?
        guess = f'{last}{proof}'.encode()
        return hashlib.sha256(guess).hexdigest()[:4] == "0000"


app = Flask(__name__)
node_id = str(uuid4()).replace('-', '')  # Unique ID for this node
chain = Chain()


@app.route('/mine', methods=['GET'])
def mine():
    # Mine a new block:
    # - Run proof of work
    # - Reward miner
    # - Forge new block
    last = chain.last_blk
    proof = chain.proof_of_work(last['proof'])

    chain.new_txn(sender="0", recipient=node_id, amt=1)  # Reward txn
    blk = chain.new_block(proof, chain.hash(last))

    return jsonify({
        'index': blk['index'],
        'txns': blk['txns'],
        'proof': blk['proof'],
        'prev_hash': blk['prev_hash'],
    }), 200


@app.route('/transaction/new', methods=['POST'])
def new_txn():
    # Accept a new transaction
    data = request.get_json()
    if not all(k in data for k in ['sender', 'recipient', 'amount']):
        return "Missing values", 400
    idx = chain.new_txn(data['sender'], data['recipient'], data['amount'])
    return jsonify({'msg': f'Txn added to block {idx}'}), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    # Return the full blockchain
    return jsonify({
        'chain': chain.chain,
        'length': len(chain.chain)
    }), 200


@app.route('/nodes/register', methods=['POST'])
def register():
    # Register new nodes to the network
    data = request.get_json()
    nodes = data.get('nodes')
    if not nodes:
        return "Provide a valid list", 400
    for n in nodes:
        chain.register_node(n)
    return jsonify({
        'msg': 'Nodes added',
        'nodes': list(chain.nodes)
    }), 201


@app.route('/nodes/resolve', methods=['GET'])
def resolve():
    # Trigger consensus algorithm
    replaced = chain.resolve()
    msg = 'Chain replaced' if replaced else 'Chain is authoritative'
    return jsonify({
        'msg': msg,
        'chain': chain.chain
    }), 200


if __name__ == '__main__':
    # Start the server
    app.run(host='0.0.0.0', port=5000)

