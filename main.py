from __future__ import absolute_import, division, print_function, unicode_literals
import bitcoin
import hashlib
import bitcoin as b
import bitcoin.core as bc 
import bitcoin.core.script as bcs
import bitcoin.core.scripteval as bcseval
import bitcoin.wallet as bw
import bitcoin.signmessage as bsm
import json
import requests
import random
from tx import *
from address import *

bitcoin.SelectParams('testnet')

# If the user wishes to generate a new Bitcoin address as brain wallet (not recommended because of lack of randomness)
def generate_address(random_str):
	addr = sender('cShz47oLnCViyuuGaGVtJkDcqrriKLVJWuprgXYwpqxypg8z7brh')
	byte_str = random_str.encode('UTF-8')
	h = hashlib.sha256(byte_str).digest()
	seckey = bw.CBitcoinSecret.from_secret_bytes(h)
	addr.priv = seckey
	addr.pubKey = seckey.pub
	addr.pubAddr = bw.P2PKHBitcoinAddress.from_pubkey(addr.priv.pubKey)
	addr.update_balance()
	return addr


# Send a transaction
def create_tx(n, addressFrom, addressTo, mixer_list, fee=None):
	pre_tx = transaction(n, addressFrom, addressTo, mixer_list, fee=None)
	own_n = len(pre_tx.own_inputs)

	# Get inputs signed by each of the miners
	for x in pre_tx.mixer_inputs:
		sig_mixer, pubKey_mixer = send_tx(pre_tx.tx, x, pre_tx.pruned_mixer_inputs)
		x.scriptSig = bcs.CScript([sig_mixer, pubKey_mixer])

	# Sign inputs owned by sender's address
	txin_scriptPubKey = bcs.CScript([bcs.OP_DUP, bcs.OP_HASH160, bc.Hash160(addressFrom.pubKey), bcs.OP_EQUALVERIFY, bcs.OP_CHECKSIG])
	for i in range(own_n):
		sighash = bcs.SignatureHash(txin_scriptPubKey, pre_tx.tx, i, bcs.SIGHASH_ALL)
		sig = addressFrom.priv.sign(sighash) + bytes([bcs.SIGHASH_ALL])
		pre_tx.inputs[i].scriptSig = bcs.CScript([sig, addressFrom.pubKey])
		bcseval.VerifyScript(pre_tx.inputs[i].scriptSig, txin_scriptPubKey, pre_tx.tx, i, (bcseval.SCRIPT_VERIFY_P2SH,))

	return pre_tx


# Sign the inputs of a transaction given the sig and pubKey
def sign_inputs(tx, inputs, sig, pubKey):
	for i in range(len(inputs)):
		inputs[i].scriptSig = bcs.CScript([sig, pubKey])


# Function to send inputs to mixer (encrypted) and have them return the sig (also encrypted)
def send_tx(tx, inputs_users, inputs):
	pass




''' 
# Test variables
mixer_list = [mixer("mvWDxMnVp6QvMHmHDthmJMDmv9nT7kvhyi"), mixer("mnBTKwSxdg2Sv2kr47g7DUqjVDnr7qxFz8")]
myAddress = sender('cShz47oLnCViyuuGaGVtJkDcqrriKLVJWuprgXYwpqxypg8z7brh')
to = [('mvWDxMnVp6QvMHmHDthmJMDmv9nT7kvhyi', 0.05)]

BELOW IS FOR TESTING PURPOSES ONLY
def mixers_sign(pre_tx):
	# Sender sends tx
	# Mixer sends back sig
	# Sender sets the scriptSig of input
	# Sender signs all inputs at once

	# Mixers return signed transaction of their inputs
	s1 = sender('cVHTqDUXwnvWt1iV7q2TsuroBWmevzUfreFSwHgMTeTRSE8eHLJ8')
	s2 = sender('cW6FqgTVewQgy3bj8Mh9tTGH6VxWoatnJRd3EVHUDCDe36vqvz8g')
	mixer_priv = [s1, s2]
	own_n = len(pre_tx.own_inputs)
	mixer_n = len(pre_tx.inputs)
	for i in range(own_n, mixer_n):
		addressFrom = mixer_priv[i-own_n]
		txin_scriptPubKey = bcs.CScript([bcs.OP_DUP, bcs.OP_HASH160, bc.Hash160(addressFrom.pubKey), bcs.OP_EQUALVERIFY, bcs.OP_CHECKSIG])
		sighash = bcs.SignatureHash(txin_scriptPubKey, pre_tx.tx, i, bcs.SIGHASH_ALL)
		sig = addressFrom.priv.sign(sighash) + bytes([bcs.SIGHASH_ALL])
		pre_tx.inputs[i].scriptSig = bcs.CScript([sig, addressFrom.pubKey])
		bcseval.VerifyScript(pre_tx.inputs[i].scriptSig, txin_scriptPubKey, pre_tx.tx, i, (bcseval.SCRIPT_VERIFY_P2SH,))

	print(bc.b2x(pre_tx.tx.serialize())) '''