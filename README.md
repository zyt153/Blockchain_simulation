# Blockchain_simulation

## Blockchain simulation supported by python and postman. 

Select **post** operation in **postman**.

Request directly: http://127.0.0.1:5000

View the complete blockchain: http://127.0.0.1:5000/chain

Start mining: http://127.0.0.1:5000/mine

Add new transaction: http://127.0.0.1:5000/new_transaction

**Post** json request here (select json in body - raw):
```
{
    "sender": "Alice",
    "receiver": "Bob",
    "amount": 2
 }
```
The newly added transactions will not be recorded in the blockchain until the mining is successful, that is, to compete for the right to keep accounts.


## 基于python和postman的区块链节点仿真

在**postman**中选择**post**操作。

直接请求：http://127.0.0.1:5000

查看完整区块链：http://127.0.0.1:5000/chain

开始挖矿：http://127.0.0.1:5000/mine

增加一次新的交易：http://127.0.0.1:5000/new_transaction

在其中**post** json请求（body - raw中选择json）：
```
{
    "sender": "Alice",
    "receiver": "Bob",
    "amount": 2
 }
```

新增加的交易在挖矿成功后才会记录到区块链中，即争抢记账权。
