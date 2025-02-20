from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

def test_mongodb_connection(uri):
    """
    测试 MongoDB 连接
    :param uri: MongoDB 的连接 URI (例如 mongodb://localhost:27017/)
    """
    try:
        # 创建 MongoDB 客户端
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)  # 设置超时时间为 5 秒
        # 尝试连接到服务器
        client.admin.command('ping')
        print("成功连接到 MongoDB！")
    except ConnectionFailure as e:
        print(f"无法连接到 MongoDB: {e}")
    finally:
        # 关闭客户端
        client.close()

# 示例调用
if __name__ == "__main__":
    # 替换为你的 MongoDB URI
    mongodb_uri = "mongodb://localhost:27017/"
    test_mongodb_connection(mongodb_uri)
