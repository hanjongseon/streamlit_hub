from rapidfuzz import process

# 검색어와 후보 리스트
query = "appl"
candidates = ["apple pie", "application", "banana split", "apricot jam"]

# 검색어와 가장 유사한 항목 찾기
matches = process.extract(query, candidates, limit=3)
print(matches)  # [(매칭 텍스트, 유사도 점수, 인덱스)]
