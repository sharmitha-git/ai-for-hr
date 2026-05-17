import re


class PrivacyService:


    @staticmethod
    def mask_pii(text: str):

        masked_text = text

        email_pattern = (
            r'[\w\.-]+@[\w\.-]+'
        )

        phone_pattern = (
            r'\+?\d[\d\s\-]{8,}'
        )

        emails = re.findall(
            email_pattern,
            text
        )

        phones = re.findall(
            phone_pattern,
            text
        )

        for email in emails:

            masked_text = masked_text.replace(
                email,
                "[EMAIL]"
            )

        for phone in phones:

            masked_text = masked_text.replace(
                phone,
                "[PHONE]"
            )

        return {

            "masked_text": masked_text,

            "emails": emails,

            "phones": phones
        }