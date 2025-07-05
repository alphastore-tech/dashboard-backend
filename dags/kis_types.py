"""
types.py
~~~~~~~~~~
한국투자증권 OpenAPI 관련 타입 정의
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class RequestHeader:
    content_type: str            # Content-Type
    authorization: str           # Bearer {access_token}
    appkey: str
    appsecret: str
    tr_id: str                   # 거래 ID (예: TTTC8001R)
    custtype: str                # 고객 타입 (P: 개인·B: 법인)
    personalseckey: Optional[str] = None
    tr_cont: Optional[str] = None
    seq_no: Optional[str] = None
    mac_address: Optional[str] = None
    phone_number: Optional[str] = None
    ip_addr: Optional[str] = None
    hashkey: Optional[str] = None
    gt_uid: Optional[str] = None

    # HTTP 전송용 dict (키를 API 규격에 맞춰 변환)
    def to_http_headers(self) -> dict[str, str]:
        mapping = {
            "content_type": "content-type",
            "authorization": "authorization",
            "appkey": "appkey",
            "appsecret": "appsecret",
            "personalseckey": "personalseckey",
            "tr_id": "tr_id",
            "tr_cont": "tr_cont",
            "custtype": "custtype",
            "seq_no": "seq_no",
            "mac_address": "mac_address",
            "phone_number": "phone_number",
            "ip_addr": "ip_addr",
            "hashkey": "hashkey",
            "gt_uid": "gt_uid",
        }
        return {api_k: getattr(self, py_k)
                for py_k, api_k in mapping.items()
                if getattr(self, py_k) is not None} 