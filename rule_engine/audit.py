"""Audit Trail Module for Rule Engine (Tieu chi A-06).

Ghi nhan nhat ky kiem toan voi toi thieu 4 truong bat buoc:
[Timestamp, User_UUID, Action_Type, Status]
Tuyet doi khong chua du lieu lam sang tho (tuan thu Zero PII).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID


class AuditRecord:
    """Ban ghi nhat ky kiem toan chuan 4 truong bat buoc."""

    def __init__(
        self,
        timestamp: str,
        user_uuid: str,
        action_type: str,
        status: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.timestamp = timestamp
        self.user_uuid = user_uuid
        self.action_type = action_type
        self.status = status
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Xuat ra dictionary hop le."""
        res: Dict[str, Any] = {
            "timestamp": self.timestamp,
            "user_uuid": self.user_uuid,
            "action_type": self.action_type,
            "status": self.status,
        }
        if self.metadata:
            res["metadata"] = self.metadata
        return res


class AuditLogger:
    """In-memory Audit Trail Logger cho Rule Engine."""

    # Danh sach cac tu khoa lam sang tho bi cam tuyet doi trong audit log
    PROHIBITED_RAW_CLINICAL_FIELDS = {
        "huyet_ap_tam_thu",
        "huyet_ap_tam_thu_nen",
        "tuoi",
        "co_di_nguyen_nghi_ngo",
        "di_nguyen_qua_duong_hit",
        "co_ton_thuong_da_niem_mac",
        "co_trieu_chung_ho_hap",
        "co_trieu_chung_tuan_hoan",
        "co_trieu_chung_tieu_hoa_nang",
    }

    def __init__(self) -> None:
        self._records: List[AuditRecord] = []

    def log(
        self,
        user_uuid: str,
        action_type: str = "EVALUATE_RULE",
        status: str = "SUCCESS",
        rule_id: Optional[str] = None,
        muc_do: Optional[str] = None,
    ) -> AuditRecord:
        """Ghi nhan su kien audit voi 4 truong bat buoc va metadata khong chua PII."""
        # Kiem tra tinh hop le cua User_UUID neu duoc truyen vao
        self._validate_uuid(user_uuid)

        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Metadata chi luu nhan ket qua cap cao, khong chua thong so sinh ly tho
        meta: Dict[str, Any] = {}
        if rule_id is not None:
            meta["rule_id"] = str(rule_id)
        if muc_do is not None:
            meta["muc_do"] = str(muc_do)

        record = AuditRecord(
            timestamp=now_iso,
            user_uuid=str(user_uuid),
            action_type=str(action_type),
            status=str(status),
            metadata=meta,
        )
        self._records.append(record)
        return record

    @staticmethod
    def _validate_uuid(val: str) -> None:
        """Kiem tra user_uuid phai la chuoi hop le."""
        if not val or not isinstance(val, str):
            raise ValueError("user_uuid phai la chuoi hop le khong rong")

    @property
    def records(self) -> List[AuditRecord]:
        return list(self._records)

    def clear(self) -> None:
        self._records.clear()

    def has_raw_clinical_data(self) -> bool:
        """Kiem tra xem co vo tinh lot thong tin lam sang tho vao audit hay khong."""
        for r in self._records:
            d = r.to_dict()
            for key in self.PROHIBITED_RAW_CLINICAL_FIELDS:
                if key in d:
                    return True
                if "metadata" in d and key in d["metadata"]:
                    return True
        return False
