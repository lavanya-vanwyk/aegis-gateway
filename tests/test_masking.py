import pytest
from app.services.masking import PrivacyMaskingService

@pytest.fixture(scope="module")
def masking_service():
    return PrivacyMaskingService()


def test_mask_text_with_no_pii(masking_service):
    """Ensure text with no PII remains completely unchanged."""
    text = "The sky is blue and the weather is pleasant."
    result = masking_service.mask_text(text)
    
    assert result["anonymized_text"] == text
    assert result["entities_masked_count"] == 0


def test_mask_za_id_number(masking_service):
    text = "My ID number is 0006190071089."
    result = masking_service.mask_text(text)
    
    assert "<ZA_ID_NUMBER>" in result["anonymized_text"]
    assert "0006190071089" not in result["anonymized_text"]
    assert result["entities_masked_count"] == 1


def test_mask_za_phone_number(masking_service):
    formats = [
        "Call me at +27825551234",
        "Reach out on 082 555 1234",
        "Office line is 27117891234"
    ]
    
    for text in formats:
        result = masking_service.mask_text(text)
        assert "<ZA_PHONE_NUMBER>" in result["anonymized_text"]
        assert result["entities_masked_count"] == 1


def test_mask_za_passport(masking_service):
    text = "Passport number: A12345678"
    result = masking_service.mask_text(text)
    
    assert "<ZA_PASSPORT>" in result["anonymized_text"]
    assert result["entities_masked_count"] == 1


def test_mask_za_tax_number(masking_service):
    text = "SARS Tax Ref: 1234567890"
    result = masking_service.mask_text(text)
    
    assert "<ZA_TAX_NUMBER>" in result["anonymized_text"]
    assert result["entities_masked_count"] == 1

