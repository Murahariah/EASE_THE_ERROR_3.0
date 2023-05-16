import hashlib
import json
import time
import sqlite3
import ipfshttpclient

# Define the Blockchain class
class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_votes = []
        self.voters = set()

    def add_vote(self, voter_id, candidate):
        if voter_id not in self.voters:
            self.voters.add(voter_id)
            self.current_votes.append({'voter_id': voter_id, 'candidate': candidate})

    def mine(self):
        self.chain.append(self.current_votes)
        self.current_votes = []

    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': time.time(),
                 'proof': proof,
                 'previous_hash': previous_hash}
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True

    def store_blockchain(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.chain, f)

    def load_blockchain(self, filename):
        with open(filename, 'r') as f:
            self.chain = json.load(f)


# Define the VotingSystem class
class VotingSystem:
    def __init__(self):
        self.voters = set()
        self.blockchain = Blockchain()

        # Create a database connection
        self.conn = sqlite3.connect('C:/Users/murahari/PycharmProjects/pythonProject1/venv/maths/votes.sqlite')
        self.c = self.conn.cursor()

        # Create a table to store votes
        self.c.execute('''CREATE TABLE IF NOT EXISTS votes
                         (voter_id text, candidate text, timestamp real)''')

    def add_voter(self, voter_id):
        self.voters.add(voter_id)
        print(f"Voter {voter_id} has been registered.")

    def add_vote(self, voter_id, candidate):
        if voter_id not in self.voters:
            print("Invalid voter ID.")

        else:
            # Check if the candidate is valid
            valid_candidates = ['Alice', 'Bob', 'Charlie', 'Dave']
            if candidate not in valid_candidates:
                print("Invalid candidate.")
            else:
                # Add the vote to the blockchain
                self.blockchain.add_vote(voter_id, candidate)

                # Add the vote to the database
                timestamp = time.time()
                self.c.execute("INSERT INTO votes VALUES (?, ?, ?)",
                               (voter_id, candidate, timestamp))
                self.conn.commit()
                print("Vote added to the blockchain and database.")

    def view_results(self):
        # Get the vote count for each candidate from the database
        self.c.execute("SELECT candidate, COUNT(*) FROM votes GROUP BY candidate")
        results = self.c.fetchall()

        # Display the results
        print("Election Results:")
        for result in results:
            print(f"{result[0]}: {result[1]}")

    def close_voting(self):
        # Check if all voters have voted
        self.c.execute("SELECT COUNT(DISTINCT voter_id) FROM votes")
        num_voted = self.c.fetchone()[0]
        num_voters = len(self.voters)
        if num_voted < num_voters:
            print(f"{num_voters - num_voted} voters have not voted yet. Please wait for them to vote.")
        else:
            # Display the final results
            self.view_results()

            # Store the blockchain to a file
            self.blockchain.store_blockchain('C:/Users/murahari/PycharmProjects/pythonProject1/venv/maths/blockchain.json')

            # Close the database connection
            self.conn.close()
            print("Voting has ended. Blockchain and database have been stored.")

def main():
    # Create a new instance of the VotingSystem class
    vs = VotingSystem()

    # Add some voters
    vs.add_voter("Voter 1")
    vs.add_voter("Voter 2")
    vs.add_voter("Voter 3")
    vs.add_voter("Voter 4")
    vs.add_voter("Voter 5")

    # Let the voters vote
    vs.add_vote("Voter 1", "Alice")
    vs.add_vote("Voter 2", "Bob")
    vs.add_vote("Voter 3", "Charlie")
    vs.add_vote("Voter 4", "Bob")
    vs.add_vote("Voter 5", "Alice")
    vs.add_vote("Voter 6", "Alice")

    # Close the voting and display the results
    vs.close_voting()

if __name__ == '__main__':
    main()