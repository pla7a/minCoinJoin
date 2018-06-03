# minCoinJoin

A minimal (and incomplete) implementation of Gregory Maxwell's CoinJoin for Bitcoin.  
This implementation uses Peter Todd's python-bitcoinlib as well as some other libraries. As you can see, the program is incomplete (there is no way to receive the signatures of the inputs from the mixers yet), and therefore does not actually work yet.  
The program lacks any real data-security precautions, and was written as a way for me to learn, so don't use it unless you want to probably lose some money. There are also some steps that have been skipped which may compromise privacy, therefore contradicting the initial reason to use CoinJoin. The UTXO selection algorithm is a naive one and it is likely not ideal to use it for any real transaction.
