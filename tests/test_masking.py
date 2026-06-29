import pytest
from unittest.mock import patch, AsyncMock
from app.services.masking import PrivacyMaskingService


@pytest.fixture
def masking_service():
    """
    Creates the masking service but mocks the TokenVaultService.
    This stops the unit tests from trying to connect to a live Redis instance.
    """
    with patch("app.services.masking.TokenVaultService") as MockVault:
        # Intercept the store_mapping method and force it to be an AsyncMock
        mock_vault_instance = MockVault.return_value
        mock_vault_instance.store_mapping = AsyncMock()

        # Yield the service with the injected mock
        yield PrivacyMaskingService()


@pytest.mark.asyncio
async def test_mask_text_with_no_pii(masking_service):
    """Ensure text with no PII remains completely unchanged."""
    text = "The sky is blue and the weather is pleasant."

    # We must now AWAIT the result
    result = await masking_service.mask_text(text)

    assert result["anonymized_text"] == text
    assert result["entities_masked_count"] == 0


@pytest.mark.asyncio
async def test_mask_za_id_number(masking_service):
    text = "My ID number is 9201015009087."
    result = await masking_service.mask_text(text)

    # assert using 'in' to account for UUIDs
    assert "<ZA_ID_NUMBER_" in result["anonymized_text"]
    assert "9201015009087" not in result["anonymized_text"]
    assert result["entities_masked_count"] == 1


@pytest.mark.asyncio
async def test_mask_za_phone_number(masking_service):
    formats = [
        "Call me at +27825551234",
        "Reach out on 082 555 1234",
        "Office line is 27117891234",
    ]

    for text in formats:
        result = await masking_service.mask_text(text)
        assert "<ZA_PHONE_NUMBER_" in result["anonymized_text"]
        assert result["entities_masked_count"] == 1


@pytest.mark.asyncio
async def test_mask_za_passport(masking_service):
    text = "Passport number: A12345678"
    result = await masking_service.mask_text(text)

    assert "<ZA_PASSPORT_NUM_" in result["anonymized_text"]
    assert result["entities_masked_count"] == 1


@pytest.mark.asyncio
async def test_mask_za_tax_number(masking_service):
    text = "SARS Tax Ref: 1234567890"
    result = await masking_service.mask_text(text)

    assert "<ZA_TAX_NUMBER_" in result["anonymized_text"]
    assert result["entities_masked_count"] == 1
