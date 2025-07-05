"""
fetch 관련 함수들의 테스트 코드
"""
import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# dags 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'dags'))

from fetch_stock_account_balance import fetch_stock_account_balance
from fetch_future_account_balance import fetch_futures_account_assets
from fetch_realized_pnl import fetch_realized_pnl
from fetch_nav import fetch_daily_nav


class TestFetchStockAccountBalance:
    """주식 계좌 자산 현황 조회 함수 테스트"""
    
    @pytest.fixture
    def mock_response(self):
        """성공적인 API 응답 모킹"""
        mock_resp = Mock()
        mock_resp.json.return_value = {
            "rt_cd": "0",
            "msg_cd": "MCA00000",
            "msg1": "정상처리 되었습니다.",
            "output1": [{
                "nass_amt_tot": "1000000.00",      # 총자산
                "evlu_pfls_amt": "50000.00",       # 평가손익
                "dnca_tot_amt": "200000.00"        # 예수금
            }]
        }
        mock_resp.raise_for_status.return_value = None
        return mock_resp
    
    @pytest.fixture
    def api_params(self):
        """API 호출 파라미터"""
        return {
            "appkey": "test_app_key",
            "appsecret": "test_app_secret", 
            "access_token": "test_access_token",
            "cano": "12345678",
            "acnt_prdt_cd": "01"
        }
    
    @patch('fetch_stock_account_balance.requests.get')
    def test_fetch_stock_account_balance_success(self, mock_get, mock_response, api_params):
        """정상적인 주식 계좌 자산 조회 테스트"""
        mock_get.return_value = mock_response
        
        result = fetch_stock_account_balance(**api_params)
        
        # 결과 검증
        assert isinstance(result, dict)
        assert "ending_equity" in result
        assert "unrealized_pnl" in result
        assert "cash_balance" in result
        assert result["ending_equity"] == 1000000.0
        assert result["unrealized_pnl"] == 50000.0
        assert result["cash_balance"] == 200000.0
        
        # API 호출 검증
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "headers" in call_args[1]
        assert "params" in call_args[1]
    
    @patch('fetch_stock_account_balance.requests.get')
    def test_fetch_stock_account_balance_api_error(self, mock_get, api_params):
        """API 에러 응답 테스트"""
        mock_resp = Mock()
        mock_resp.json.return_value = {
            "rt_cd": "1",
            "msg_cd": "ERROR001",
            "msg1": "API 에러 발생"
        }
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp
        
        with pytest.raises(RuntimeError, match="KIS API error"):
            fetch_stock_account_balance(**api_params)
    
    @patch('fetch_stock_account_balance.requests.get')
    def test_fetch_stock_account_balance_http_error(self, mock_get, api_params):
        """HTTP 에러 테스트"""
        mock_get.side_effect = Exception("HTTP 에러")
        
        with pytest.raises(Exception):
            fetch_stock_account_balance(**api_params)


class TestFetchFuturesAccountAssets:
    """선물/옵션 계좌 자산 현황 조회 함수 테스트"""
    
    @pytest.fixture
    def mock_response(self):
        """성공적인 API 응답 모킹"""
        mock_resp = Mock()
        mock_resp.json.return_value = {
            "rt_cd": "0",
            "msg_cd": "MCA00000", 
            "msg1": "정상처리 되었습니다.",
            "output1": [{
                "tot_ass_amt": "2000000.00",       # 총자산
                "evlu_pfls_amt": "100000.00",      # 평가손익
                "dnca_tot_amt": "300000.00"        # 예수금
            }]
        }
        mock_resp.raise_for_status.return_value = None
        return mock_resp
    
    @pytest.fixture
    def api_params(self):
        """API 호출 파라미터"""
        return {
            "appkey": "test_app_key",
            "appsecret": "test_app_secret",
            "access_token": "test_access_token", 
            "cano": "87654321",
            "acnt_prdt_cd": "02"
        }
    
    @patch('fetch_future_account_balance.requests.get')
    def test_fetch_futures_account_assets_success(self, mock_get, mock_response, api_params):
        """정상적인 선물 계좌 자산 조회 테스트"""
        mock_get.return_value = mock_response
        
        result = fetch_futures_account_assets(**api_params)
        
        # 결과 검증
        assert isinstance(result, dict)
        assert "ending_equity" in result
        assert "unrealized_pnl" in result
        assert "cash_balance" in result
        assert result["ending_equity"] == 2000000.0
        assert result["unrealized_pnl"] == 100000.0
        assert result["cash_balance"] == 300000.0
        
        # API 호출 검증
        mock_get.assert_called_once()
    
    @patch('fetch_future_account_balance.requests.get')
    def test_fetch_futures_account_assets_api_error(self, mock_get, api_params):
        """API 에러 응답 테스트"""
        mock_resp = Mock()
        mock_resp.json.return_value = {
            "rt_cd": "1",
            "msg_cd": "ERROR002",
            "msg1": "선물 API 에러"
        }
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp
        
        with pytest.raises(RuntimeError, match="KIS API error"):
            fetch_futures_account_assets(**api_params)


class TestFetchRealizedPnl:
    """실현손익 조회 함수 테스트"""
    
    @pytest.fixture
    def mock_response(self):
        """성공적인 API 응답 모킹"""
        mock_resp = Mock()
        mock_resp.json.return_value = {
            "rt_cd": "0",
            "msg_cd": "MCA00000",
            "msg1": "정상처리 되었습니다.",
            "output1": [
                {
                    "trad_dt": "20250101",
                    "buy_amt": "100000.00",
                    "sll_amt": "110000.00", 
                    "rlzt_pfls": "10000.00",
                    "fee": "100.00",
                    "loan_int": "0.00",
                    "tl_tax": "50.00",
                    "pfls_rt": "10.00",
                    "sll_qty1": "10",
                    "buy_qty1": "10"
                },
                {
                    "trad_dt": "20250102",
                    "buy_amt": "200000.00",
                    "sll_amt": "220000.00",
                    "rlzt_pfls": "20000.00", 
                    "fee": "200.00",
                    "loan_int": "0.00",
                    "tl_tax": "100.00",
                    "pfls_rt": "10.00",
                    "sll_qty1": "20",
                    "buy_qty1": "20"
                }
            ],
            "output2": {
                "sll_qty_smtl": "30",
                "sll_tr_amt_smtl": "330000.00",
                "tot_rlzt_pfls": "30000.00"
            }
        }
        mock_resp.raise_for_status.return_value = None
        return mock_resp
    
    @pytest.fixture
    def api_params(self):
        """API 호출 파라미터"""
        return {
            "appkey": "test_app_key",
            "appsecret": "test_app_secret",
            "access_token": "test_access_token",
            "cano": "12345678",
            "acnt_prdt_cd": "01",
            "start_dt": "20250101",
            "end_dt": "20250102"
        }
    
    @patch('fetch_realized_pnl.requests.get')
    def test_fetch_realized_pnl_success(self, mock_get, mock_response, api_params):
        """정상적인 실현손익 조회 테스트"""
        mock_get.return_value = mock_response
        
        result = fetch_realized_pnl(**api_params)
        
        # 결과 검증
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "trad_dt" in result.columns
        assert "buy_amt" in result.columns
        assert "sll_amt" in result.columns
        assert "rlzt_pfls" in result.columns
        
        # 데이터 타입 검증 (numeric으로 변환되었는지)
        assert pd.api.types.is_numeric_dtype(result["buy_amt"])
        assert pd.api.types.is_numeric_dtype(result["sll_amt"])
        assert pd.api.types.is_numeric_dtype(result["rlzt_pfls"])
        
        # API 호출 검증
        mock_get.assert_called_once()
    
    @patch('fetch_realized_pnl.requests.get')
    def test_fetch_realized_pnl_api_error(self, mock_get, api_params):
        """API 에러 응답 테스트"""
        mock_resp = Mock()
        mock_resp.json.return_value = {
            "rt_cd": "1",
            "msg_cd": "ERROR003",
            "msg1": "실현손익 API 에러"
        }
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp
        
        with pytest.raises(RuntimeError, match="KIS API error"):
            fetch_realized_pnl(**api_params)
    
    @patch('fetch_realized_pnl.requests.get')
    def test_fetch_realized_pnl_empty_data(self, mock_get, api_params):
        """빈 데이터 응답 테스트"""
        mock_resp = Mock()
        mock_resp.json.return_value = {
            "rt_cd": "0",
            "msg_cd": "MCA00000",
            "msg1": "정상처리 되었습니다.",
            "output1": [],
            "output2": None
        }
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp
        
        result = fetch_realized_pnl(**api_params)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


class TestFetchDailyNav:
    """일별 NAV 조회 함수 테스트"""
    
    @pytest.fixture
    def spot_kwargs(self):
        """주식 계좌 파라미터"""
        return {
            "appkey": "test_app_key",
            "appsecret": "test_app_secret",
            "access_token": "test_access_token",
            "cano": "12345678",
            "acnt_prdt_cd": "01"
        }
    
    @pytest.fixture
    def futures_kwargs(self):
        """선물 계좌 파라미터"""
        return {
            "appkey": "test_app_key", 
            "appsecret": "test_app_secret",
            "access_token": "test_access_token",
            "cano": "87654321",
            "acnt_prdt_cd": "02"
        }
    
    @patch('fetch_nav.fetch_futures_account_assets')
    @patch('fetch_nav.fetch_stock_account_balance')
    def test_fetch_daily_nav_success(self, mock_fetch_stock, mock_fetch_futures, 
                                   spot_kwargs, futures_kwargs):
        """정상적인 일별 NAV 조회 테스트"""
        # 모킹된 반환값 설정
        mock_fetch_stock.return_value = {
            "ending_equity": 1000000.0,
            "unrealized_pnl": 50000.0,
            "cash_balance": 200000.0
        }
        
        mock_fetch_futures.return_value = {
            "ending_equity": 2000000.0,
            "unrealized_pnl": 100000.0,
            "cash_balance": 300000.0
        }
        
        result = fetch_daily_nav(spot_kwargs, futures_kwargs)
        
        # 결과 검증
        assert isinstance(result, dict)
        assert "spot_nav" in result
        assert "futures_nav" in result
        assert "total_nav" in result
        assert "spot_unrealized" in result
        assert "futures_unrealized" in result
        
        assert result["spot_nav"] == 1000000.0
        assert result["futures_nav"] == 2000000.0
        assert result["total_nav"] == 3000000.0
        assert result["spot_unrealized"] == 50000.0
        assert result["futures_unrealized"] == 100000.0
        
        # 함수 호출 검증
        mock_fetch_stock.assert_called_once_with(**spot_kwargs)
        mock_fetch_futures.assert_called_once_with(**futures_kwargs)
    
    @patch('fetch_nav.fetch_futures_account_assets')
    @patch('fetch_nav.fetch_stock_account_balance')
    def test_fetch_daily_nav_stock_error(self, mock_fetch_stock, mock_fetch_futures,
                                       spot_kwargs, futures_kwargs):
        """주식 계좌 조회 에러 테스트"""
        mock_fetch_stock.side_effect = RuntimeError("주식 API 에러")
        
        with pytest.raises(RuntimeError, match="주식 API 에러"):
            fetch_daily_nav(spot_kwargs, futures_kwargs)
        
        # 선물 함수는 호출되지 않아야 함
        mock_fetch_futures.assert_not_called()
    
    @patch('fetch_nav.fetch_futures_account_assets')
    @patch('fetch_nav.fetch_stock_account_balance')
    def test_fetch_daily_nav_futures_error(self, mock_fetch_stock, mock_fetch_futures,
                                         spot_kwargs, futures_kwargs):
        """선물 계좌 조회 에러 테스트"""
        mock_fetch_stock.return_value = {
            "ending_equity": 1000000.0,
            "unrealized_pnl": 50000.0,
            "cash_balance": 200000.0
        }
        mock_fetch_futures.side_effect = RuntimeError("선물 API 에러")
        
        with pytest.raises(RuntimeError, match="선물 API 에러"):
            fetch_daily_nav(spot_kwargs, futures_kwargs)
        
        # 주식 함수는 호출되어야 함
        mock_fetch_stock.assert_called_once_with(**spot_kwargs)


class TestIntegration:
    """통합 테스트"""
    
    @pytest.fixture
    def sample_data(self):
        """샘플 데이터"""
        return {
            "stock_data": {
                "ending_equity": 1000000.0,
                "unrealized_pnl": 50000.0,
                "cash_balance": 200000.0
            },
            "futures_data": {
                "ending_equity": 2000000.0,
                "unrealized_pnl": 100000.0,
                "cash_balance": 300000.0
            },
            "realized_pnl_data": pd.DataFrame({
                "trad_dt": ["20250101", "20250102"],
                "buy_amt": [100000.0, 200000.0],
                "sll_amt": [110000.0, 220000.0],
                "rlzt_pfls": [10000.0, 20000.0]
            })
        }
    
    def test_data_consistency(self, sample_data):
        """데이터 일관성 테스트"""
        stock = sample_data["stock_data"]
        futures = sample_data["futures_data"]
        
        # NAV 계산 검증
        total_nav = stock["ending_equity"] + futures["ending_equity"]
        assert total_nav == 3000000.0
        
        # 현금 잔고 검증
        total_cash = stock["cash_balance"] + futures["cash_balance"]
        assert total_cash == 500000.0
        
        # 평가손익 검증
        total_unrealized = stock["unrealized_pnl"] + futures["unrealized_pnl"]
        assert total_unrealized == 150000.0
    
    def test_realized_pnl_data_validation(self, sample_data):
        """실현손익 데이터 검증 테스트"""
        df = sample_data["realized_pnl_data"]
        
        # 필수 컬럼 존재 확인
        required_columns = ["trad_dt", "buy_amt", "sll_amt", "rlzt_pfls"]
        for col in required_columns:
            assert col in df.columns
        
        # 데이터 타입 검증
        assert pd.api.types.is_numeric_dtype(df["buy_amt"])
        assert pd.api.types.is_numeric_dtype(df["sll_amt"])
        assert pd.api.types.is_numeric_dtype(df["rlzt_pfls"])
        
        # 손익 계산 검증
        for _, row in df.iterrows():
            expected_pnl = row["sll_amt"] - row["buy_amt"]
            assert abs(row["rlzt_pfls"] - expected_pnl) < 0.01  # 부동소수점 오차 허용


if __name__ == "__main__":
    pytest.main([__file__]) 