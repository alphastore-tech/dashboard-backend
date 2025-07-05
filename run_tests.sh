#!/bin/bash

# 테스트 실행 스크립트

echo "=== Fetch 함수들 테스트 실행 ==="

# 테스트 의존성 설치
echo "1. 테스트 의존성 설치 중..."
pip install -r requirements-test.txt

# 테스트 실행
echo "2. 테스트 실행 중..."
python -m pytest tests/ -v --tb=short

# 커버리지 리포트 생성 (선택사항)
echo "3. 커버리지 리포트 생성 중..."
python -m pytest tests/ --cov=dags --cov-report=html --cov-report=term

echo "=== 테스트 완료 ===" 