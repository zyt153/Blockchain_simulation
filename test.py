import hashlib
import json
import time
from urllib.parse import urlparse
from uuid import uuid4
import requests
from flask import Flask, jsonify, request
from typing import Any, Dict, List, Optional  # 数据结构

'''
typing.Optional
可选类型。

Optional[X] 等价于 Union[X, None]。也就是要么是X，要么是None

请注意，这不是一个可选参数的概念，它是一个具有默认值的参数。具有默认值的可选参数不需要在其类型注释上使用 Optional 限定符（虽然如果默认值为 None，则推断）。
如果允许 None 的显式值，则强制参数可以仍然具有 Optional 类型。

typing.Any
表示无约束类型的特殊类型。

每种类型都与 Any 兼容。

Any 兼容各种类型。

'''


class DadaCoinBlockChain:
    def __init__(self):
        self.current_transactions = []  # 交易列表
        self.chain = []  # 区块链
        self.nodes = set()  # 保存网络节点
        self.new_block(proof=1234567, preHash="1234567")  # 创世区块

    ##创建区块
    def new_block(self,
                  proof: int,  # 指定参数为int
                  preHash: Optional[str]  # 指定上一块的哈希数据类型为str，默认为None
                  ) -> Dict[str, Any]:  # 指定返回数据类型
        block = {
            "index": len(self.chain) + 1,  # 索引
            "timestamp": time.time(),  # 当前时间
            "transactions": self.current_transactions,
            "proof": proof,
            "preHash": preHash or self.hash(self.chain[-1])

        }
        self.current_transactions = []
        self.chain.append(block)

        return block

    @staticmethod
    def hash(block: Dict[str, Any]) -> str:
        block_str = json.dumps(block, sort_keys=True).encode("utf-8")
        return hashlib.sha256(block_str).hexdigest()

    def new_transaction(self, sender: str, receiver: str, amount: int) -> int:  # 创建交易
        transaction = {
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
        }
        self.current_transactions.append(transaction)
        return self.last_block["index"] + 1  # 索引标记交易的数量

    @property
    def last_block(self) -> Dict[str, Any]:
        return self.chain[-1]

    def proof_of_work(self, preHash: int) -> int:  # 工作量证明
        proof = 0
        while self.valid_proof(preHash, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(preHash: str, proof: int) -> bool:  # 验证证明
        guess = f'{preHash+str(proof)}'.encode("utf-8")
        guess_hash = int(hashlib.sha256(guess).hexdigest(),16)
        #C = 0x1
        #A = 0x3e8
        #return guess_hash <= 0x000008fffffffd818d12a246c86a865f9eeb5d93d38b89fcb76022d2a2b * A * C
        #节点随机计算哈希值，如果哈希值小于下面的值则挖矿成功，阈值越小挖矿时间越长
        return guess_hash <= 0x000008fffffffd818d12a246c86a865f9eeb5d93d38b89fcb76022d2a2b

    def register_node(self, addr: str) -> None:  # 加入网络的其他节点，用于更新
        now_url = urlparse(addr)
        self.nodes.add(now_url.netloc)  # 增加网络节点
        pass

    def valid_chain(self, chain: List[Dict[str, Any]]) -> bool:  # 区块链校验
        last_block = self.chain[0]
        current_index = 1
        while current_index < len(self.chain):
            block = self.chain[current_index]
            # 哈希校验
            if block["preHash"] != self.hash(last_block):
                return False
            # 工作量校验
            if not self.valid_proof(last_block["preHash"], block["proof"]):
                return False
            last_block = block
            current_index += 1

        return True

    def resolve_conflict(self) -> bool:  # 同步区块链
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)
        for node in neighbours:
            response = requests.post(f'http://{node}/chain')
            if response.status_code == 200:
                chain = response.json()["chain"]
                length = response.json()["length"]
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
        if new_chain:
            self.chain = new_chain
            return True
        else:
            return False

#----------------------------------------------------------------
datacoin = DadaCoinBlockChain()  # 创建一个网络节点
node_id = str(uuid4()).replace("-", "")  # 生成钱包地址
print("当前节点钱包地址：", node_id)
app = Flask(__name__)  # 初始化


# 首页
@app.route("/", methods=["POST"])
def index_page():
    return "区块链节点仿真"


# 获取区块链
@app.route("/chain", methods=["POST"])
def index_chain():
    response = {
        "chain": datacoin.chain,  # 区块链
        "length": len(datacoin.chain),
    }
    return jsonify(response), 200


# 创建新的交易
@app.route("/new_transaction", methods=["POST"])
def new_transaction():
    values = request.get_json()
    print("values:", values)
    required = ["sender", "receiver", "amount"]
    if not all(key in values for key in required):
        return "数据不完整", 400
    index = datacoin.new_transaction(values["sender"], values["receiver"], values["amount"])
    response = {
        "message": f'交易加入到区块{index}',
    }

    return jsonify(response), 200


# 挖矿
@app.route("/mine", methods=["POST"])
def index_mine():
    last_block = datacoin.last_block
    preHash = last_block["preHash"]
    proof = datacoin.proof_of_work(preHash)  # 挖矿计算

    # 系统奖励，挖矿产生交易
    datacoin.new_transaction(sender="0", receiver=node_id, amount=10)
    block = datacoin.new_block(proof, None)  # 增加一个区块
    response = {
        "message": "新的区块创建",
        "index": block["index"],
        "transactions": block["transactions"],
        "proof": block["proof"],
        "preHash": block["preHash"],
    }

    return jsonify(response), 200


# 新增节点
@app.route("/new_node", methods=["POST"])
def new_node():
    values = request.get_json()
    nodes = values.get("nodes")
    if nodes is None:
        return "数据错误", 400
    for node in nodes:
        datacoin.register_node(node)
    response = {
        "message": f'网络节点已被追加',
        "nodes": list(datacoin.nodes),
    }
    return jsonify(response), 200


# 刷新节点
@app.route("/node_refresh", methods=["POST"])
def node_refresh():
    replaced = datacoin.resolve_conflict()  # 共识算法进行最长替换
    if replaced:
        response = {
            "message": "区块链已被替换为最长",  # 区块链
            "new_chain": datacoin.chain,
        }
        pass
    else:
        response = {
            "message": "当前区块链已是最长，无需替换",  # 区块链
            "new_chain": datacoin.chain,
        }

    return jsonify(response), 200

if __name__ == "__main__":
    app.run("127.0.0.1", port=5000)
