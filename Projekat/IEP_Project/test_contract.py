from web3 import Web3
from web3 import HTTPProvider
import os

GANACHE_URL = os.getenv("GANACHE_URL", "http://127.0.0.1:8545")
OWNER_PRIVATE_KEY = os.getenv("OWNER_PRIVATE_KEY", "0xb64be88dd6b89facf295f4fd0dda082efcbe95a2bb4478f5ee582b7efe88cf60")
OWNER_ADDRESS = os.getenv("OWNER_ADDRESS", "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1")

print(f"Ganache URL: {GANACHE_URL}")
print(f"Owner Private Key: {OWNER_PRIVATE_KEY}")
print(f"Owner Address: {OWNER_ADDRESS}")

w3 = Web3(HTTPProvider(GANACHE_URL))

print(f"\nConnected: {w3.is_connected()}")
print(f"Chain ID: {w3.eth.chain_id}")
print(f"Latest block: {w3.eth.block_number}")
print(f"\nAvailable accounts:")
for i, acc in enumerate(w3.eth.accounts):
    balance = w3.eth.get_balance(acc)
    print(f"  {i}: {acc} - Balance: {w3.from_wei(balance, 'ether')} ETH")

# Test if owner address has balance
owner_checksum = Web3.to_checksum_address(OWNER_ADDRESS)
owner_balance = w3.eth.get_balance(owner_checksum)
print(f"\nOwner address balance: {w3.from_wei(owner_balance, 'ether')} ETH")

if owner_balance == 0:
    print("WARNING: Owner address has no balance!")