from main import *
from tx import *

# Object of Bitcoin address. Stores private key (if one is given), public key, list of all utxos
class address:
	def __init__(self):
		pass

	# Return list of all utxos (txid, idx, amount) for the address
	def all_utxos(self):
		# Of form [{address, txid, vout, scriptPubKey, amount, satoshis, height, confirmations}]
		utxo_json = requests.get("https://testnet.blockexplorer.com/api/addr/%s/utxo" %(self.pubAddr))
		return utxo_json.json()
	def update_balance(self):
		self.balance = sum([x["amount"] for x in self.all_utxos()])


# Class for mixer addresses (only public address is specified)
# pubAddr is string of P2PKH address
# outAddr is string of one P2PKH output address for the transaction (limited to one address to begin with)
# amount is maximum they are willing to mix with (if None, then amount is sum of all UTXOs)
# fee is amount mixer is charging to do the mixing
class mixer(address):
	def __init__(self, pubAddr, balance=None, outAddr=None, fee=0):
		self.pubAddr = bw.P2PKHBitcoinAddress(pubAddr)
		if not outAddr:
			self.output_addr = [self.pubAddr]
		else:
			self.output_addr = outAddr

		if (not balance):
			self.update_balance()
		else:
			self.balance = balance

		self.fee = fee

# Class for sender addresses (private key is specified)
class sender(address):
	def __init__(self, privKey):
		self.priv = bw.CBitcoinSecret(privKey)
		self.pubAddr = bw.P2PKHBitcoinAddress.from_pubkey(self.priv.pub)
		self.pubKey = bw.CBitcoinSecret(privKey).pub
		self.update_balance()


class stand_address(address):
	def __init__(self, pubAddr, privKey=None):
		self.pubAddr = bw.P2PKHBitcoinAddress(pubAddr)
		if not privKey:
			self.privKey = privKey
