from time import sleep, ctime, time, gmtime
import datetime, pytz
from brownie import network
from simple_scheduler.recurring import recurring_scheduler
import brownie
from brownie.network import gas_price, priority_fee
import sys
new_path = 'scripts/.'
if new_path not in sys.path:
    sys.path.append(new_path)
import deployment

## MAIN SWITCH
MAINNET = False
## MAIN SWITCH

AUCTION_DURATION = 60*60*24*3 if MAINNET else 5                                                             # <------------ CHANGE FOR MAINNET 60*60*24*3 # 3 days 
GAS_FEE = '70 gwei' if MAINNET else '100 gwei'                                                              # <------------ CHANGE FOR MAINNET 70 gwei

SCHEDULER_PERIOD_SEC = 60*60*24*3 if MAINNET else 30
SCHEDULER_START = "Sep 26 00:00:00 2021" if MAINNET else "Sep 25 13:40:00 2021"
SCHEDULER_STOP = "Jan 2 01:00:00 2022" if MAINNET else "Sep 25 14:40:00 2021"

# Settings gas fees
is_development = True if network.show_active() == 'development' else False
deployment.gas_input = gas_price(GAS_FEE) if is_development else priority_fee(GAS_FEE)
deployment.tx_params = {'from': deployment.DEPLOYER, 'gas_price': deployment.gas_input} if is_development else {'from': deployment.DEPLOYER, 'priority_fee': deployment.gas_input}
print('Tx params: ', deployment.tx_params)

# Loading contracts
emograms, marketplace_contract, vault, marketplace = deployment.load_deployed_contracts()   # <------------ CHANGE FOR MAINNET withProxy=True &fromJSON=True
print('EmogramsCollectibe: ', emograms)
print('EmogramMarketplaceUpgradeable: ', marketplace)
print('FounderVault: ', vault)
print('Current auction cycle: ', total_auction_counter)

def call_function():
    total_auction_counter = marketplace.initialAuction()['cycle']
    if total_auction_counter <= 34:
        total_auction_counter = total_auction_counter + 1
        tz = pytz.timezone('America/New_York')
        nyc = datetime.datetime.now(tz)
        print('------- Auction #%s -------' %(total_auction_counter))
        print('Ran at local:', ctime(time()))
        print('NYC time: ', nyc)
        deployment.run_initialAuction_cycles(emograms, marketplace, AUCTION_DURATION)
    else:
        print('Auction finisheed, no more stepAuction calls.')
        recurring_scheduler.job_summary()
        total_auction_counter = total_auction_counter + 1

print('\nCurrent localtime:', ctime(time()))

condition = True if MAINNET else False
while condition:
    if gmtime().tm_hour == 6:                                                   # <------------ CHANGE FOR MAINNET 6                             
        if gmtime().tm_min == 0:                                                # <------------ CHANGE FOR MAINNET 0
            condition = False

recurring_scheduler.add_job(target=call_function,
                            period_in_seconds=SCHEDULER_PERIOD_SEC,
                            start=SCHEDULER_START,
                            stop=SCHEDULER_STOP,
                            job_name="scheduler_auction",
                            tz="America/New_York")
recurring_scheduler.verbose = True
recurring_scheduler.job_summary()

def main():
    recurring_scheduler.run()
    sleep(1)
    if total_auction_counter <= 35:
        sys.exit()

