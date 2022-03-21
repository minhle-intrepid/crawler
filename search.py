from main import *
es = Elasticsearch("http://localhost:9200/")
resp = es.search(index="lazada", query={"match_all": {}})
print(resp)
