"""Kiem thu module Audit Trail (Tieu chi A-06).

Yeu cau:
- Ghi nhat ky kiem toan voi toi thieu 4 truong [Timestamp, User_UUID, Action_Type, Status].
- Khong chua du lieu lam sang tho (Zero PII).
"""
import uuid
import pytest
from rule_engine.audit import AuditLogger, AuditRecord
from rule_engine.classifier import classify_with_audit


def test_audit_record_four_mandatory_fields():
    """Kiem tra ban ghi co day du 4 truong bat buoc."""
    logger = AuditLogger()
    test_uuid = str(uuid.uuid4())
    record = logger.log(
        user_uuid=test_uuid,
        action_type="EVALUATE_RULE",
        status="SUCCESS",
        rule_id="R01-PV",
        muc_do="PHAN_VE",
    )

    data = record.to_dict()
    assert "timestamp" in data
    assert "user_uuid" in data
    assert "action_type" in data
    assert "status" in data

    assert data["user_uuid"] == test_uuid
    assert data["action_type"] == "EVALUATE_RULE"
    assert data["status"] == "SUCCESS"
    assert data["timestamp"].endswith("Z")  # Format ISO-8601 UTC


def test_audit_zero_raw_clinical_data():
    """Kiem tra audit record hoan toan khong chua du lieu lam sang tho."""
    logger = AuditLogger()
    test_uuid = str(uuid.uuid4())
    logger.log(
        user_uuid=test_uuid,
        action_type="EVALUATE_RULE",
        status="SUCCESS",
        rule_id="R-SOC",
        muc_do="SOC_PHAN_VE",
    )

    assert not logger.has_raw_clinical_data()
    data = logger.records[0].to_dict()

    prohibited_keys = [
        "tuoi",
        "huyet_ap_tam_thu",
        "huyet_ap_tam_thu_nen",
        "co_di_nguyen_nghi_ngo",
        "co_ton_thuong_da_niem_mac",
    ]
    for key in prohibited_keys:
        assert key not in data
        if "metadata" in data:
            assert key not in data["metadata"]


def test_classify_with_audit_integration():
    """Kiem tra ham classify_with_audit tich hop ca phan loai va ghi nhat ky."""
    logger = AuditLogger()
    test_uuid = str(uuid.uuid4())

    patient = {
        "co_di_nguyen_nghi_ngo": False,
        "co_ton_thuong_da_niem_mac": True,
        "co_trieu_chung_ho_hap": True,
        "tuoi": 25.0,
        "huyet_ap_tam_thu": 120,
    }

    res, rec = classify_with_audit(patient, user_uuid=test_uuid, logger=logger)

    assert res["muc_do"] == "PHAN_VE"
    assert res["rule_id"] == "R01-PV"

    assert len(logger.records) == 1
    assert rec.user_uuid == test_uuid
    assert rec.action_type == "EVALUATE_RULE"
    assert rec.status == "SUCCESS"
    assert rec.metadata["rule_id"] == "R01-PV"
    assert rec.metadata["muc_do"] == "PHAN_VE"


def test_audit_invalid_uuid():
    """Kiem tra validation user_uuid."""
    logger = AuditLogger()
    with pytest.raises(ValueError):
        logger.log(user_uuid="")
