import redis
from redis import from_url
def insert_urls():
    redisClient = redis.from_url('redis://127.0.0.1:6379')

    #Push URLs to Redis Queue
    for i in range(1,10001):
        url = f"https://electoralsearch.eci.gov.in/"
        redisClient.lpush('elect:start_urls', url)
        print('+++++redis queue successfull+++++++')


if __name__ == '__main__':
    insert_urls()
