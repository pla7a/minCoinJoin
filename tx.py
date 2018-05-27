from main import *
from address import *

bitcoin.SelectParams('testnet')

class transaction:
	# n = integer of number of mixers
	# addressFrom = object address of address the BTC is being sent from
	# addressTo = list of string and amount of sender's output addresses [(address, amount)]
	# amount = float of amount to send
	# fee = float of amount to send (estimates fees if none specified)
	def __init__(self, n, addressFrom, addressTo, mixer_list, fee=None):
		# Sum the output amounts of the transaction
		self.amount =  sum([x[1] for x in addressTo])

		# Keep running total of sum of inputs to account for change output
		self.sum_inputs = 0
		self.sum_outputs = 0

		# Running total of mixer fees
		self.mixer_fees = 0

		# Check user balance is large enough to send transaction
		if (addressFrom.balance < self.amount):
			raise Exception("You have insufficient funds to do this transaction.")

		self.addressTo = [(stand_address(x[0]),x[1]) for x in addressTo]

		self.sender_addr = addressFrom

		# Estimate fee for the trsnaction (if fee=None)
		if not fee:
			self.fee = self.estimate_fee(n, priority="medium")
		else:
			self.fee = fee

		# Return list of own UTXOs [CMutableTxIn(txid, idx)]
		self.own_inputs, _ = self.select_utxos(self.sender_addr, fee=self.fee)

		# List of all mixers used in transaction
		self.mixers = []

		# Variable recording list of amounts each mixer has committed [(mixer, amount)]
		self.mixer_amounts = []

		# Return list of mixer's UTXOs [CMutableTxIn(txid, idx)]
		self.mixer_inputs = self.select_mixer_utxos(n, mixer_list)
		self.pruned_mixer_inputs = [x[1][0] for x in self.mixer_inputs]

		# self.inputs is list of utxos of form [CMutableTxIn(txid,vout)]
		self.inputs = self.own_inputs+self.pruned_mixer_inputs

		# List of outputs of form CMutableTxOut(amount*COIN, address.to_scriptPubKey())
		self.outputs = self.select_outputs(addressTo, self.mixers)
		self.outputs.append(bc.CMutableTxOut((self.sum_inputs-self.fee-self.sum_outputs)*bc.COIN, addressFrom.pubAddr.to_scriptPubKey()))

		self.tx = bc.CMutableTransaction(self.inputs, self.outputs)
		

	# Returns list of n mixers (address, max_amount) such that max_amount >= self.amount
	def select_mixer_utxos(self, n, mixer_list):
		if len(mixer_list) < n:
			raise Exception("There are not enough mixers available right now.")
		# Sort the mixer list based on the fees
		mixer_list.sort(key=lambda x : x.fee)

		# Check the sender has enough to cover the fees
		if sum([x.fee for x in mixer_list[0:n]]) > self.fee:
			raise Exception("Your fee is not large enough to find your desired number of mixers")

		# Take n mixers with lowest fees
		sum_fees = 0
		for i in range(n):
 			if mixer_list[i].balance >= self.amount:
 				self.mixers.append(mixer_list[i])


		# Return a list of to-be-used utxos from each of the selected mixers
		mixer_utxos = []

		for x in self.mixers:
			utxo_set, sum_utxo = self.select_utxos(x)
			self.mixer_amounts.append((x,sum_utxo+x.fee))
			mixer_utxos.append((x,utxo_set))
			self.mixer_fees += x.fee

		# Return type is [[(txid,idx,amount)]]
		return mixer_utxos


	# Select utxos for specified address s.t sum(utxo amount) >= amount
	# Return type is list [(txid, idx, amount)]
	def select_utxos(self, addr, fee=0):
		# Naive UTXO selection algorithm - can be updated later
		all_utxos = addr.all_utxos()
		utxos = []
		sum_utxo = 0
		i = 0

		while sum_utxo < self.amount:
			utxos.append(bc.CMutableTxIn(bc.COutPoint(bc.lx(all_utxos[i]["txid"]), all_utxos[i]["vout"])))
			sum_utxo += all_utxos[i]["amount"]
			i += 1

		self.sum_inputs += sum_utxo

		return utxos, sum_utxo


	# Estimate fee of transaction with n other participants and desired priority (low =< 12 blocks, med =< 6 blocks, high =< 2 blocks)
	def estimate_fee(self, n, priority):
		return 0.01


	# Return list of outputs of transaction
	def select_outputs(self, addressTo, mixers):
		txout = []
		to_address = []

		# Cover addresses to CBitcoinAddress objects
		for (addr, amt) in self.addressTo:
			txout.append(bc.CMutableTxOut(amt*bc.COIN, addr.pubAddr.to_scriptPubKey()))
			self.sum_outputs += amt

		# Add mixer's outputs to txout
		for x in self.mixer_amounts:
			txout.append(bc.CMutableTxOut(x[1]*bc.COIN, x[0].pubAddr.to_scriptPubKey()))
			self.sum_outputs += x[1]

		return txout


