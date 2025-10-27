# Copyright (C) 2015-2025 The Neo Project.
#
# testcases/initial.py file belongs to the neo project and is free
# software distributed under the MIT software license, see the
# accompanying file LICENSE in the main directory of the
# repository or http://www.opensource.org/licenses/mit-license.php
# for more details.
#
# Redistribution and use in source and binary forms with or without
# modifications are permitted.

from neo.contract import *
from testcases.basics.gas_rpc_transfer_multisig import GasRpcTransferMultiSign
from testcases.basics.neo_rpc_transfer_multisig import NeoRpcTransferMultiSign
from testcases.testing import Testing


# Operation: this case initializes the NEO and GAS balance of the others[0] and committee-address.
# Expect Result: The NEO and GAS balance of the others[0] and committee-address are initialized as expected.
class TestingInitial(Testing):

    def __init__(self):
        super().__init__(__class__.__name__)

    def run_test(self):
        # Step 1: initialize the NEO and GAS balance of the others[0] account
        neo_initial = NeoRpcTransferMultiSign()
        neo_initial.run()

        gas_initial = GasRpcTransferMultiSign()
        gas_initial.run()

        self._initialize_gas_for_committee()

    def _initialize_gas_for_committee(self):
        # Step 2: transfer 10000 GAS from the BFT account to the committee account
        source160 = self.bft_address()
        dest160 = self.committee_address()
        amount = 10000_00000000  # 10000 GAS
        script = ScriptBuilder().emit_dynamic_call(
            script_hash=GAS_CONTRACT_HASH,
            method='transfer',
            call_flags=(CallFlags.STATES | CallFlags.ALLOW_CALL | CallFlags.ALLOW_NOTIFY),
            args=[source160, dest160, amount, None],  # transfer(from, to, 10000 GAS, None)
        ).to_bytes()

        # Step 3: get source and destination GAS balance
        source_balance = self.client.get_gas_balance(source160)
        self.logger.info(f"Source {source160} GAS balance: {source_balance}")

        dest_balance = self.client.get_gas_balance(dest160)
        self.logger.info(f"Destination {dest160} GAS balance: {dest_balance}")

        block_index = self.client.get_block_index()
        tx = self.make_multisig_tx(script, self.default_sysfee, self.default_netfee, block_index+10)
        tx_hash = self.client.send_raw_tx(tx.to_array())
        tx_id = tx_hash['hash']
        self.logger.info(f"Transaction sent: {tx_id}")

        # Step 4: wait for the next block
        block_index = self.client.get_block_index()
        self.wait_next_block(block_index)

        # Step 5: check the destination GAS balance
        to_balance = self.client.get_gas_balance(dest160)
        self.logger.info(f"Destination {dest160} GAS balance: {to_balance}, difference: {to_balance - dest_balance}")
        assert to_balance == dest_balance + amount, f"Expected to_balance == {dest_balance + amount}, got {to_balance}"

        # Step 5: check the application log
        application_log = self.client.get_application_log(tx_id)
        self.logger.info(f"Application log: {application_log}")


# Run with: python3 -B -m testcases.initial
if __name__ == "__main__":
    test = TestingInitial()
    test.run()
