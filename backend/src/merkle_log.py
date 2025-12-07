import hashlib
import json

class MerkleTree:
    """
    Implements a binary Merkle Tree for Blockchain-like verification.
    """
    def __init__(self):
        self.leaves = []
        self.levels = []

    def add_leaf(self, data_string):
        """Adds a new entry (vote) to the log."""
        # Hash the data to create a leaf
        leaf_hash = hashlib.sha256(data_string.encode()).hexdigest()
        self.leaves.append(leaf_hash)
        self._recalculate_tree()
        return len(self.leaves) - 1, leaf_hash

    def get_root(self):
        if not self.levels:
            return None
        return self.levels[-1][0]

    def get_proof(self, index):
        """
        Generates Merkle Proof for a specific index.
        Returns list of (hash, direction) tuples needed to reconstruct root.
        """
        if index >= len(self.leaves) or index < 0:
            return None
            
        proof = []
        current_index = index
        
        for level in self.levels[:-1]: # Don't need root in proof
            is_right_node = current_index % 2 == 1
            sibling_index = current_index - 1 if is_right_node else current_index + 1
            
            if sibling_index < len(level):
                sibling_hash = level[sibling_index]
                proof.append({
                    "hash": sibling_hash,
                    "direction": "left" if is_right_node else "right"
                })
            else:
                # Odd number of nodes, no sibling
                # In this simple implementation, we might simulate duplication or just carry up
                # For simplicity here, we assume the node pairs with itself or ignore
                pass
                
            current_index = current_index // 2
            
        return proof

    def _recalculate_tree(self):
        """Rebuilds the tree from leaves up to root."""
        if not self.leaves:
            self.levels = []
            return

        current_level = self.leaves[:]
        self.levels = [current_level]
        
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                if i + 1 < len(current_level):
                    right = current_level[i + 1]
                else:
                    right = left # Duplicate last node if odd number
                
                # Combine hash: H(left + right)
                combined = hashlib.sha256((left + right).encode()).hexdigest()
                next_level.append(combined)
            
            self.levels.append(next_level)
            current_level = next_level

    def verify_proof(self, data_string, proof, root):
        """
        Verifies that data_string belongs to the tree with root hash.
        """
        current_hash = hashlib.sha256(data_string.encode()).hexdigest()
        
        for step in proof:
            sibling = step["hash"]
            direction = step["direction"]
            
            if direction == "right":
                # Sibling is on the right: H(current + sibling)
                current_hash = hashlib.sha256((current_hash + sibling).encode()).hexdigest()
            else:
                # Sibling is on the left: H(sibling + current)
                current_hash = hashlib.sha256((sibling + current_hash).encode()).hexdigest()
                
        return current_hash == root

if __name__ == "__main__":
    mt = MerkleTree()
    mt.add_leaf("Vote A")
    mt.add_leaf("Vote B")
    mt.add_leaf("Vote C")
    
    root = mt.get_root()
    print(f"Merkle Root: {root}")
    
    # Prove Vote B (Index 1)
    proof = mt.get_proof(1)
    print("Proof for Vote B:", proof)
    
    is_valid = mt.verify_proof("Vote B", proof, root)
    print(f"Verification Result: {is_valid}")
