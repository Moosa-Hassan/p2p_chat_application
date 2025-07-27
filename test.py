# test_chat.py
import time
from node import Node

# Create Alice and Bob
alice = Node("Alice", 0, "127.0.0.1", 8001)
bob = Node("Bob", 1, "127.0.0.1", 8002)

# Start their listeners (servers)
alice.listener("127.0.0.1", 8001)
bob.listener("127.0.0.1", 8002)

# Update each other's directories manually (simulate a join)
alice.update_directory("Bob", "J", bob.public_key, "127.0.0.1", 8002)
bob.update_directory("Alice", "J", alice.public_key, "127.0.0.1", 8001)

# Wait a bit to ensure listeners are up
time.sleep(1)

# Send a message from Alice to Bob
# print("\n[TEST] Alice sending 'Hello Bob!' to Bob")
alice.send_message("Bob", "Hello Bob!")

# Wait to allow message delivery
time.sleep(1)

# Send a message from Bob to Alice
# print("\n[TEST] Bob sending 'Hi Alice!' to Alice")
bob.send_message("Alice", "Hi Alice!")

# Keep the program running a bit longer to see outputs
time.sleep(2)

# Clean up (optional)
alice.leave()
bob.leave()
