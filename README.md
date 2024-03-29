# ts-tax-auditor
Auditing Topshot moment transactions has always been a trouble for topshot users. All NFT transactions are taxable events, including ripping packs, rental moments and trading moments. This `auditor` script help user sort out their transactions and assign moment values for packs, rentals and trades.

## Authorship
This script is developed by **Topshot @MingDynastVase**, contact info:
- Discord: MingDynastyVase#5527
- Twitter: @MetaDynastyVase

Please feel free to ask questions or send moments as donation :)

This script is opensource and any improvement (pull-request) is welcomed. 

**There is no guaranteed that this script provides 100% accurate result. Please rely on licensed tax agents for filing your tax report.**

## Rules of Auditing
This auditor is following these rules when handling transactions:
1. Trade Ticket (TT) has no value. TT is not NFT.
2. Moments pulled from packs divide the pack price equally, considering Topshot is selling you 9 moments for price $99, then the cost of each moment is $11. Because there is no relationship between the Topshot pack prices and the secondary market moment prices. E.g. 4 Badge Rookies might have higher price than MGLEs even though the rookies have 4k mint while rares are 749 mint.
3. Rewards are considered as free, i.e. $0.00 cost, and for the challenge requirement moments:
   1. If you flip those moments after challenges, the loses are already audited.
   2. If you hold those moments (or have them locked for leaderboard rewards), there is no out-going transaction for those moments, so you are not losing anything (even the prices are tanking), the loss will be audited once you sell those moments.
4. Burned moments are considered as selling for $0.00 value, because rewards and TTs are all free (based on Rule #1 and #3).
5. Rental
   1. Rent moments from others (in rental)
      1. If paid cash for rental, the in price (received gift) will be the rental fee and out price (sent back) will be $0.00, because rented moments are just returned to previous owner.
      2. If paid moments for rental, the in price will be $0.00 and out price as well. 
      The moments paid as fee for this rental will also have out price $0.00, because you are not getting any money back from those moments.
   2. Rent moments to others (out rental)
      1. If received cash for rental, the out price (send gift) will be `original in price + rental fee`, the next in price (received back) will be the original in price:
         1. E.g. You bought a moment for $100.00 and rented it out for $5.00 and received it back later. The rented out transaction price will be `$100.00 + $5.00 = $105.00`, the received back in transaction price will be $100.00. In this way, you still have the original cost (in-price) of this moment as $100, and you have a buy-and-sell transaction with $5.00 capital gain.
      2. If received moments for rental, the out price and in price will be `original in price`. The received moments will have in price $0.00.
         1. E.g. You bought a moment for $100.00 and rented it out and received it back later. You got a free moment paid by the renter. Then the in and out price of the rented moment is unchanged ($100.00), and the moment you got is free (in-price $0.00).
         2. However, there is no way for the auditor to detect which moments are received as rental payment. So those moments will be grouped into `6. Trade` and you need to enter `$0.00` as the trade payment i.e. you paid nothing for getting those moments.
   3. If you just send moment out and receive it back for no purpose (like interact with your own external account), these transactions will be removed
6. Trade, all trades are considered as **fair**, so the overall formula `out moment total value + payment = in moment total value`
   1. Moments sent out: There is no need to itemize the out price for moments sent out, because in auditing we only care about the total gain/loss. 
      1. E.g. you paid $1000 on 2 moments and traded them out for $600, no matter how you assign the out value of each moment, the total capital loss is always $400.
   2. Moments received in: The price of each received moment needs to be assigned manually to match FMV, but the script provide a convenient way to equally distribute the total value to all received moments if they have very similar FMVs.
      1. E.g. you paid $30 for 20 base 4 moments, each can be marked as $1.50
      2. For rare/legendary moments, highly recommended to assign values manually
   3. Payment: All forms of payments (cash/venmo/crypto...) needs to reported
      1. positive if you pay extra money in the trade
      2. negative if you receive money back
7. Moment sale prices:
   1. Moments sold on Topshot MP will take out the 5% transaction fee
   2. Moments sent out for trades, follow **6.i**
   3. Moments sold on 3rd party MP are marked as 'Sent Gift', so these transactions will be handled as trades (without incoming moment or payments), use the received payment value as out price
8. `Capital gain/loss = out price - in price`, no wash sale.

## Dependency
The script is written and tested with `Python 3.10`, not using external packages.

## Runbook
### 1. Code install
Make sure your system has `git` (or `github desktop`) and `python` installed.

Open a terminal/console and **cd to any directory you want to put the code in**

Use `git clone https://github.com/hellohanchen/ts-tax-auditor.git` to pull this code.

Create an empty directory `test`
```shell
cd ts-tax-auditor
mkdir test
```

Or you can also update the `auditor.py` script to load and store csv files from other places.

### 2. Download activity log from Livetoken
https://livetoken.co/myaccount &rarr; Activity Log &rarr; Get CSV File

Livetoken will send the csv file through email containing all transactions, for tax purpose, only moments sold/burned/traded in the last tax year need to be reported, there are 2 different approaches here:
- Manually truncate the livetoken csv file to exclude all transactions after December 31st of last year (keep all transactions before that date)
  - Smaller amount of transactions being processed
- Manually truncate the final result csv file generated by the auditor to exclude all transactions after December 31st
  - Sorted out all moments, save some work for the next audit

### 3. Update input filename
Update this line to load from the downloaded file
```python
moments = load_from_activities(os.path.relpath('activityFeed.csv'))  # change me
```

### 4. Run the script
```shell
python auditor.py [0|1|2|3|4]
```
Here `[0|1|2|3|4]` refers to different steps of auditing
```shell
0 -- Start from begining, load activity log
1 -- Resume from where transactions are loaded
2 -- Resume from where packs are resolved
3 -- Resume from where rentals are resolved
4 -- Resume from where trades are resolved
```
The followings are detailed explanation about how transactions are handled in each step

#### 0 Load livetoken file
Livetoken logs are loaded, transactions are handled differently based on transaction types (`tx_type`):
- In types: `'Auction Bought', 'Bought', 'Pack', 'Received Gift', 'Reward'`
  - `'Reward'`transactions will have price marked as **0**
- Out types: `'Auction Sold', 'Burned', 'Sent Gift', 'Sold', 'Traded In'`
  - `'Burned', 'Traded In'` transactions will have price marked as **0**
- Other types: `'Listed', 'Delisted', 'Made Offer', 'Accepted Offer', 'Cancel Offer', 'Locked'` are all ignored
  - `'Accepted Offer'` transactions always have a corresponding `'Sold'` transaction

The transactions are then converted into a different format:
```shell
'identifier', 'moment', 'tx_type', 'counter_party', 'price', 'date'
```
This schema is used for all intermedia results so that we can resume the progress from any step.

After loading transactions, an intermedia result file will be output: `momentTransactions.csv`

#### 1 Handle packs
The auditor will group all transactions with type `'Pack'` by dates, and later users need to provide total value for all packs ripped on that date.

##### 1.1 Merge packs
Considering the possibility that the time of ripping packs spans two dates, the script will later ask you whether we want to merge two groups of `'Pack'` transactions into one, follow the console instruction for merge packs:
```shell
==== MERGE PACKS ====
Pack 1 on 2022-04-14, pulled 6 moments:
Series 3 | Base Set | Thomas Bryant | #4592 | 2/10/2022 on 2022-04-14T19:12:55.000Z
Series 3 | Base Set | Steven Adams | #51806 | 12/19/2021 on 2022-04-14T19:12:55.000Z
Series 3 | Base Set | Max Strus | #36463 | 12/11/2021 on 2022-04-14T19:12:55.000Z
Series 3 | Metallic Gold LE | Dwight Powell | #403 | 3/11/2022 on 2022-04-14T19:12:55.000Z
Series 3 | Base Set | Norman Powell | #22950 | 2/10/2022 on 2022-04-14T19:12:55.000Z
Series 3 | Base Set | Chuma Okeke | #26133 | 1/28/2022 on 2022-04-14T19:12:55.000Z
<====>
Pack 2 on 2022-04-15, pulled 3 moments:
Series 3 | Base Set | Reggie Jackson | #29348 | 11/3/2021 on 2022-04-15T05:55:56.000Z
Series 3 | Base Set | Danilo Gallinari | #28667 | 11/6/2021 on 2022-04-15T05:55:56.000Z
Series 3 | Base Set | Anfernee Simons | #18680 | 11/1/2021 on 2022-04-15T05:55:56.000Z
------
Merge these two packs? (yes/no)
```
The default response `yes` is marked using red color. You can check the detail timestamp to remind yourself whether the packs were bought and ripped together.

##### 1.2 Provide pack values
After all packs transactions are grouped, the auditor will ask you to provide the total payment of packs ripped on the same date
```shell
==== RESOLVE PACK ====
Pack on 2022-04-14, pulled 9 moments:
Series 3 | Base Set | Thomas Bryant | #4592 | 2/10/2022 on 2022-04-14T19:12:55.000Z
Series 3 | Base Set | Steven Adams | #51806 | 12/19/2021 on 2022-04-14T19:12:55.000Z
Series 3 | Base Set | Max Strus | #36463 | 12/11/2021 on 2022-04-14T19:12:55.000Z
Series 3 | Metallic Gold LE | Dwight Powell | #403 | 3/11/2022 on 2022-04-14T19:12:55.000Z
Series 3 | Base Set | Norman Powell | #22950 | 2/10/2022 on 2022-04-14T19:12:55.000Z
Series 3 | Base Set | Chuma Okeke | #26133 | 1/28/2022 on 2022-04-14T19:12:55.000Z
Series 3 | Base Set | Reggie Jackson | #29348 | 11/3/2021 on 2022-04-15T05:55:56.000Z
Series 3 | Base Set | Danilo Gallinari | #28667 | 11/6/2021 on 2022-04-15T05:55:56.000Z
Series 3 | Base Set | Anfernee Simons | #18680 | 11/1/2021 on 2022-04-15T05:55:56.000Z
------
Input the total payment of these packs: (default: 0)
For reward/locker room packs, just put 0
```
The default response `0` is marked using red color

##### 1.3 Store intermedia result
After resolving `'Pack'` transactions, an intermedia result file will be output: `momentWithPacks.csv`

#### 2 Handle Rentals
Everytime the script detects sending and receiving (or receiving and sending) a specific moment to a specific user, it will mark these 2 transactions as `Rental`. You can either rent a moment in (Received Gift) and then sent it back (Sent Gift) or rent a moment out (Send Gift) and then received it back (Received Gift).

##### 2.1 Handle renting moment in
For moment received and sent back to the same user consecutively (2 transactions), the auditor will ask whether these 2 transactions form a rental event
```shell
==== CLEAN IN RENTAL ====
Moment id: 6067229 #210, total transactions: 4
Moment: Series 2 | 2021 All-Star Game | Luka Don膷i膰 | #210 | 3/7/2021, 
Received from thelastdancekid on 2022-12-02T03:00:47.000Z
Sent back on 2022-12-02T04:36:32.000Z
Are these 2 transactions from a rental? (yes/no)
yes
```
If `yes` (default), then it will ask for the rental fee paid in cash, if paying moments, just enter 0
```shell
Are these 2 transactions from a rental? (yes/no)
yes
How much cash did you pay? (0)
12
```
If `no`, then it will ask whether you want to remove these 2 transactions (by marking the prices to be `$0.00`) or simply leave them there
```shell
Are these 2 transactions from a rental? (yes/no)
no
Remove these 2 transactions? (yes/no)
yes
```

##### 2.2 Handle renting moment out
For moment sent to and received back from the same user consecutively (2 transactions), the auditor will ask whether these 2 transactions form a rental event
```shell
==== CLEAN OUT RENTAL ====
Moment id: 36440735 #1777, total transactions: 7
Moment: Series 3 | 2022 NBA Playoffs | Luka Don膷i膰 | #1777 | 5/15/2022, 
Sent to creepyjeremy on 2022-08-19T00:09:35.000Z
Received back on 2022-08-19T00:11:27.000Z
Are these 2 transactions from a rental? (yes/no)
yes
```
If `yes` (default), then it will ask for the rental fee earned in cash, if earning moments, just enter 0
```shell
Are these 2 transactions from a rental? (yes/no)
yes
How much cash did you earn? (0)
0
```
If `no`, then it will ask whether you want to remove these 2 transactions or simply leave them there
```shell
Are these 2 transactions from a rental? (yes/no)
no
Remove these 2 transactions? (yes/no)
yes
```

##### 2.3 Update transaction type for rentals
Auditor will automatically update transaction types to mark rental records.
- For in rentals, `'Received Gift'` &rarr; `'Rented In'`, `'Sent Gift'` &rarr; `'Returned Back'`
- For out rentals, `'Sent Gift'` &rarr; `'Rented Out'`, `'Received Gift'` &rarr; `'Received Back'`

##### 2.4 Store intermedia result
After resolving `Rental` transactions, an intermedia result file will be output: `momentWithRentals.csv`

#### 3. Handle Trades
After resolving `Rental`s, all `'Received Gift'` and `'Sent Gift'` transactions are consider part of trades.
Transactions will be first grouped by dates and users (counter_party as in Livetoken).

##### 3.1 Merge trades
Considering the possibility that the time of sending and receiving moments from another user spans two days, after grouping transactions by dates and users, it will find trades to the same user in two consecutive dates, and ask you whether these 2 trades are actually parts of the same trades so that they should be merged together.
```shell
==== MERGE TRADES ====
Trade with EZreal88 on 2022-08-16, traded in 2 moments, traded out 2 moments, 
OUT Series 2 | Base Set | Tyler Herro | #26948 | 2/3/2021 on 2022-08-16T19:34:23.000Z
OUT Series 2 | 2021 NBA Playoffs | Carmelo Anthony | #7776 | 5/22/2021 on 2022-08-16T19:34:27.000Z
IN: Series 3 | Base Set | Moritz Wagner | #19530 | 10/24/2021 on 2022-08-16T19:35:43.000Z
IN: Series 3 | Base Set | Robin Lopez | #46176 | 12/22/2021 on 2022-08-16T19:35:43.000Z
<====>
Trade with EZreal88 on 2022-08-17, traded in 1 moments, traded out 2 moments, 
OUT Series 3 | Base Set | Jimmy Butler | #26333 | 10/25/2021 on 2022-08-17T20:35:39.000Z
IN: Series 3 | Base Set | Terry Rozier | #7708 | 12/27/2021 on 2022-08-17T20:36:23.000Z
OUT Series 3 | Base Set | Jayson Tatum | #9463 | 11/1/2021 on 2022-08-17T20:36:37.000Z
------
Merge these two trades? (no/yes)
==== SKIPPED ====
```
The default response `no` is marked using red color. 

You can check the detail timestamp to remind yourself whether these transactions are from the same trade. **Another way is to check Discord/Twitter message history to get trade details.**

##### 3.2 Assign moment values
After merging trades, you need to assign trading value to each trade. As described in `Rules`, all trades are considered fair so this equation always holds: `total value of out moments + cash = total value of in moments`. The `cash` here is positive if you are paying and negative if you are receiving. 

The trades will be assigned user-by-user, an indicator shows how many users in total and the current progress.
```shell
(User #0/198)
```
An intermedia result will be written every 20 users resolved. 

###### 3.2.1 Moments traded out
If any moment traded out, auditor will ask for the total value of out moments and assign this value to all moments equally. E.g. if 5 moments are traded out for $10.00 value, each will have $2.00 price.
```shell
==== ASSIGN TRADE VALUE ====
Trade with BradleyHansen19 on 2022-11-08, traded in 2 moments, traded out 1 moments, 
IN: Series 2 | Base Set | Cody Zeller | #27784 | 1/30/2021 on 2022-11-08T02:25:19.000Z
IN: Series 3 | Base Set | Jaren Jackson Jr. | #27112 | 11/30/2021 on 2022-11-08T02:28:00.000Z
OUT Series 3 | Hustle and Show | Darius Garland | #13602 | 1/4/2022 on 2022-11-08T02:28:51.000Z
------
Input the total value of moments sent out (0): 
5
==== ASSIGNED PRICE FOR SENT MOMENTS ====
```
**The out value is the total value of moments you traded out, not the value you received in.** So if you are selling these moments for cash (traded for cash), put the total cash you received here.

###### 3.2.2 Cash payment
If any moment received in, auditor will then ask whether you are paying/receiving cash in this trade.
```shell
Input the total cash you paid in this trade (default: 0): 
Positive for cash paid, Negative for cash received
3
```

###### 3.2.3 Moments traded in
Usually prices are just the FMV or Floor Ask. **Make sure you assign values carefully because those values affect gain/loss of future transactions**. But considering the situation of trading in moments of similar FMV in bulks (like TTs), auditor also supports assigning value equally to all traded in moments. **The recommended way is to check Discord/Twitter message history to get trade details.**

Auditor will ask which way you want to assign values.

```shell
---- Now you need to assign prices for received moments, choose from 1/2 
1: Assigned $8.0 equally
2: Assigned individually
```

If you select `2`, then it will go through moments 1-by-1 starting from the lowest serial number (as lowest serial number moments are usually rarer and have higher value).
```shell
1/2 Series 3 | Base Set | Jaren Jackson Jr. | #27112 | 11/30/2021
Provide value in range [0, 8.0]:
2
```
The provided value has to be positive and smaller than the total value ($8.00 in this example).

After assigning value to each moment, it will ask whether you want to assign the rest of value equally (default no). 
```shell
Provide value in range [0, 8.0]:
2
For the rest 1 moments, assigned $6.0 equally? (no/yes)
yes
```

Just repeat assigning until all moments have an in value.

###### 3.2.4 Moments bought on 3rd-party marketplace
**Please keep in mind that moments bought on 3rd-party marketplaces, e.g. Gaia, Flowty, are all marked at `'Received Gift'` by Livetoken so this auditor is treating them as trades. You need to provide the cash/crypto payment info for those moments. Similar for moments sold on these 3rd-party marketplaces, you need to provide the sale price as out value.**

##### 3.3 Store intermedia result
After resolving `Trade` transactions, an intermedia result file will be output: `momentWithTrades.csv`

#### 4 Compute Gain/Loss
Now the auditor is ready to compute gain/loss from all transactions. For every moment, its transaction list must be **\[in, out, in, out, ...\]**. Each pair of in and out transactions will result in a gain/loss. The 5% transaction fee will be taken out for moments `'Sold'` on Topshot marketplace.

The final result file is ordered by `in_date` and has the following format:
```shell
'moment_id', 'moment', 'in_type', 'in_counter_party', 'in_price', 'in_date', 'out_type', 'out_counter_party', 'out_price', 'out_date', 'profit', 'days_holding'
```

You can later use the `days_holding` column to determine long-term and short-term profit.
