from eth_account import Account

# Enable mnemonic features
Account.enable_unaudited_hdwallet_features()

# Generate mnemonic
mnemonic = Account().create_with_mnemonic()[1]

print("Your generated mnemonic:", mnemonic)
